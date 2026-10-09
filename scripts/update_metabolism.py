#!/usr/bin/env python3
"""自适应代谢与热量监控引擎 (Adaptive TDEE & Nutrition Engine)

读取 user-data/nutrition.json 与 CURRENT-STATE.json：
1. 计算平滑均线体重（过滤水分与水肿噪声）
2. 基于能量守恒反推真实动态 TDEE
3. 动态更新目标热量与减脂状态建议

用法：
    python scripts/update_metabolism.py
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, atomic_write

ROOT = Path(__file__).resolve().parent.parent
USER_DATA = ROOT / "user-data"
CN_TZ = timezone(timedelta(hours=8))

# 默认基础生物参数（若 PROFILE.md 未填写则作保底兜底）
FALLBACK_AGE = 25
FALLBACK_HEIGHT_CM = 175.0
DEFAULT_ACTIVITY_MULT = 1.35  # 中低强度活动度系数
CALORIES_PER_KG_FAT = 7700.0  # 1kg 纯脂肪组织理论热量差
TARGET_DEFICIT = 450          # 推荐的健康日热量缺口（约每周减 0.4kg 纯脂）


def get_profile_bio():
    """从 PROFILE.md 中动态解析年龄与身高，避免硬编码"""
    age, height = FALLBACK_AGE, FALLBACK_HEIGHT_CM
    profile_file = USER_DATA / "PROFILE.md"
    if profile_file.exists():
        try:
            import re
            text = profile_file.read_text(encoding="utf-8")
            m_age = re.search(r'(\d+)\s*岁', text)
            if m_age:
                age = int(m_age.group(1))
            m_h = re.search(r'(\d+(?:\.\d+)?)\s*cm', text)
            if m_h:
                height = float(m_h.group(1))
        except Exception:
            pass
    return age, height


def calculate_bmr(weight_kg, height_cm, age):
    """Mifflin-St Jeor 公式计算理论基础代谢"""
    return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + 5.0



def compute_ema(series, alpha=0.25):
    """指数移动平均 (EMA)，有效平滑单日水分暴增/骤降噪声"""
    if not series:
        return []
    ema = [series[0]]
    for x in series[1:]:
        ema.append(round(alpha * x + (1.0 - alpha) * ema[-1], 2))
    return ema


def main():
    state_file = USER_DATA / "CURRENT-STATE.json"
    nutrition_file = USER_DATA / "nutrition.json"

    if not state_file.exists():
        print(f"❌ {state_file} 不存在。")
        return 1

    state = load_json(state_file)
    nutrition = load_json(nutrition_file) if nutrition_file.exists() else {}

    # 按日期升序排序记录
    sorted_dates = sorted(nutrition.keys())
    valid_entries = []
    for d in sorted_dates:
        item = nutrition[d]
        w = item.get("weight_kg")
        c = item.get("calories_in")
        p = item.get("protein_g")
        if w is not None or c is not None:
            valid_entries.append({"date": d, "weight": w, "calories": c, "protein": p})

    # 获取用户生物参数与最新体重
    user_age, user_height = get_profile_bio()
    weights = [e["weight"] for e in valid_entries if e["weight"] is not None]
    latest_weight = weights[-1] if weights else 70.0

    # 计算体重趋势均线
    if weights:
        trend_weights = compute_ema(weights, alpha=0.25)
        trend_weight = trend_weights[-1]
    else:
        trend_weight = latest_weight

    # 理论冷启动 TDEE
    bmr_baseline = calculate_bmr(trend_weight, user_height, user_age)
    baseline_tdee = round(bmr_baseline * DEFAULT_ACTIVITY_MULT)


    # 动态 TDEE 算法（反向守恒推导）
    # 当有连续记录且时间跨度 >= 7 天时启动真实逆推
    dynamic_tdee = baseline_tdee
    data_days_count = len(valid_entries)
    confidence = "冷启动基线"

    if data_days_count >= 7:
        # 取最近 14 天（或全部）计算热量均值与均线体重差
        window = valid_entries[-14:]
        cals_in_window = [e["calories"] for e in window if e["calories"] is not None]
        
        # 窗口期起点与终点的平滑体重差
        window_weights = [e["weight"] for e in window if e["weight"] is not None]
        if len(window_weights) >= 5 and cals_in_window:
            avg_cal = sum(cals_in_window) / len(cals_in_window)
            w_emas = compute_ema(window_weights, alpha=0.25)
            delta_w = w_emas[-1] - w_emas[0]
            days_span = max(1, len(window) - 1)

            # 逆推日均消耗：TDEE = avg_cal - (delta_w * 7700 / days_span)
            inferred_tdee = avg_cal - (delta_w * CALORIES_PER_KG_FAT / days_span)

            # 约束保护：TDEE 不应低于 BMR * 1.05，也不应超过 3500
            inferred_tdee = max(bmr_baseline * 1.05, min(3500.0, inferred_tdee))

            # 权重融合：天数越多，对真实逆推的信任度越高
            weight_ratio = min(1.0, data_days_count / 14.0)
            dynamic_tdee = round((1.0 - weight_ratio) * baseline_tdee + weight_ratio * inferred_tdee)
            confidence = "7天动态融合" if data_days_count < 14 else "14天自适应校准"

    # 计算建议摄入与状态
    recommended_calories = max(1500, dynamic_tdee - TARGET_DEFICIT)

    # 减重速率评估
    if len(weights) >= 7:
        recent_delta_w = trend_weights[-1] - trend_weights[-7]
        weekly_loss_rate = abs(recent_delta_w) / trend_weight * 100.0
        if recent_delta_w > 0.3:
            metabolic_status = "体重微升（储水/充碳，继续观察）"
        elif weekly_loss_rate > 1.2:
            metabolic_status = "⚠️ 掉重过快，谨防肌肉分解，建议微调碳水"
        elif weekly_loss_rate < 0.2 and data_days_count >= 14:
            metabolic_status = "⚠️ 代谢可能产生适应，建议安排充碳日(Refeed)"
        else:
            metabolic_status = "🔥 处于高效燃脂区间 (0.5%~1%/周)"
    else:
        weekly_loss_rate = 0.5
        metabolic_status = "冷启动筑基期，以稳步唤醒为主"

    # 组装状态对象
    metabolism_state = {
        "latest_weight_kg": latest_weight,
        "trend_weight_kg": trend_weight,
        "bmr_baseline": round(bmr_baseline),
        "dynamic_tdee": dynamic_tdee,
        "tdee_confidence": confidence,
        "target_deficit": TARGET_DEFICIT,
        "recommended_calories": recommended_calories,
        "recommended_protein_g": round(trend_weight * 2.0),  # 减脂期建议 2.0g/kg 保护肌肉
        "weekly_loss_rate_pct": round(weekly_loss_rate, 2),
        "metabolic_status": metabolic_status,
        "total_logged_days": data_days_count
    }

    state["metabolism"] = metabolism_state
    state["updated_at"] = datetime.now(CN_TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")

    atomic_write(state_file, state)

    print(f"✅ 代谢快照已更新至 {state_file.name}")
    print(f"   当前体重: {latest_weight} kg (均线: {trend_weight} kg) | BMR: {round(bmr_baseline)} kcal")
    print(f"   动态 TDEE: {dynamic_tdee} kcal ({confidence}) | 建议摄入: {recommended_calories} kcal (缺口 -{TARGET_DEFICIT})")
    print(f"   状态评估: {metabolic_status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
