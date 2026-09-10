from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from driveforge.intent import parse_request


class IntentTests(unittest.TestCase):
    def test_parses_english_instance_from_chinese_request(self) -> None:
        intent = parse_request("把当前 UART7 适配到 RT-Thread serial framework，要求支持中断接收")
        self.assertEqual("UART", intent.peripheral)
        self.assertEqual("UART7", intent.instance)
        self.assertEqual("adapt", intent.operation)

    def test_parses_supported_peripheral_without_instance(self) -> None:
        intent = parse_request("验证 I2C 驱动")
        self.assertEqual("I2C", intent.peripheral)
        self.assertIsNone(intent.instance)
        self.assertEqual("verify", intent.operation)


if __name__ == "__main__":
    unittest.main()
