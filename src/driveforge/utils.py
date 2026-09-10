from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


IGNORED_DIRS = {
    ".git",
    ".driveforge",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "packages",
}

TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".cmake",
    ".conf",
    ".cpp",
    ".dts",
    ".dtsi",
    ".h",
    ".hpp",
    ".ini",
    ".ld",
    ".md",
    ".py",
    ".s",
    ".scons",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

TEXT_NAMES = {
    "CMakeLists.txt",
    "Kconfig",
    "Makefile",
    "SConscript",
    "SConstruct",
    "defconfig",
    "rtconfig.h",
    "rtconfig.py",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def relative_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def iter_text_files(
    root: Path,
    *,
    max_files: int = 5000,
    max_bytes: int = 2_000_000,
) -> Iterable[Path]:
    seen = 0
    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = sorted(
            name
            for name in dir_names
            if name not in IGNORED_DIRS and not name.startswith(".driveforge")
        )
        for name in sorted(file_names):
            path = Path(current_root) / name
            if name not in TEXT_NAMES and path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            yield path
            seen += 1
            if seen >= max_files:
                return


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def excerpt_at(text: str, offset: int, limit: int = 180) -> str:
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    if end < 0:
        end = len(text)
    return re.sub(r"\s+", " ", text[start:end]).strip()[:limit]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Configuration root must be an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def dump_yaml(value: Any, indent: int = 0) -> str:
    """Serialize the JSON-compatible subset of YAML without a runtime dependency."""
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines: list[str] = []
        for key, item in value.items():
            rendered_key = key if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", str(key)) else _yaml_scalar(key)
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{prefix}{rendered_key}:")
                lines.append(dump_yaml(item, indent + 2))
            else:
                rendered = dump_yaml(item, 0) if isinstance(item, (dict, list)) else _yaml_scalar(item)
                lines.append(f"{prefix}{rendered_key}: {rendered}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return "[]"
        lines = []
        for item in value:
            if isinstance(item, dict) and item:
                first_key = next(iter(item))
                first_value = item[first_key]
                rendered_key = first_key if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", str(first_key)) else _yaml_scalar(first_key)
                if isinstance(first_value, (dict, list)) and first_value:
                    lines.append(f"{prefix}- {rendered_key}:")
                    lines.append(dump_yaml(first_value, indent + 4))
                else:
                    rendered = dump_yaml(first_value, 0) if isinstance(first_value, (dict, list)) else _yaml_scalar(first_value)
                    lines.append(f"{prefix}- {rendered_key}: {rendered}")
                for key, child in list(item.items())[1:]:
                    rendered_key = key if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", str(key)) else _yaml_scalar(key)
                    if isinstance(child, (dict, list)) and child:
                        lines.append(f"{' ' * (indent + 2)}{rendered_key}:")
                        lines.append(dump_yaml(child, indent + 4))
                    else:
                        rendered = dump_yaml(child, 0) if isinstance(child, (dict, list)) else _yaml_scalar(child)
                        lines.append(f"{' ' * (indent + 2)}{rendered_key}: {rendered}")
            elif isinstance(item, list) and item:
                lines.append(f"{prefix}-")
                lines.append(dump_yaml(item, indent + 2))
            else:
                rendered = dump_yaml(item, 0) if isinstance(item, (dict, list)) else _yaml_scalar(item)
                lines.append(f"{prefix}- {rendered}")
        return "\n".join(lines)
    return f"{prefix}{_yaml_scalar(value)}"


def write_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(value) + "\n", encoding="utf-8")


def flatten_dict(value: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, child in value.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict):
            result.update(flatten_dict(child, full_key))
        else:
            result[full_key] = child
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_snapshot(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in iter_text_files(root):
        try:
            snapshot[relative_posix(path, root)] = sha256_file(path)
        except OSError:
            continue
    return snapshot


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
