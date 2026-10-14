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
_TIMEOUT = re.compile(r"timeout|deadline|tick|elapsed|retry|for\s*\(", re.I)


def _mask_comments_and_strings(text: str) -> str:
    """Mask C comments and literals while preserving offsets and newlines."""
    pattern = re.compile(r"/\*.*?\*/|//[^\n]*|(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')", re.S)
    return pattern.sub(lambda match: "".join("\n" if char == "\n" else " " for char in match.group(0)), text)


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int | None:
    if start >= len(text) or text[start] != opening:
        return None
    depth = 0
    for index in range(start, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    return None


def find_unbounded_waits(path: str | Path, text: str | None = None) -> list[TimeoutFinding]:
    source = Path(path)
    content = source.read_text(encoding="utf-8", errors="replace") if text is None else text
    masked = _mask_comments_and_strings(content)
    findings: list[TimeoutFinding] = []
    for match in re.finditer(r"\bwhile\b\s*\(", masked, re.I):
        open_paren = masked.find("(", match.start())
        close_paren = _balanced_end(masked, open_paren, "(", ")")
        if close_paren is None:
            continue
        condition = masked[open_paren + 1:close_paren]
        if not any(token in condition.upper() for token in ("STAT", "STATUS", "FLAG", "READY", "BUSY", "TX", "RX", "ERR")):
            continue
        body_start = close_paren + 1
        while body_start < len(masked) and masked[body_start].isspace():
            body_start += 1
        body_end = body_start
        if body_start < len(masked) and masked[body_start] == "{":
            body_end = _balanced_end(masked, body_start, "{", "}") or len(masked)
        else:
            body_end = masked.find(";", body_start)
            body_end = len(masked) if body_end < 0 else body_end + 1
        body = masked[body_start:body_end]
        if _TIMEOUT.search(condition) or _TIMEOUT.search(body):
            continue
        line = content.count("\n", 0, match.start()) + 1
        original_line = content.splitlines()[line - 1].strip() if content.splitlines() else ""
        findings.append(TimeoutFinding(source.as_posix(), line, original_line))
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

