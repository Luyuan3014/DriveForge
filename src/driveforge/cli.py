from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path
from typing import Any

from .analyzer import ProjectAnalyzer
from .config import hardware_overrides, load_config, set_dotted
from .intent import parse_request
from .planner import build_plan
from .resolver import build_manifest, merge_facts, validate_facts
from .runner import WorkflowRunner, build_report
from .utils import load_json, project_snapshot, utc_now, write_json, write_yaml
from .viewer import generate_report_page


def _coerce(value: str) -> Any:
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    if lower in {"null", "none"}:
        return None
    try:
        return int(value, 0)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="driveforge",
        description="Evidence-first RT-Thread driver engineering workflow",
    )
    parser.add_argument("--version", action="version", version="DriveForge 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("scan", "Analyze a target project and produce a hardware manifest."),
        ("plan", "Analyze facts and produce an adaptation-first driver plan."),
        ("run", "Plan and optionally execute configured workflow gates."),
    ):
        child = subparsers.add_parser(name, help=help_text)
        child.add_argument("project", type=Path, help="RT-Thread project directory")
        child.add_argument("-r", "--request", help="Driver requirement in natural language")
        child.add_argument("-c", "--config", type=Path, help="DriveForge JSON configuration")
        child.add_argument("-o", "--output", type=Path, help="Artifact directory (default: PROJECT/.driveforge)")
        child.add_argument(
            "--set",
            action="append",
            default=[],
            metavar="KEY=VALUE",
            help="Override configuration, for example hardware.pins.rx=PD0",
        )
        child.add_argument("--mcu", help="Verified MCU model supplied by the user")
        child.add_argument("--os-version", help="Verified RT-Thread version")
        child.add_argument("--reference", help="Existing peripheral instance to adapt, e.g. CAN1")
        child.add_argument("--rx-pin", help="Verified RX pin")
        child.add_argument("--tx-pin", help="Verified TX pin")
        child.add_argument("--clock-bus", help="Verified peripheral clock bus")
        child.add_argument("--clock-gate", help="Verified SDK clock gate symbol")
        child.add_argument("--clock-frequency", type=int, help="Verified peripheral clock frequency in Hz")
        child.add_argument("--irq", help="Verified IRQ symbol")
    run = subparsers.choices["run"]
    run.add_argument("--execute-patch", action="store_true", help="Run commands.patch from the config")
    run.add_argument("--execute-build", action="store_true", help="Run the configured/detected build")
    run.add_argument("--execute-flash", action="store_true", help="Run commands.flash from the config")
    run.add_argument("--execute-test", action="store_true", help="Run commands.test from the config")
    view = subparsers.add_parser("view", help="Open a read-only HTML view of real workflow artifacts.")
    view.add_argument("project", type=Path, help="RT-Thread project directory")
    view.add_argument("-o", "--output", type=Path, help="Artifact directory (default: PROJECT/.driveforge)")
    view.add_argument("--no-open", action="store_true", help="Generate the page without opening a browser")
    return parser


def _apply_cli_config(config: dict[str, Any], args: argparse.Namespace) -> None:
    for item in args.set:
        if "=" not in item:
            raise ValueError(f"--set expects KEY=VALUE, received: {item}")
        key, value = item.split("=", 1)
        set_dotted(config, key, _coerce(value))
    mappings = {
        "mcu": "hardware.mcu.model",
        "os_version": "hardware.platform.version",
        "reference": "hardware.driver.reference",
        "rx_pin": "hardware.pins.rx",
        "tx_pin": "hardware.pins.tx",
        "clock_bus": "hardware.clock.bus",
        "clock_gate": "hardware.clock.gate",
        "clock_frequency": "hardware.clock.frequency",
        "irq": "hardware.interrupt.irq",
    }
    for attr, key in mappings.items():
        value = getattr(args, attr, None)
        if value is not None:
            set_dotted(config, key, value)
    if args.request is not None:
        config["request"] = args.request


