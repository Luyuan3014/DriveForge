from __future__ import annotations

from dataclasses import dataclass, field
import difflib
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True, slots=True)
class PatchOperation:
    path: str
    replacements: dict[str, str] = field(default_factory=dict)
    required: tuple[str, ...] = ()


@dataclass(slots=True)
class PatchResult:
    diff: str
    files: list[str]
    applied: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"files": self.files, "applied": self.applied, "errors": self.errors, "diff": self.diff}


def _apply_replacements(text: str, replacements: dict[str, str]) -> tuple[str, list[str]]:
    result = text
    errors: list[str] = []
    for old, new in replacements.items():
        count = result.count(old)
        if count == 0:
            errors.append(f"replacement anchor not found: {old[:120]!r}")
            continue
        if count > 1:
            errors.append(f"replacement anchor is ambiguous ({count} matches): {old[:120]!r}")
            continue
        result = result.replace(old, new, 1)
    return result, errors


class AdaptFirstPatcher:
    """Produce a minimal, deterministic unified diff from verified anchors.

    The patcher never guesses a source location: every replacement must match
    exactly once (or the operation fails without touching the project).
    """

    def __init__(self, project: str | Path) -> None:
        self.project = Path(project).resolve()

    def preview(self, operations: Iterable[PatchOperation]) -> PatchResult:
        chunks: list[str] = []
        files: list[str] = []
        errors: list[str] = []
        for operation in operations:
            path = (self.project / operation.path).resolve()
            try:
                path.relative_to(self.project)
            except ValueError:
                errors.append(f"patch path escapes project: {operation.path}")
                continue
            if not path.is_file():
                errors.append(f"patch target does not exist: {operation.path}")
                continue
            original = path.read_text(encoding="utf-8", errors="replace")
            for required in operation.required:
                if required not in original:
                    errors.append(f"required anchor not found in {operation.path}: {required[:120]!r}")
            updated, replacement_errors = _apply_replacements(original, operation.replacements)
            errors.extend(f"{operation.path}: {error}" for error in replacement_errors)
            if updated == original:
                continue
            files.append(operation.path.replace("\\", "/"))
            chunks.extend(difflib.unified_diff(
                original.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=f"a/{operation.path.replace('\\', '/')}",
                tofile=f"b/{operation.path.replace('\\', '/')}",
                lineterm="\n",
            ))
        return PatchResult("".join(chunks), sorted(set(files)), False, errors)

    def apply(self, operations: Iterable[PatchOperation], *, patch_file: str | Path | None = None) -> PatchResult:
        operation_list = list(operations)
        result = self.preview(operation_list)
        if result.errors:
            return result
        for operation in operation_list:
            path = (self.project / operation.path).resolve()
            original = path.read_text(encoding="utf-8", errors="replace")
            updated, _ = _apply_replacements(original, operation.replacements)
            path.write_text(updated, encoding="utf-8", newline="")
        if patch_file is not None:
            destination = Path(patch_file)
            if not destination.is_absolute():
                destination = self.project / destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(result.diff, encoding="utf-8")
        result.applied = True
        return result


def operations_from_config(config: dict[str, object]) -> list[PatchOperation]:
    """Load explicit patch anchors from ``patch.operations`` config."""
    raw = config.get("patch", {})
    if not isinstance(raw, dict):
        return []
    operations: list[PatchOperation] = []
    for item in raw.get("operations", []) if isinstance(raw.get("operations", []), list) else []:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        replacements = item.get("replacements", {})
        required = item.get("required", [])
        operations.append(PatchOperation(
            path=item["path"],
            replacements={str(k): str(v) for k, v in replacements.items()} if isinstance(replacements, dict) else {},
            required=tuple(str(value) for value in required) if isinstance(required, list) else (),
        ))
    return operations


def render_patch_file(project: str | Path, operations: Iterable[PatchOperation], output: str | Path) -> PatchResult:
    result = AdaptFirstPatcher(project).preview(operations)
    destination = Path(output)
    if not destination.is_absolute():
        destination = Path(project) / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result.diff, encoding="utf-8")
    return result
