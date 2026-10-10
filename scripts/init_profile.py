#!/usr/bin/env python3
"""初始化 user-data/，从 assets/starter-profile/ 复制模板。

用法：
    python scripts/init_profile.py --name 小龙 --theme 武侠
    python scripts/init_profile.py
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, atomic_write

ROOT = Path(__file__).resolve().parent.parent
if (ROOT / "assets" / "starter-profile").exists():
    STARTER = ROOT / "assets" / "starter-profile"
else:
    STARTER = ROOT / "share" / "assets" / "starter-profile"
USER_DATA = ROOT / "user-data"


def main():
    parser = argparse.ArgumentParser(description="初始化训练档案")
    parser.add_argument("--name", help="你的名字")
    parser.add_argument("--theme", help="RPG 主题")
    parser.add_argument("--force", action="store_true", help="覆盖已有 user-data")
    args = parser.parse_args()

    if USER_DATA.exists() and not args.force:
        print(f"❌ {USER_DATA} 已存在。用 --force 覆盖（会删除现有数据）。")
        return 1

    if USER_DATA.exists():
        shutil.rmtree(USER_DATA)
    shutil.copytree(STARTER, USER_DATA)

    # 填初始值
    state_file = USER_DATA / "CURRENT-STATE.json"
    state = load_json(state_file)
    if args.name:
        state["profile"]["name"] = args.name
    if args.theme:
        state["profile"]["theme"] = args.theme
    atomic_write(state_file, state)

    # 同步 PROFILE.md 占位符
    profile_file = USER_DATA / "PROFILE.md"
    text = profile_file.read_text(encoding="utf-8")
    if args.name:
        text = text.replace("<你的名字>", args.name)
    if args.theme:
        text = text.replace("<经典模式 / 武侠 / 剑与魔法 / 战士 / 自定义>", args.theme)
    profile_file.write_text(text, encoding="utf-8")

    print(f"✅ 已初始化 {USER_DATA}")
    print("   编辑 PROFILE.md 和 CURRENT-STATE.json 完善档案，或直接开始训练。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
