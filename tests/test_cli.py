from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from driveforge.cli import main
from test_pipeline import create_rtthread_can_project


class CliTests(unittest.TestCase):
    def test_plan_writes_reviewable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["plan", str(project), "--request", "增加 CAN0 驱动"])
            self.assertEqual(0, code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("PLANNED", payload["status"])
            output = project / ".driveforge"
            self.assertTrue((output / "hardware_manifest.yaml").exists())
            self.assertTrue((output / "driver_plan.yaml").exists())
            self.assertTrue((output / "state.json").exists())
            self.assertTrue((output / "baseline.json").exists())
            self.assertIn("source:", (output / "hardware_manifest.yaml").read_text(encoding="utf-8"))

    def test_run_reports_changes_since_plan_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, main(["plan", str(project), "-r", "增加 CAN0 驱动"]))
            driver = project / "drv_can.c"
            driver.write_text(driver.read_text(encoding="utf-8") + "\n/* CAN0 adaptation */\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, main(["run", str(project), "-r", "增加 CAN0 驱动"]))
            report = json.loads((project / ".driveforge" / "verification_report.json").read_text(encoding="utf-8"))
            self.assertIn("drv_can.c", report["modified_files"])
            self.assertEqual("PLANNED", report["status"])

    def test_explicit_full_workflow_reaches_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            python_command = f'"{sys.executable}" -c "print(123)"'
            config_path = project / "driveforge.json"
            config_path.write_text(
                json.dumps(
                    {
                        "request": "增加 CAN0 驱动并验证收发",
                        "commands": {
                            "build": python_command,
                            "flash": python_command,
                            "test": python_command,
                        },
                        "max_repair_attempts": 0,
                    }
                ),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "run",
                        str(project),
                        "--config",
                        str(config_path),
                        "--execute-build",
                        "--execute-flash",
                        "--execute-test",
                    ]
                )
            self.assertEqual(0, code)
            report = json.loads((project / ".driveforge" / "verification_report.json").read_text(encoding="utf-8"))
            self.assertEqual("VERIFIED", report["status"])
            terminal_phases = {
                item["phase"]: item["status"] for item in report["phases"] if item["phase"] in {"build", "flash", "test"}
            }
            self.assertEqual({"build": "PASS", "flash": "PASS", "test": "PASS"}, terminal_phases)

    def test_view_generates_read_only_page_from_real_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            create_rtthread_can_project(project)
            request = "增加 CAN0 驱动 <script>alert(1)</script>"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, main(["plan", str(project), "-r", request]))
                self.assertEqual(0, main(["view", str(project), "--no-open"]))
            page = (project / ".driveforge" / "report.html").read_text(encoding="utf-8")
            self.assertIn("DriveForge 只读执行报告", page)
            self.assertIn("PLANNED", page)
            self.assertIn("驱动规划", page)
            self.assertIn("adapt_existing_instance", page)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
            self.assertNotIn("<script>alert(1)</script>", page)


if __name__ == "__main__":
    unittest.main()
