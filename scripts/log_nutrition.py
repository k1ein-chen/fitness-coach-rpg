#!/usr/bin/env python3
"""记录单日体重、热量摄入，并自动刷新动态代谢状态。

用法：
    python scripts/log_nutrition.py --weight 73.5 --cal 1850 --protein 140
    python scripts/log_nutrition.py --date 2026-10-09 --weight 74.0
"""
import argparse
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, atomic_write

ROOT = Path(__file__).resolve().parent.parent
USER_DATA = ROOT / "user-data"
CN_TZ = timezone(timedelta(hours=8))


def main():
    parser = argparse.ArgumentParser(description="记录体重与摄入热量")
    parser.add_argument("--date", help="日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--weight", type=float, help="早晨空腹体重 (kg)")
    parser.add_argument("--cal", type=int, help="今日总摄入热量 (kcal)")
    parser.add_argument("--protein", type=int, help="今日蛋白质摄入 (g)")
    parser.add_argument("--notes", help="体感或饮食备注")
    args = parser.parse_args()

    date_str = args.date or datetime.now(CN_TZ).strftime("%Y-%m-%d")

    nutrition_file = USER_DATA / "nutrition.json"
    nutrition = load_json(nutrition_file) if nutrition_file.exists() else {}

    entry = nutrition.get(date_str, {})
    if args.weight is not None:
        entry["weight_kg"] = round(args.weight, 2)
    if args.cal is not None:
        entry["calories_in"] = args.cal
    if args.protein is not None:
        entry["protein_g"] = args.protein
    if args.notes is not None:
        entry["notes"] = args.notes

    if not entry:
        print("⚠️ 未提供任何有效数据 (--weight / --cal / --protein / --notes)")
        return 1

    nutrition[date_str] = entry
    atomic_write(nutrition_file, nutrition)
    print(f"📝 已记录 {date_str} 营养与体重数据: {entry}")

    # 自动触发代谢与 TDEE 重新计算
    script_path = Path(__file__).resolve().parent / "update_metabolism.py"
    subprocess.run([sys.executable, str(script_path)], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
