#!/usr/bin/env python3
"""追加一次训练记录到 sessions/YYYY-MM-DD.json。

用法：
    echo '{"session_type":"push","exercises":[...]}' | python scripts/append_session.py
    python scripts/append_session.py --file session.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, atomic_write

ROOT = Path(__file__).resolve().parent.parent
USER_DATA = ROOT / "user-data"
CN_TZ = timezone(timedelta(hours=8))


def validate_exercise(ex):
    sets = ex.get("sets", [])
    if not sets:
        raise ValueError(f"动作 {ex.get('exercise', '?')} 没有 sets")
    for i, s in enumerate(sets):
        w = s.get("weight_kg")
        r = s.get("reps")
        rpe = s.get("rpe")
        if w is not None and w < 0:
            raise ValueError(f"动作 {ex['exercise']} 第{i+1}组 weight_kg 必须 >= 0")
        if r is not None and r <= 0:
            raise ValueError(f"动作 {ex['exercise']} 第{i+1}组 reps 必须 > 0")
        if rpe is not None and not (1 <= rpe <= 10):
            raise ValueError(f"动作 {ex['exercise']} 第{i+1}组 rpe 必须 1-10")


def normalize_exercise(ex):
    """lbs → kg。"""
    for s in ex.get("sets", []):
        if "weight_lbs" in s and "weight_kg" not in s:
            s["weight_kg"] = round(s["weight_lbs"] * 0.4536, 2)
            del s["weight_lbs"]
    return ex


def main():
    parser = argparse.ArgumentParser(description="追加训练记录")
    parser.add_argument("--file", help="训练数据 JSON 文件路径")
    parser.add_argument("--date", help="日期 YYYY-MM-DD（默认今天）")
    args = parser.parse_args()

    if args.file:
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    else:
        raw = sys.stdin.read()
        if not raw.strip():
            print("❌ 未提供训练数据。用 --file 或管道传入 JSON。")
            return 1
        data = json.loads(raw)

    # 日期标准化
    if args.date:
        date = args.date
    elif "date" in data:
        date = data["date"]
    else:
        date = datetime.now(CN_TZ).strftime("%Y-%m-%d")

    # 校验 + 标准化
    exercises = data.get("exercises", [])
    for ex in exercises:
        normalize_exercise(ex)
        validate_exercise(ex)

    data["date"] = date
    data["schema_version"] = data.get("schema_version", "1.0")

    # 追加到 sessions 文件
    session_file = USER_DATA / "sessions" / f"{date}.json"
    session_file.parent.mkdir(parents=True, exist_ok=True)

    if session_file.exists():
        session = load_json(session_file)
        session.setdefault("exercises", []).extend(exercises)
        if "duration_minutes" in data:
            session["duration_minutes"] = max(
                session.get("duration_minutes", 0), data["duration_minutes"])
        if "overall_rpe" in data:
            session["overall_rpe"] = data["overall_rpe"]
    else:
        session = data

    atomic_write(session_file, session)
    print(f"✅ 已追加 {len(exercises)} 个动作到 {session_file.name}")
    print("   下一步：运行 update_summary.py 更新状态。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
