from __future__ import annotations

from typing import Any

from .models import DriverCandidate, Fact, Status
from .utils import utc_now


def _value(facts: dict[str, Fact], key: str) -> Any:
    fact = facts.get(key)
    return fact.value if fact and fact.resolved else None


def _select_reference(
    facts: dict[str, Fact],
    candidates: list[DriverCandidate],
    requested_reference: str | None,
) -> tuple[str | None, DriverCandidate | None]:
    peripheral = str(_value(facts, "target.peripheral") or "").upper()
    target = str(_value(facts, "target.instance") or "").upper()
    requested = requested_reference.upper() if requested_reference else None
    suitable = [item for item in candidates if item.peripheral == peripheral]
    if requested:
        for item in suitable:
            if requested in item.instances:
                return requested, item
        return requested, None
    for item in suitable:
        for instance in item.instances:
            if instance != target:
                return instance, item
    return None, suitable[0] if suitable else None


def build_plan(
    request: str,
    facts: dict[str, Fact],
    candidates: list[DriverCandidate],
    blockers: list[dict[str, Any]],
    requested_reference: str | None = None,
    inventory: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    target = _value(facts, "target.instance")
    peripheral = _value(facts, "target.peripheral")
    reference, candidate = _select_reference(facts, candidates, requested_reference)

    if blockers:
        strategy = "blocked"
    elif reference:
        strategy = "adapt_existing_instance"
    elif candidate:
        strategy = "extend_existing_driver"
    else:
        strategy = "implement_from_verified_sdk_evidence"

    evidence_files: list[str] = []
    for item in candidates:
        if item.peripheral == peripheral and item.path not in evidence_files:
            evidence_files.append(item.path)
        if len(evidence_files) >= 10:
            break

    steps: list[dict[str, Any]] = [
        {
            "id": "understand",
            "phase": "analyze",
            "action": "Review the manifest evidence and the selected reference implementation.",
            "acceptance": "Every hardware-dependent edit cites a resolved fact.",
        },
        {
            "id": "patch",
            "phase": "implement",
            "action": (
                f"Adapt {reference} to {target} with the smallest project-style patch."
                if reference
                else f"Implement {target} using verified project or vendor SDK patterns."
            ),
            "acceptance": "Driver, board configuration, Kconfig and build files remain internally consistent.",
        },
        {
            "id": "build",
            "phase": "build",
            "action": "Run the detected/configured build command and classify any failure.",
            "acceptance": "Build command exits with code 0.",
        },
        {
            "id": "flash",
            "phase": "flash",
            "action": "Program and verify the firmware with the explicitly configured probe command.",
            "acceptance": "Programmer reports successful program and verification.",
        },
        {
            "id": "test",
            "phase": "hardware_test",
            "action": f"Execute the {peripheral or 'peripheral'} playbook through the configured test command.",
            "acceptance": "Required device, transfer and interrupt checks pass.",
        },
        {
            "id": "repair",
            "phase": "diagnose",
            "action": "On failure, form an evidence-backed hypothesis, apply one focused repair and rerun the failed gate.",
            "acceptance": "Gate passes or the bounded repair budget is exhausted with a recorded blocker.",
        },
    ]
    if blockers:
        for step in steps:
            step["status"] = Status.BLOCKED.value
    else:
        for step in steps:
            step["status"] = "PENDING"

    risks: list[str] = []
    if requested_reference and candidate is None:
        risks.append(
            f"Requested reference {requested_reference.upper()} was not found in scanned project files; locate and verify it before patching."
        )
    if not reference:
        risks.append("No different peripheral instance was proven as a reusable reference.")
    if not evidence_files:
        risks.append("No existing driver source was found in the project scan.")

    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "request": request,
        "status": Status.BLOCKED.value if blockers else Status.PLANNED.value,
        "target": target,
        "peripheral": peripheral,
        "strategy": strategy,
        "reference": {
            "instance": reference,
            "file": candidate.path if candidate else None,
            "origin": candidate.origin if candidate else None,
        },
        "project_inventory": inventory or {},
        "evidence_files": evidence_files,
        "steps": steps,
        "risks": risks,
        "blockers": blockers,
    }
