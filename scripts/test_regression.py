#!/usr/bin/env python3
"""自动化回归测试（对照 references/test-scenarios.md）。

运行：
    python scripts/test_regression.py
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from _common import load_json
import validate_state


class RegressionTests(unittest.TestCase):
    def test_schema_validity(self):
        """测试核心状态文件是否符合 schema 规范"""
        code = validate_state.main()
        self.assertEqual(code, 0, "validate_state 返回非零退出码")

    def test_current_state_structure(self):
        """测试 CURRENT-STATE.json 字段完整性与 base_exp 存在性"""
        p = ROOT / "user-data" / "CURRENT-STATE.json"
        self.assertTrue(p.exists(), "CURRENT-STATE.json 不存在")
        data = load_json(p)
        self.assertIn("exp", data)
        self.assertIn("base_exp", data)
        self.assertIn("attributes", data)
        self.assertIn("strength", data["attributes"])

    def test_nutrition_ema_consistency(self):
        """测试 nutrition.json 数据可读性"""
        p = ROOT / "user-data" / "nutrition.json"
        self.assertTrue(p.exists(), "nutrition.json 不存在")
        data = load_json(p)
        self.assertTrue(len(data) >= 1)


if __name__ == "__main__":
    unittest.main()
