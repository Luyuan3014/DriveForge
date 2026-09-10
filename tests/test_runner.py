from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from driveforge.models import Confidence, Fact
from driveforge.runner import WorkflowRunner, build_report, final_status


class RunnerTests(unittest.TestCase):
    def test_build_pass_is_not_hardware_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            output = project / ".driveforge"
            command = f'"{sys.executable}" -c "print(123)"'
            config = {
                "commands": {"build": command, "flash": None, "test": None, "repair": None},
                "timeouts": {"build": 20},
                "max_repair_attempts": 0,
            }
            facts = {"build.system": Fact("build.system", "scons", Confidence.VERIFIED, "test")}
            runner = WorkflowRunner(project, output, config, facts)
            results, modified = runner.execute(
                execute_patch=False,
                execute_build=True,
                execute_flash=False,
                execute_test=False,
            )
            plan = {"target": "CAN0", "peripheral": "CAN", "strategy": "adapt_existing_instance"}
            report = build_report(
                "add CAN0", facts, plan, results, modified, {"build": True, "flash": False, "test": False}
            )
            self.assertEqual("BUILD_PASS", report["status"])
            self.assertTrue((output / "logs" / "build-1.log").exists())

    def test_missing_requested_flash_command_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            config = {
                "commands": {"build": None, "flash": None, "test": None, "repair": None},
                "timeouts": {},
                "max_repair_attempts": 0,
            }
            runner = WorkflowRunner(project, project / ".driveforge", config, {})
            results, _ = runner.execute(
                execute_patch=False,
                execute_build=False,
                execute_flash=True,
                execute_test=False,
            )
            self.assertTrue(any(item["phase"] == "flash" and item["status"] == "BLOCKED" for item in results))

    def test_recovered_failure_uses_latest_gate_result(self) -> None:
        results = [
            {"phase": "build", "status": "FAIL", "attempt": 1},
            {"phase": "repair", "status": "PASS", "attempt": 1},
            {"phase": "build", "status": "PASS", "attempt": 2},
        ]
        self.assertEqual(
            "BUILD_PASS",
            final_status(results, {"patch": False, "build": True, "flash": False, "test": False}),
        )


if __name__ == "__main__":
    unittest.main()
