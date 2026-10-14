from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from typing import Any


@dataclass(frozen=True, slots=True)
class SVDField:
    name: str
    bit_offset: int
    bit_width: int
    description: str | None = None

    @property
    def mask(self) -> int:
        return ((1 << self.bit_width) - 1) << self.bit_offset


@dataclass(frozen=True, slots=True)
class SVDRegister:
    name: str
    address_offset: int
    size: int | None = None
    access: str | None = None
    reset_value: int | None = None
    description: str | None = None
    fields: tuple[SVDField, ...] = ()


@dataclass(frozen=True, slots=True)
class SVDInterrupt:
    name: str
    value: int
    description: str | None = None


@dataclass(frozen=True, slots=True)
class SVDPeripheral:
    name: str
    base_address: int
    group_name: str | None = None
    description: str | None = None
    registers: tuple[SVDRegister, ...] = ()
    interrupts: tuple[SVDInterrupt, ...] = ()

    def register(self, name: str) -> SVDRegister | None:
        wanted = name.upper()
        return next((item for item in self.registers if item.name.upper() == wanted), None)


@dataclass(frozen=True, slots=True)
class SVDDevice:
    name: str
    vendor: str | None = None
    version: str | None = None
    cpu_name: str | None = None
    address_unit_bits: int = 8
    peripherals: tuple[SVDPeripheral, ...] = ()

    def peripheral(self, name: str) -> SVDPeripheral | None:
        wanted = name.upper()
        return next((item for item in self.peripherals if item.name.upper() == wanted), None)

    def fact_index(self) -> dict[str, Any]:
        """Return deterministic hardware facts suitable for a manifest or resolver."""
        facts: dict[str, Any] = {"svd.device": self.name}
        if self.vendor:
            facts["svd.vendor"] = self.vendor
        if self.cpu_name:
            facts["svd.cpu"] = self.cpu_name
        facts["svd.address_unit_bits"] = self.address_unit_bits
        for peripheral in self.peripherals:
            prefix = peripheral.name.lower()
            facts[f"svd.{prefix}.base_address"] = peripheral.base_address
            if peripheral.group_name:
                facts[f"svd.{prefix}.group"] = peripheral.group_name
            if peripheral.interrupts:
                facts[f"svd.{prefix}.interrupts"] = {
                    irq.name: irq.value for irq in peripheral.interrupts
                }
            facts[f"svd.{prefix}.registers"] = {
                register.name: {
                    "offset": register.address_offset,
                    "address": peripheral.base_address + register.address_offset,
                    "size": register.size,
                    "access": register.access,
                    "reset": register.reset_value,
                    "fields": {
                        field.name: {"offset": field.bit_offset, "width": field.bit_width, "mask": field.mask}
                        for field in register.fields
                    },
                }
                for register in peripheral.registers
            }
        return facts


def _text(node: ET.Element | None) -> str | None:
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value or None


def _number(value: str | None, default: int | None = None) -> int | None:
    if value is None:
        return default
    raw = value.strip().replace("'", "")
    try:
        return int(raw, 0)
    except ValueError:
        try:
            return int(raw, 16)
        except ValueError:
            return default


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element.iter() if _tag(child) == name]


def _direct_children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if _tag(child) == name]


def _first(element: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in element.iter() if _tag(child) == name), None)


def _parse_field(node: ET.Element) -> SVDField:
    bit_offset = _number(_text(_first(node, "bitOffset")))
    bit_width = _number(_text(_first(node, "bitWidth")))
    if bit_offset is None or bit_width is None:
        lsb = _text(_first(node, "lsb"))
        msb = _text(_first(node, "msb"))
        if lsb is not None and msb is not None:
            bit_offset, bit_width = int(lsb, 0), int(msb, 0) - int(lsb, 0) + 1
        else:
            bit_range = _text(_first(node, "bitRange")) or "[0:0]"
            match = re.fullmatch(r"\[(\d+)\s*:\s*(\d+)\]", bit_range)
            if not match:
                raise ValueError(f"SVD field {_text(_first(node, 'name'))!r} has no bit range")
            msb, lsb = int(match.group(1)), int(match.group(2))
            bit_offset, bit_width = lsb, msb - lsb + 1
    return SVDField(
        name=_text(_first(node, "name")) or "UNNAMED",
        bit_offset=bit_offset,
        bit_width=bit_width,
        description=_text(_first(node, "description")),
    )


