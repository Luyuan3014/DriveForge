from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .utils import flatten_dict, load_json


DEFAULT_CONFIG: dict[str, Any] = {
    "request": "",
    "hardware": {},
    "commands": {
        "patch": None,
        "build": None,
        "flash": None,
        "test": None,
        "repair": None,
    },
    "timeouts": {"build": 600, "flash": 180, "test": 180, "repair": 600},
    "max_repair_attempts": 2,
}


def _deep_merge(target: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def load_config(path: Path | None) -> dict[str, Any]:
    config = deepcopy(DEFAULT_CONFIG)
    if path is not None:
        _deep_merge(config, load_json(path))
    return config


def set_dotted(config: dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".")
    node = config
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def hardware_overrides(config: dict[str, Any]) -> dict[str, Any]:
    hardware = config.get("hardware", {})
    if not isinstance(hardware, dict):
        raise ValueError("hardware configuration must be an object")
    return flatten_dict(hardware)
