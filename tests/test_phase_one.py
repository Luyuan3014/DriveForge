from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from driveforge.c_analysis import CSourceAnalyzer
from driveforge.defensive import add_timeout_guard, find_unbounded_waits
from driveforge.patcher import AdaptFirstPatcher, PatchOperation
from driveforge.svd import parse_svd
from driveforge.timing import solve_can_bittiming, solve_spi_clock, solve_uart_baudrate


class PhaseOneTests(unittest.TestCase):
    def test_svd_register_and_field_facts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chip.svd"
            path.write_text("""<device><name>TEST</name><peripherals><peripheral><name>CAN0</name><baseAddress>0x4000</baseAddress><registers><register><name>STAT</name><addressOffset>0x10</addressOffset><fields><field><name>READY</name><bitRange>[3:2]</bitRange></field></fields></register></registers></peripheral></peripherals></device>""", encoding="utf-8")
            device = parse_svd(path)
            register = device.peripheral("CAN0").register("STAT")
            self.assertEqual(0x4010, device.fact_index()["svd.can0.registers"]["STAT"]["address"])
            self.assertEqual(0b1100, register.fields[0].mask)

    def test_conditional_scanner_ignores_disabled_initializer(self) -> None:
        model = CSourceAnalyzer().parse("driver.c", "#if 0\n#define DISABLED 1\n#endif\n#define ENABLED 1\nstatic struct cfg active = {.pin = PA0};\n")
        self.assertEqual(["ENABLED"], [item.name for item in model.macros if item.active])
        self.assertEqual("active", model.initializers[0].variable)

    def test_timing_solutions_are_within_contract(self) -> None:
        can = solve_can_bittiming(60_000_000, 500_000)
        self.assertLessEqual(can.error_percent, 0.5)
        self.assertTrue(0.80 <= can.sample_point <= 0.875)
        self.assertLessEqual(solve_uart_baudrate(60_000_000, 115200).error_percent, 1.5)
        self.assertLessEqual(solve_spi_clock(60_000_000, 10_000_000).sck_hz, 10_000_000)

    def test_patch_preview_requires_unique_anchor_and_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drv.c"
            path.write_text("init(CAN1);\n", encoding="utf-8")
            result = AdaptFirstPatcher(directory).preview([PatchOperation("drv.c", {"init(CAN1);": "init(CAN0);"})])
            self.assertFalse(result.applied)
            self.assertIn("CAN0", result.diff)
            self.assertIn("CAN1", path.read_text(encoding="utf-8"))

    def test_timeout_guard_finds_hardware_wait(self) -> None:
        findings = find_unbounded_waits("drv.c", "while (!(CAN_STAT & READY));\n")
        self.assertEqual(1, len(findings))
        self.assertIn("timeout", add_timeout_guard("while (!(CAN_STAT & READY));").lower())


if __name__ == "__main__":
    unittest.main()