def _expand_indices(raw: str | None, count: int) -> list[str]:
    if not raw:
        return [str(index) for index in range(count)]
    values: list[str] = []
    for item in raw.split(","):
        item = item.strip()
        if "-" in item:
            start, end = (part.strip() for part in item.split("-", 1))
            try:
                values.extend(str(index) for index in range(int(start, 0), int(end, 0) + 1))
            except ValueError:
                values.append(item)
        elif item:
            values.append(item)
    return values or [str(index) for index in range(count)]


def _parse_register(node: ET.Element) -> list[SVDRegister]:
    """Parse one register, including the standard CMSIS-SVD ``dim`` form."""
    reg_name = _text(_first(node, "name"))
    offset = _number(_text(_first(node, "addressOffset")))
    if not reg_name or offset is None:
        return []
    count = _number(_text(_first(node, "dim")), 1) or 1
    increment = _number(_text(_first(node, "dimIncrement")), 0) or 0
    names = _expand_indices(_text(_first(node, "dimIndex")), count)
    fields_node = _first(node, "fields")
    fields: list[SVDField] = []
    if fields_node is not None:
        for field in _direct_children(fields_node, "field"):
            try:
                fields.append(_parse_field(field))
            except ValueError:
                continue
    parsed: list[SVDRegister] = []
    for index in range(count):
        suffix = names[index] if index < len(names) else str(index)
        expanded_name = reg_name.replace("%s", suffix) if "%s" in reg_name else (f"{reg_name}{suffix}" if count > 1 else reg_name)
        parsed.append(SVDRegister(
            name=expanded_name,
            address_offset=offset + (index * increment),
            size=_number(_text(_first(node, "size"))),
            access=_text(_first(node, "access")),
            reset_value=_number(_text(_first(node, "resetValue"))),
            description=_text(_first(node, "description")),
            fields=tuple(fields),
        ))
    return parsed


def parse_svd(path: str | Path) -> SVDDevice:
    """Parse a CMSIS-SVD XML file using only the standard library.

    Derived addresses are kept as integers and expanded registers are represented
    explicitly so downstream planning never needs to infer a register location.
    """
    source = Path(path)
    root = ET.parse(source).getroot()
    device_node = root if _tag(root) == "device" else _first(root, "device")
    if device_node is None:
        raise ValueError(f"{source} is not a CMSIS-SVD document: missing <device>")
    peripherals_node = _first(device_node, "peripherals")
    peripherals: list[SVDPeripheral] = []
    for node in ([] if peripherals_node is None else [item for item in list(peripherals_node) if _tag(item) == "peripheral"]):
        name = _text(_first(node, "name"))
        base = _number(_text(_first(node, "baseAddress")))
        if not name or base is None:
            continue
        registers_node = _first(node, "registers")
        registers: list[SVDRegister] = []
        if registers_node is not None:
            for reg in _direct_children(registers_node, "register"):
                registers.extend(_parse_register(reg))
        interrupts = tuple(
            SVDInterrupt(
                name=_text(_first(item, "name")) or "UNNAMED",
                value=_number(_text(_first(item, "value")), 0) or 0,
                description=_text(_first(item, "description")),
            )
            for item in _direct_children(node, "interrupt")
            if _text(_first(item, "name"))
        )
        peripherals.append(SVDPeripheral(
            name=name,
            base_address=base,
            group_name=_text(_first(node, "groupName")),
            description=_text(_first(node, "description")),
            registers=tuple(registers),
            interrupts=interrupts,
        ))
    cpu = _first(device_node, "cpu")
    return SVDDevice(
        name=_text(_first(device_node, "name")) or source.stem,
        vendor=_text(_first(device_node, "vendor")),
        version=_text(_first(device_node, "version")),
        cpu_name=_text(_first(cpu, "name")) if cpu is not None else None,
        address_unit_bits=_number(_text(_first(device_node, "addressUnitBits")), 8) or 8,
        peripherals=tuple(peripherals),
    )


load_svd = parse_svd
