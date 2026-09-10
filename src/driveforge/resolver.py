from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .intent import DriverIntent, SUPPORTED_PERIPHERALS
from .models import Confidence, Evidence, Fact, ScanResult, Status
from .utils import utc_now


CRITICAL_FACT_GROUPS: dict[str, tuple[tuple[str, ...], ...]] = {
    "GPIO": (("pins.pin",),),
    "UART": (("pins.rx",), ("pins.tx",), ("clock.gate", "clock.bus"), ("interrupt.irq",)),
    "SPI": (("pins.sck",), ("pins.miso",), ("pins.mosi",), ("clock.gate", "clock.bus")),
    "I2C": (("pins.scl",), ("pins.sda",), ("clock.gate", "clock.bus")),
    "CAN": (("pins.rx",), ("pins.tx",), ("clock.gate", "clock.bus"), ("interrupt.irq",)),
    "ADC": (("pins.pin",), ("target.channel",), ("clock.gate", "clock.bus")),
    "PWM": (("pins.pin",), ("target.channel",), ("clock.gate", "clock.bus")),
}


def _normalize_os(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    compact = re.sub(r"[\s_-]+", "", value).lower()
    return "rt-thread" if compact in {"rtthread", "rtt"} else value.lower()


def _normalize_peripheral(value: Any) -> Any:
    return value.upper() if isinstance(value, str) else value


def _derive_mcu_facts(facts: dict[str, Fact]) -> None:
    model_fact = facts.get("mcu.model")
    if not model_fact or not isinstance(model_fact.value, str):
        return
    model = model_fact.value.upper()
    if model.startswith("GD32"):
        vendor = "GigaDevice"
        family = re.match(r"GD32F4", model)
    elif model.startswith("STM32"):
        vendor = "STMicroelectronics"
        family = re.match(r"STM32F4", model)
    else:
        vendor = None
        family = None
    current_vendor = facts.get("mcu.vendor")
    if vendor and (current_vendor is None or current_vendor.source != "user_config"):
        facts["mcu.vendor"] = Fact(
            "mcu.vendor", vendor, Confidence.HIGH, "derived:mcu.model", model_fact.evidence
        )
    if family:
        current_family = facts.get("mcu.family")
        if current_family is None or current_family.source != "user_config":
            facts["mcu.family"] = Fact(
                "mcu.family", family.group(0), Confidence.HIGH, "derived:mcu.model", model_fact.evidence
            )


def merge_facts(
    scan: ScanResult,
    intent: DriverIntent,
    overrides: dict[str, Any],
) -> dict[str, Fact]:
    facts = dict(scan.facts)
    if intent.peripheral:
        facts["target.peripheral"] = Fact(
            "target.peripheral",
            intent.peripheral,
            Confidence.VERIFIED,
            "user_request",
            [Evidence(path="<request>", excerpt=intent.request)],
        )
    if intent.instance:
        facts["target.instance"] = Fact(
            "target.instance",
            intent.instance,
            Confidence.VERIFIED,
            "user_request",
            [Evidence(path="<request>", excerpt=intent.request)],
        )

    for key, value in overrides.items():
        if value is None or value == "":
            continue
        if key == "platform.os":
            value = _normalize_os(value)
        elif key == "target.peripheral":
            value = _normalize_peripheral(value)
        elif key in {"target.instance", "mcu.model", "mcu.family", "clock.gate"} and isinstance(value, str):
            value = value.upper()
        elif key.startswith("pins.") and isinstance(value, str):
            pin_match = re.fullmatch(r"P?([A-K])[._-]?(\d{1,2})", value.strip(), re.IGNORECASE)
            if pin_match:
                value = f"P{pin_match.group(1).upper()}{int(pin_match.group(2))}"
        facts[key] = Fact(
            key=key,
            value=value,
            confidence=Confidence.VERIFIED,
            source="user_config",
            evidence=[Evidence(path="<config>", excerpt=f"{key}={value}")],
        )

    target = facts.get("target.instance")
    peripheral = facts.get("target.peripheral")
    if target and isinstance(target.value, str) and not peripheral:
        prefix = re.sub(r"\d+$", "", target.value.upper())
        if prefix in SUPPORTED_PERIPHERALS:
            facts["target.peripheral"] = Fact(
                "target.peripheral", prefix, Confidence.HIGH, "derived:target.instance", target.evidence
            )
    _derive_mcu_facts(facts)
    return facts


def _has_resolved(facts: dict[str, Fact], options: tuple[str, ...]) -> bool:
    return any(key in facts and facts[key].resolved for key in options)


def validate_facts(facts: dict[str, Fact]) -> tuple[list[dict[str, Any]], list[str]]:
    blockers: list[dict[str, Any]] = []
    warnings: list[str] = []
    for key in ("platform.os", "mcu.model", "target.peripheral", "target.instance"):
        if not _has_resolved(facts, (key,)):
            blockers.append(
                {
                    "fact": key,
                    "reason": "Critical fact has no traceable value.",
                    "resolution": f"Provide hardware.{key} in the config or add project evidence.",
                }
            )

    os_value = facts.get("platform.os")
    if os_value and os_value.resolved and os_value.value != "rt-thread":
        blockers.append(
            {
                "fact": "platform.os",
                "reason": f"MVP supports RT-Thread only, detected {os_value.value}.",
                "resolution": "Use an RT-Thread target or extend the platform adapter.",
            }
        )

    mcu = facts.get("mcu.model")
    if mcu and mcu.resolved and not re.match(r"^(?:GD32F4|STM32F4)", str(mcu.value), re.IGNORECASE):
        blockers.append(
            {
                "fact": "mcu.model",
                "reason": f"MVP supports GD32F4 and STM32F4, detected {mcu.value}.",
                "resolution": "Use a supported MCU or add a platform pack before implementation.",
            }
        )

    peripheral_fact = facts.get("target.peripheral")
    peripheral = str(peripheral_fact.value).upper() if peripheral_fact and peripheral_fact.resolved else None
    instance_fact = facts.get("target.instance")
    instance = str(instance_fact.value).upper() if instance_fact and instance_fact.resolved else None
    if peripheral and peripheral not in SUPPORTED_PERIPHERALS:
        blockers.append(
            {
                "fact": "target.peripheral",
                "reason": f"{peripheral} is outside the MVP peripheral set.",
                "resolution": f"Choose one of: {', '.join(SUPPORTED_PERIPHERALS)}.",
            }
        )
    for options in CRITICAL_FACT_GROUPS.get(peripheral or "", ()):
        if not _has_resolved(facts, options):
            label = " or ".join(options)
            blockers.append(
                {
                    "fact": label,
                    "reason": "Required hardware fact is unknown; DriveForge will not guess it.",
                    "resolution": f"Add hardware.{options[0]} to the config or expose it in board/SDK files.",
                }
            )

    if peripheral and instance and not instance.startswith(peripheral):
        blockers.append(
            {
                "fact": "target.instance",
                "reason": f"Instance {instance} is inconsistent with peripheral {peripheral}.",
                "resolution": "Correct hardware.target.peripheral or hardware.target.instance.",
            }
        )
    for key, fact in facts.items():
        if key.startswith("pins.") and fact.resolved:
            match = re.fullmatch(r"P([A-K])(\d{1,2})", str(fact.value), re.IGNORECASE)
            if not match or not 0 <= int(match.group(2)) <= 15:
                blockers.append(
                    {
                        "fact": key,
                        "reason": f"Pin value {fact.value} is not a supported Cortex-M GPIO name.",
                        "resolution": "Use a verified pin in PA0..PK15 form.",
                    }
                )
    frequency = facts.get("clock.frequency")
    if frequency and frequency.resolved:
        try:
            valid_frequency = int(frequency.value) > 0
        except (TypeError, ValueError):
            valid_frequency = False
        if not valid_frequency:
            blockers.append(
                {
                    "fact": "clock.frequency",
                    "reason": f"Clock frequency {frequency.value} is not a positive integer.",
                    "resolution": "Provide the verified peripheral clock frequency in Hz.",
                }
            )

    version = facts.get("platform.version")
    if not version or not version.resolved:
        warnings.append("RT-Thread version was not proven from the project or user configuration.")
    elif not str(version.value).startswith("5."):
        warnings.append(f"RT-Thread {version.value} is outside the preferred MVP 5.x line.")
    if not _has_resolved(facts, ("build.system",)):
        warnings.append("Build system was not detected; configure commands.build before execution.")
    return blockers, warnings


def build_manifest(
    project: Path,
    request: str,
    facts: dict[str, Fact],
    blockers: list[dict[str, Any]],
    warnings: list[str],
) -> dict[str, Any]:
    verified = sum(fact.confidence == Confidence.VERIFIED for fact in facts.values())
    high = sum(fact.confidence == Confidence.HIGH for fact in facts.values())
    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "project": str(project.resolve()),
        "request": request,
        "status": Status.BLOCKED.value if blockers else Status.READY.value,
        "facts": {key: fact.to_dict() for key, fact in sorted(facts.items())},
        "fact_summary": {
            "verified": verified,
            "high_confidence": high,
            "other": len(facts) - verified - high,
            "unknown_critical": len(blockers),
        },
        "blockers": blockers,
        "warnings": warnings,
    }
