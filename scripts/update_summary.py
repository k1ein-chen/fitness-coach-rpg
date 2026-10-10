#!/usr/bin/env python3
"""训练后更新 CURRENT-STATE.json（重算 bests/exp/recovery/STR/CON）。

用法：
    python scripts/update_summary.py

END/AGI/INT 不由脚本计算（输入数据缺失），留空由 AI 评估填入。
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, atomic_write

ROOT = Path(__file__).resolve().parent.parent
USER_DATA = ROOT / "user-data"
CN_TZ = timezone(timedelta(hours=8))

# EXP 规则（references/rpg-rules.md v2：奖励健康行为，不奖励硬撑）
EXP_PER_SET = 5
EXP_PER_PR = 10  # PR 只是里程碑，不鼓励为大重量硬撑
EXP_PER_CARDIO = 15
EXP_PER_HONEST_PAIN = 5  # 诚实记录疼痛
EXP_PER_REASONABLE_DELOAD = 5  # 合理降重
EXP_LONG_TERM_CONSISTENCY = 20  # 近30天≥8次
STREAK_BONUS = {2: 1.2, 3: 1.5, 5: 2.0}

# 等级阈值（rpg-rules.md）
LEVEL_THRESHOLDS = {1: 0, 2: 200, 3: 600, 4: 1500, 5: 3500, 6: 7000, 7: 15000}


def load_all_sessions():
    d = USER_DATA / "sessions"
    if not d.exists():
        return []
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            out.append(load_json(f))
        except Exception as e:
            print(f"⚠️ 跳过 {f.name}: {e}")
    return out


def compute_bests(sessions):
    bests = {}
    for s in sessions:
        date = s.get("date", "")
        for ex in s.get("exercises", []):
            name = ex.get("exercise", "")
            for st in ex.get("sets", []):
                w = st.get("weight_kg", 0) or 0
                r = st.get("reps", 0) or 0
                if name not in bests or w > bests[name]["weight_kg"]:
                    bests[name] = {"weight_kg": w, "reps": r, "date": date}
    return bests


def compute_streak(sessions):
    dates = sorted({s.get("date") for s in sessions if s.get("date")})
    if not dates:
        return 0
    last = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    streak = 1
    for i in range(len(dates) - 2, -1, -1):
        prev = datetime.strptime(dates[i], "%Y-%m-%d").date()
        if (last - prev).days == 1:
            streak += 1
            last = prev
        else:
            break
    return streak


def compute_exp(sessions):
    """按时间顺序算累计 EXP。奖励健康行为（诚实记录/合理降重/规律/一致），PR 只是里程碑。"""
    from datetime import datetime, timedelta
    sorted_s = sorted(sessions, key=lambda s: s.get("date", ""))
    running = {}  # 动作 → 历史最大重量
    total = 0
    last_session_exp = 0
    for s in sorted_s:
        se = 0
        session_max = {}
        has_honest_pain = False
        for ex in s.get("exercises", []):
            name = ex.get("exercise", "")
            # 诚实记录疼痛
            p = ex.get("pain", {})
            if p.get("severity", 0) > 0:
                has_honest_pain = True
            for st in ex.get("sets", []):
                se += EXP_PER_SET
                w = st.get("weight_kg", 0) or 0
                if name not in session_max or w > session_max[name]:
                    session_max[name] = w
        # PR（里程碑，非主要来源）
        for name, w in session_max.items():
            if name in running and w > running[name]:
                se += EXP_PER_PR
        # 合理降重：本次 < 上次且 RPE 合理
        overall_rpe = s.get("overall_rpe")
        rpe_ok = overall_rpe is not None and overall_rpe <= 8
        for name, w in session_max.items():
            if name in running and w < running[name] and rpe_ok:
                se += EXP_PER_REASONABLE_DELOAD
        # 诚实记录疼痛
        if has_honest_pain:
            se += EXP_PER_HONEST_PAIN
        # 更新历史最佳
        for name, w in session_max.items():
            if name not in running or w > running[name]:
                running[name] = w
        if s.get("session_type", "").lower() in ("cardio", "有氧", "aerobic"):
            se += EXP_PER_CARDIO
        total += se
        last_session_exp = se
    # 长期一致性：近 30 天 ≥ 8 次
    if sessions:
        dates = sorted({s.get("date") for s in sessions if s.get("date")})
        if dates:
            latest = datetime.strptime(dates[-1], "%Y-%m-%d").date()
            cutoff = latest - timedelta(days=30)
            recent_count = sum(1 for d in dates
                               if datetime.strptime(d, "%Y-%m-%d").date() >= cutoff)
            if recent_count >= 8:
                total += EXP_LONG_TERM_CONSISTENCY
    # 连击加成（仅最近一次）
    streak = compute_streak(sessions)
    bonus = 1.0
    if streak >= 5:
        bonus = STREAK_BONUS[5]
    elif streak >= 3:
        bonus = STREAK_BONUS[3]
    elif streak >= 2:
        bonus = STREAK_BONUS[2]
    total = total - last_session_exp + int(last_session_exp * bonus)
    return total


def compute_recovery(sessions):
    if not sessions:
        return {"last_session_date": None, "days_since_last": None,
                "streak_days": 0, "recent_rpe_trend": [], "active_pain": []}
    dates = sorted({s.get("date") for s in sessions if s.get("date")})
    last_date = dates[-1]
    today = datetime.now(CN_TZ).strftime("%Y-%m-%d")
    days = (datetime.strptime(today, "%Y-%m-%d").date() -
            datetime.strptime(last_date, "%Y-%m-%d").date()).days
    recent = sorted(sessions, key=lambda s: s.get("date", ""))[-5:]
    rpe_trend = [s.get("overall_rpe") for s in recent
                 if s.get("overall_rpe") is not None]
    pain = []
    for s in sorted(sessions, key=lambda s: s.get("date", ""))[-10:]:
        for ex in s.get("exercises", []):
            p = ex.get("pain", {})
            if p.get("severity", 0) > 0:
                pain.append({"location": p.get("location"),
                             "severity": p["severity"], "date": s.get("date")})
    return {"last_session_date": last_date, "days_since_last": days,
            "streak_days": compute_streak(sessions),
            "recent_rpe_trend": rpe_trend, "active_pain": pain}


def compute_attributes(sessions):
    """STR/CON 脚本算，END/AGI/INT 留空给 AI。"""
    max_w = 0
    total_reps = 0
    total_vol = 0
    for s in sessions:
        for ex in s.get("exercises", []):
            for st in ex.get("sets", []):
                w = st.get("weight_kg", 0) or 0
                r = st.get("reps", 0) or 0
                if w > max_w:
                    max_w = w
                total_reps += r
                total_vol += w * r
    return {"STR": round(max_w / 2 + total_reps / 20, 1),
            "END": None, "CON": round(total_vol / 1000, 1),
            "AGI": None, "INT": None}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update CURRENT-STATE.json summary")
    parser.add_argument("--quest-exp", type=int, default=0, help="剧情任务达成奖励经验 (EXP)")
    args = parser.parse_args()
    quest_exp = args.quest_exp

    state_file = USER_DATA / "CURRENT-STATE.json"
    if not state_file.exists():
        print(f"❌ {state_file} 不存在。先运行 init_profile.py。")
        return 1
    sessions = load_all_sessions()
    state = load_json(state_file)

    # 合并 PR 最佳记录（不冲掉历史更优表现）
    new_bests = compute_bests(sessions)
    existing_bests = state.get("recent_bests", {})
    for k, v in new_bests.items():
        if k not in existing_bests or v.get("weight_kg", 0) >= existing_bests[k].get("weight_kg", 0):
            existing_bests[k] = v
    state["recent_bests"] = existing_bests

    if sessions:
        state["recovery"] = compute_recovery(sessions)
        if "recovery_days" in state:
            state["recovery_days"] = state["recovery"]["days_since_last"]

    # 经验与等级：保留历史基线，自适应扁平/嵌套结构
    session_exp = compute_exp(sessions)
    profile_obj = state.get("profile", state)
    # 若无新 session，则维持当前已有经验值，不强制归位；固化 base_exp 防止二次重复累加
    current_exp = profile_obj.get("exp", 0)
    base_exp = profile_obj.get("base_exp", current_exp)
    total_exp = (current_exp + quest_exp) if not sessions else (base_exp + session_exp + quest_exp)

    old_level = profile_obj.get("level", 1)
    new_level = old_level
    for lv in sorted(LEVEL_THRESHOLDS, reverse=True):
        if total_exp >= LEVEL_THRESHOLDS[lv]:
            new_level = max(old_level, lv)
            break
    if new_level != old_level:
        print(f"🎉 升级！Lv.{old_level} → Lv.{new_level}")

    exp_to_next = profile_obj.get("next_level_exp", LEVEL_THRESHOLDS.get(new_level + 1, 900))
    if "profile" in state:
        state["profile"]["base_exp"] = base_exp
        state["profile"]["exp"] = total_exp
        state["profile"]["level"] = new_level
        state["profile"]["exp_to_next"] = exp_to_next
    else:
        state["base_exp"] = base_exp
        state["exp"] = total_exp
        state["level"] = new_level
        state["next_level_exp"] = exp_to_next

    # 属性更新：兼容大写 (STR/CON) 与小写 (strength/endurance)
    new_attr = compute_attributes(sessions)
    old_attr = state.get("attributes", {})
    if "STR" in old_attr and new_attr["STR"] > 0:
        old_attr["STR"] = max(old_attr.get("STR", 0), new_attr["STR"])
    if "CON" in old_attr and new_attr["CON"] > 0:
        old_attr["CON"] = max(old_attr.get("CON", 0), new_attr["CON"])
    if "strength" in old_attr and new_attr["STR"] > 0:
        old_attr["strength"] = max(old_attr.get("strength", 0), int(new_attr["STR"]))
    if "endurance" in old_attr and new_attr["CON"] > 0:
        old_attr["endurance"] = max(old_attr.get("endurance", 0), int(new_attr["CON"]))
    state["attributes"] = old_attr

    state["updated_at"] = datetime.now(CN_TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    atomic_write(state_file, state)
    str_display = old_attr.get("STR", old_attr.get("strength", 0))
    con_display = old_attr.get("CON", old_attr.get("endurance", 0))
    print(f"✅ 已更新 {state_file.name}")
    print(f"   Lv.{new_level} | EXP {total_exp}/{exp_to_next} | "
          f"STR/力量 {str_display} CON/耐力 {con_display}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
