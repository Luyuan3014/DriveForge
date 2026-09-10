from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from .models import CommandResult, Fact, Status
from .utils import changed_files, project_snapshot, utc_now


def classify_failure(output: str, phase: str) -> str:
    lower = output.lower()
    if "timed out" in lower:
        return "timeout"
    if any(token in lower for token in ("not recognized", "command not found", "no such file or directory")):
        return "tool_not_found"
    if phase == "build":
        if any(token in lower for token in ("undefined reference", "linker command failed", "ld returned")):
            return "linker"
        if any(token in lower for token in ("error:", "fatal error", "compilation terminated")):
            return "compiler"
        if any(token in lower for token in ("kconfig", "sconstruct", "cmake error")):
            return "build_configuration"
    if phase == "flash" and any(token in lower for token in ("cannot connect", "no device", "target connection", "j-link")):
        return "probe_or_target"
    if phase == "test" and any(token in lower for token in ("assert", "fail", "timeout", "not found")):
        return "hardware_test"
    return "command_failure"


class WorkflowRunner:
    def __init__(
        self,
        project: Path,
        output: Path,
        config: dict[str, Any],
        facts: dict[str, Fact],
    ) -> None:
        self.project = project.resolve()
        self.output = output.resolve()
        self.config = config
        self.facts = facts
        self.results: list[dict[str, Any]] = []
        self.output.mkdir(parents=True, exist_ok=True)

    def _command(self, phase: str) -> str | None:
        value = self.config.get("commands", {}).get(phase)
        return str(value) if value else None

    def _timeout(self, phase: str) -> int:
        value = self.config.get("timeouts", {}).get(phase, 300)
        try:
            return max(1, int(value))
        except (TypeError, ValueError):
            return 300

    def _environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "DRIVEFORGE_PROJECT": str(self.project),
                "DRIVEFORGE_OUTPUT": str(self.output),
                "DRIVEFORGE_MANIFEST": str(self.output / "hardware_manifest.yaml"),
                "DRIVEFORGE_PLAN": str(self.output / "driver_plan.yaml"),
            }
        )
        return env

    def _run_command(self, phase: str, command: str, attempt: int = 1) -> CommandResult:
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=self.project,
                env=self._environment(),
                shell=True,
                text=True,
                capture_output=True,
                timeout=self._timeout(phase),
                errors="replace",
            )
            output = "".join((completed.stdout or "", completed.stderr or ""))
            status = Status.PASS if completed.returncode == 0 else Status.FAIL
            exit_code: int | None = completed.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            output = f"{stdout}{stderr}\nCommand timed out after {self._timeout(phase)} seconds."
            status = Status.FAIL
            exit_code = None
        duration = round(time.monotonic() - started, 3)
        safe_phase = re.sub(r"[^a-z0-9_-]+", "_", phase.lower())
        log_path = self.output / "logs" / f"{safe_phase}-{attempt}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(output, encoding="utf-8", errors="replace")
        result = CommandResult(
            phase=phase,
            status=status,
            command=command,
            exit_code=exit_code,
            duration_seconds=duration,
            log=str(log_path),
            attempt=attempt,
        )
        payload = result.to_dict()
        if status == Status.FAIL:
            payload["failure_class"] = classify_failure(output, phase)
            payload["output_tail"] = output[-2000:]
        self.results.append(payload)
        return result

    def _skip(self, phase: str, reason: str) -> None:
        self.results.append({"phase": phase, "status": Status.SKIPPED.value, "reason": reason})

    def _blocked(self, phase: str, reason: str) -> None:
        self.results.append({"phase": phase, "status": Status.BLOCKED.value, "reason": reason})

    def _repair(self, failed_phase: str, attempt: int) -> bool:
        command = self._command("repair")
        if not command:
            return False
        env_command = command.replace("{phase}", failed_phase).replace("{attempt}", str(attempt))
        return self._run_command("repair", env_command, attempt).status == Status.PASS

    def execute(
        self,
        *,
        execute_patch: bool,
        execute_build: bool,
        execute_flash: bool,
        execute_test: bool,
        baseline: dict[str, str] | None = None,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        before = baseline if baseline is not None else project_snapshot(self.project)

        if execute_patch:
            command = self._command("patch")
            if not command:
                self._blocked("patch", "Execution requested but commands.patch is not configured.")
                return self.results, []
            if self._run_command("patch", command).status == Status.FAIL:
                return self.results, changed_files(before, project_snapshot(self.project))
        else:
            self._skip("patch", "Code changes are performed by the invoking engineering agent.")

        build_passed = not execute_build
        if execute_build:
            command = self._command("build") or self._default_build_command()
            if not command:
                self._blocked("build", "No build command is configured or safely detected.")
                return self.results, changed_files(before, project_snapshot(self.project))
            max_repairs = max(0, min(10, int(self.config.get("max_repair_attempts", 2))))
            for attempt in range(1, max_repairs + 2):
                result = self._run_command("build", command, attempt)
                if result.status == Status.PASS:
                    build_passed = True
                    break
                if attempt > max_repairs or not self._repair("build", attempt):
                    break
        else:
            self._skip("build", "Build execution was not enabled.")

        if execute_build and not build_passed:
            self._skip("flash", "Build did not pass.")
            self._skip("test", "Build did not pass.")
            return self.results, changed_files(before, project_snapshot(self.project))

        flash_passed = not execute_flash
        if execute_flash:
            command = self._command("flash")
            if not command:
                self._blocked("flash", "Execution requested but commands.flash is not configured.")
                return self.results, changed_files(before, project_snapshot(self.project))
            flash_passed = self._run_command("flash", command).status == Status.PASS
        else:
            self._skip("flash", "Flash execution was not enabled.")

        if execute_flash and not flash_passed:
            self._skip("test", "Flash did not pass.")
            return self.results, changed_files(before, project_snapshot(self.project))

        if execute_test:
            command = self._command("test")
            if not command:
                self._blocked("test", "Execution requested but commands.test is not configured.")
                return self.results, changed_files(before, project_snapshot(self.project))
            max_repairs = max(0, min(10, int(self.config.get("max_repair_attempts", 2))))
            for attempt in range(1, max_repairs + 2):
                result = self._run_command("test", command, attempt)
                if result.status == Status.PASS:
                    break
                if attempt > max_repairs or not self._repair("test", attempt):
                    break
                build_command = self._command("build") or self._default_build_command()
                if execute_build and build_command and self._run_command("build", build_command, attempt + 1).status == Status.FAIL:
                    break
                flash_command = self._command("flash")
                if execute_flash and flash_command and self._run_command("flash", flash_command, attempt + 1).status == Status.FAIL:
                    break
        else:
            self._skip("test", "Hardware test execution was not enabled.")

        return self.results, changed_files(before, project_snapshot(self.project))

    def _default_build_command(self) -> str | None:
        fact = self.facts.get("build.system")
        value = str(fact.value).lower() if fact and fact.resolved else ""
        return {"scons": "scons", "make": "make", "west": "west build"}.get(value)


def final_status(results: list[dict[str, Any]], requested: dict[str, bool]) -> str:
    statuses = [item.get("status") for item in results]
    if Status.BLOCKED.value in statuses:
        return Status.BLOCKED.value
    for phase in ("patch", "build", "flash", "test"):
        if not requested.get(phase):
            continue
        attempts = [
            item
            for item in results
            if item.get("phase") == phase and item.get("status") != Status.SKIPPED.value
        ]
        if not attempts or attempts[-1].get("status") != Status.PASS.value:
            return Status.FAIL.value
    if requested.get("test") and any(
        item.get("phase") == "test" and item.get("status") == Status.PASS.value for item in results
    ):
        return "VERIFIED"
    if requested.get("flash") and any(
        item.get("phase") == "flash" and item.get("status") == Status.PASS.value for item in results
    ):
        return "FLASH_PASS"
    if requested.get("build") and any(
        item.get("phase") == "build" and item.get("status") == Status.PASS.value for item in results
    ):
        return "BUILD_PASS"
    return Status.PLANNED.value


def build_report(
    request: str,
    facts: dict[str, Fact],
    plan: dict[str, Any],
    results: list[dict[str, Any]],
    modified_files: list[str],
    requested: dict[str, bool],
) -> dict[str, Any]:
    facts_payload = {key: fact.to_dict() for key, fact in sorted(facts.items())}
    failures = [item for item in results if item.get("status") in {Status.FAIL.value, Status.BLOCKED.value}]
    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "request": request,
        "target": plan.get("target"),
        "platform": facts_payload.get("platform.os"),
        "mcu": facts_payload.get("mcu.model"),
        "peripheral": plan.get("peripheral"),
        "strategy": plan.get("strategy"),
        "status": final_status(results, requested),
        "phases": results,
        "modified_files": modified_files,
        "hardware_facts": facts_payload,
        "failures": failures,
    }