def _prepare(args: argparse.Namespace) -> tuple[Path, Path, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    project = args.project.resolve()
    if not project.is_dir():
        raise ValueError(f"Project directory does not exist: {project}")
    config = load_config(args.config.resolve() if args.config else None)
    _apply_cli_config(config, args)
    request = str(config.get("request") or "").strip()
    if not request:
        raise ValueError("A driver requirement is required through --request or config.request.")

    overrides = hardware_overrides(config)
    intent = parse_request(request)
    if overrides.get("target.peripheral"):
        intent.peripheral = str(overrides["target.peripheral"]).upper()
    if overrides.get("target.instance"):
        intent.instance = str(overrides["target.instance"]).upper()

    scan = ProjectAnalyzer(project, intent).analyze()
    facts = merge_facts(scan, intent, overrides)
    blockers, fact_warnings = validate_facts(facts)
    warnings = [*scan.warnings, *fact_warnings]
    manifest = build_manifest(project, request, facts, blockers, warnings)
    reference = overrides.get("driver.reference")
    plan = build_plan(
        request,
        facts,
        scan.driver_candidates,
        blockers,
        str(reference) if reference else None,
        scan.inventory,
    )
    output = args.output.resolve() if args.output else project / ".driveforge"
    return project, output, config, {"scan": scan, "facts": facts, "blockers": blockers}, manifest, plan


def _write_base_artifacts(output: Path, manifest: dict[str, Any], plan: dict[str, Any] | None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    write_yaml(output / "hardware_manifest.yaml", manifest)
    if plan is not None:
        write_yaml(output / "driver_plan.yaml", plan)


def _print_summary(output: Path, manifest: dict[str, Any], plan: dict[str, Any] | None, report: dict[str, Any] | None = None) -> None:
    payload = {
        "status": report.get("status") if report else (plan.get("status") if plan else manifest.get("status")),
        "manifest": str(output / "hardware_manifest.yaml"),
        "plan": str(output / "driver_plan.yaml") if plan else None,
        "report": str(output / "verification_report.yaml") if report else None,
        "blockers": manifest.get("blockers", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "view":
            project = args.project.resolve()
            if not project.is_dir():
                raise ValueError(f"Project directory does not exist: {project}")
            output = args.output.resolve() if args.output else project / ".driveforge"
            page, status = generate_report_page(output)
            if not args.no_open:
                webbrowser.open(page.as_uri())
            print(json.dumps({"status": status, "page": str(page)}, ensure_ascii=False, indent=2))
            return 0
        project, output, config, context, manifest, plan = _prepare(args)
        if args.command == "scan":
            _write_base_artifacts(output, manifest, None)
            write_json(output / "scan.json", context["scan"].to_dict())
            _print_summary(output, manifest, None)
            return 2 if context["blockers"] else 0

        _write_base_artifacts(output, manifest, plan)
        write_json(
            output / "state.json",
            {
                "schema_version": "1.0",
                "generated_at": utc_now(),
                "manifest": manifest,
                "plan": plan,
                "scan": context["scan"].to_dict(),
            },
        )
        if args.command == "plan":
            write_json(
                output / "baseline.json",
                {"project": str(project), "snapshot": project_snapshot(project)},
            )
            _print_summary(output, manifest, plan)
            return 2 if context["blockers"] else 0

        if context["blockers"]:
            report = build_report(
                str(config["request"]),
                context["facts"],
                plan,
                [{"phase": "fact_gate", "status": "BLOCKED", "blockers": context["blockers"]}],
                [],
                {"build": False, "flash": False, "test": False},
            )
            write_yaml(output / "verification_report.yaml", report)
            _print_summary(output, manifest, plan, report)
            return 2

        requested = {
            "patch": bool(args.execute_patch),
            "build": bool(args.execute_build),
            "flash": bool(args.execute_flash),
            "test": bool(args.execute_test),
        }
        baseline: dict[str, str] | None = None
        baseline_path = output / "baseline.json"
        if baseline_path.exists():
            baseline_data = load_json(baseline_path)
            if baseline_data.get("project") == str(project) and isinstance(baseline_data.get("snapshot"), dict):
                baseline = {
                    str(key): str(value) for key, value in baseline_data["snapshot"].items()
                }
        runner = WorkflowRunner(project, output, config, context["facts"])
        results, modified_files = runner.execute(
            execute_patch=requested["patch"],
            execute_build=requested["build"],
            execute_flash=requested["flash"],
            execute_test=requested["test"],
            baseline=baseline,
        )
        report = build_report(
            str(config["request"]), context["facts"], plan, results, modified_files, requested
        )
        write_yaml(output / "verification_report.yaml", report)
        write_json(output / "verification_report.json", report)
        _print_summary(output, manifest, plan, report)
        return 0 if report["status"] not in {"FAIL", "BLOCKED"} else (2 if report["status"] == "BLOCKED" else 1)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"driveforge: error: {exc}\n")
    return 2
