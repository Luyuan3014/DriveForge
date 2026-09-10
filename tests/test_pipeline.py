from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from driveforge.analyzer import ProjectAnalyzer
from driveforge.config import hardware_overrides, load_config
from driveforge.intent import parse_request
from driveforge.planner import build_plan
from driveforge.resolver import build_manifest, merge_facts, validate_facts


def create_rtthread_can_project(root: Path) -> None:
    (root / "SConstruct").write_text("CC='arm-none-eabi-gcc'\n", encoding="utf-8")
    (root / "rtdef.h").write_text(
        "#define RT_VERSION 5\n#define RT_SUBVERSION 1\n#define RT_REVISION 0\n",
        encoding="utf-8",
    )
    (root / "board.h").write_text(
        "\n".join(
            (
                "#include <rtthread.h>",
                "#define SOC_MODEL GD32F470ZIT6",
                "#define CAN0_RX_PIN PD0",
                "#define CAN0_TX_PIN PD1",
                "#define CAN0_CLOCK RCU_CAN0",
                "#define CAN0_RX_IRQ CAN0_RX0_IRQn",
            )
        ),
        encoding="utf-8",
    )
    (root / "drv_can.c").write_text(
        "#ifdef RT_USING_CAN\nvoid rt_hw_can_init(void) { can_deinit(CAN1); }\n#endif\n",
        encoding="utf-8",
    )
    (root / "Kconfig").write_text("config BSP_USING_CAN\n    bool \"Enable CAN\"\n", encoding="utf-8")
    (root / "linker.ld").write_text("MEMORY { FLASH (rx) : ORIGIN = 0x08000000 }\n", encoding="utf-8")
    (root / "startup_gd32f470.s").write_text("Reset_Handler:\n", encoding="utf-8")


class PipelineTests(unittest.TestCase):
    def test_evidence_gate_and_adapt_first_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            request = "给这个项目增加 CAN0 驱动并验证收发"
            intent = parse_request(request)
            scan = ProjectAnalyzer(project, intent).analyze()
            facts = merge_facts(scan, intent, {})
            blockers, warnings = validate_facts(facts)
            self.assertEqual([], blockers)
            self.assertEqual("GD32F470ZIT6", facts["mcu.model"].value)
            self.assertEqual("PD0", facts["pins.rx"].value)
            self.assertEqual("CAN0_RX0_IRQn", facts["interrupt.irq"].value)
            self.assertIn("Kconfig", scan.inventory["kconfig"])
            self.assertIn("linker.ld", scan.inventory["linker_scripts"])
            self.assertIn("startup_gd32f470.s", scan.inventory["startup"])
            plan = build_plan(request, facts, scan.driver_candidates, blockers)
            self.assertEqual("adapt_existing_instance", plan["strategy"])
            self.assertEqual("CAN1", plan["reference"]["instance"])
            manifest = build_manifest(project, request, facts, blockers, warnings)
            self.assertEqual("READY", manifest["status"])
            self.assertGreaterEqual(manifest["fact_summary"]["verified"], 8)

    def test_missing_hardware_facts_block_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "rtthread.h").write_text("#define RT_VERSION 5\n", encoding="utf-8")
            (project / "board.h").write_text("#define SOC STM32F407ZGT6\n", encoding="utf-8")
            intent = parse_request("增加 CAN0 驱动")
            scan = ProjectAnalyzer(project, intent).analyze()
            facts = merge_facts(scan, intent, {})
            blockers, _ = validate_facts(facts)
            missing = {item["fact"] for item in blockers}
            self.assertIn("pins.rx", missing)
            self.assertIn("pins.tx", missing)
            self.assertIn("clock.gate or clock.bus", missing)
            self.assertIn("interrupt.irq", missing)

    def test_json_config_flattens_hardware_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "driveforge.json"
            path.write_text(
                json.dumps({"hardware": {"pins": {"rx": "PD0"}, "clock": {"frequency": 60000000}}}),
                encoding="utf-8",
            )
            config = load_config(path)
            flattened = hardware_overrides(config)
            self.assertEqual("PD0", flattened["pins.rx"])
            self.assertEqual(60000000, flattened["clock.frequency"])

    def test_user_symbols_keep_case_and_model_derivations_follow_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            intent = parse_request("增加 CAN0 驱动")
            scan = ProjectAnalyzer(project, intent).analyze()
            facts = merge_facts(
                scan,
                intent,
                {"mcu.model": "STM32F407ZGT6", "interrupt.irq": "CAN0_RX0_IRQn"},
            )
            self.assertEqual("CAN0_RX0_IRQn", facts["interrupt.irq"].value)
            self.assertEqual("STM32F4", facts["mcu.family"].value)
            self.assertEqual("STMicroelectronics", facts["mcu.vendor"].value)

    def test_invalid_pin_and_mismatched_instance_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            intent = parse_request("增加 CAN0 驱动")
            scan = ProjectAnalyzer(project, intent).analyze()
            facts = merge_facts(
                scan,
                intent,
                {"target.peripheral": "SPI", "target.instance": "CAN0", "pins.rx": "PZ99"},
            )
            blockers, _ = validate_facts(facts)
            blocked_facts = [item["fact"] for item in blockers]
            self.assertIn("target.instance", blocked_facts)
            self.assertIn("pins.rx", blocked_facts)


if __name__ == "__main__":
    unittest.main()
