from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TimeoutFinding:
    path: str
    line: int
    statement: str
    reason: str = "hardware wait loop has no bounded timeout"

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "line": self.line, "statement": self.statement, "reason": self.reason}


# Conservative patterns: only loops whose condition reads a likely peripheral
# status symbol are reported. Generic application loops are left alone.
_WAIT = re.compile(r"while\s*\(\s*!?\s*\(?\s*([A-Za-z_]\w*(?:->|\.|_)[A-Za-z0-9_]+|[A-Z][A-Z0-9_]*(?:\s*&\s*[A-Z][A-Z0-9_]*)?)\s*\)?\s*\)")
_TIMEOUT = re.compile(r"timeout|deadline|tick|elapsed|retry|for\s*\(", re.I)


def find_unbounded_waits(path: str | Path, text: str | None = None) -> list[TimeoutFinding]:
    source = Path(path)
    content = source.read_text(encoding="utf-8", errors="replace") if text is None else text
    findings: list[TimeoutFinding] = []
    lines = content.splitlines()
    for index, line in enumerate(lines, 1):
        match = _WAIT.search(line)
        if not match or _TIMEOUT.search(line):
            continue
        signal = match.group(1)
        if any(token in signal.upper() for token in ("STAT", "STATUS", "FLAG", "READY", "BUSY", "TX", "RX", "ERR")):
            findings.append(TimeoutFinding(source.as_posix(), index, line.strip()))
    return findings


def add_timeout_guard(loop: str, *, timeout_name: str = "timeout", timeout_value: str = "DRIVER_TIMEOUT_TICKS") -> str:
    """Wrap a single-line wait loop with a caller-owned timeout counter."""
    match = re.fullmatch(r"\s*while\s*\((?P<condition>.*)\)\s*;\s*", loop)
    if not match:
        raise ValueError("loop must be a single-line while(condition); statement")
    condition = match.group("condition").strip()
    return (
        f"uint32_t {timeout_name} = {timeout_value};\n"
        f"while ({condition} && ({timeout_name} > 0U)) {{\n"
        f"    --{timeout_name};\n"
        "}\n"
        f"if ({timeout_name} == 0U) {{\n"
        "    return -ETIMEDOUT;\n"
        "}"
    )

