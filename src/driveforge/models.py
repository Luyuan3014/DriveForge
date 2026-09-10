from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

__version__ = "0.1.0"


class Confidence(str, Enum):
    VERIFIED = "VERIFIED"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class Status(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    PLANNED = "PLANNED"
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


@dataclass(slots=True)
class Evidence:
    path: str
    line: int | None = None
    excerpt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(slots=True)
class Fact:
    key: str
    value: Any = None
    confidence: Confidence = Confidence.UNKNOWN
    source: str = "unresolved"
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def resolved(self) -> bool:
        return self.value is not None and self.confidence not in {
            Confidence.LOW,
            Confidence.UNKNOWN,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "confidence": self.confidence.value,
            "source": self.source,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(slots=True)
class DriverCandidate:
    peripheral: str
    path: str
    instances: list[str] = field(default_factory=list)
    origin: str = "project"
    score: int = 0
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "peripheral": self.peripheral,
            "path": self.path,
            "instances": self.instances,
            "origin": self.origin,
            "score": self.score,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(slots=True)
class ScanResult:
    project: str
    files_scanned: int
    facts: dict[str, Fact]
    driver_candidates: list[DriverCandidate]
    inventory: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "files_scanned": self.files_scanned,
            "facts": {key: fact.to_dict() for key, fact in sorted(self.facts.items())},
            "driver_candidates": [item.to_dict() for item in self.driver_candidates],
            "inventory": self.inventory,
            "warnings": self.warnings,
        }


@dataclass(slots=True)
class CommandResult:
    phase: str
    status: Status
    command: str | None = None
    exit_code: int | None = None
    duration_seconds: float = 0.0
    log: str | None = None
    attempt: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            key: (value.value if isinstance(value, Enum) else value)
            for key, value in asdict(self).items()
            if value is not None
        }
