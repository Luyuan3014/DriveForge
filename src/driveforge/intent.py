from __future__ import annotations

import re
from dataclasses import dataclass


SUPPORTED_PERIPHERALS = ("GPIO", "UART", "SPI", "I2C", "CAN", "ADC", "PWM")


@dataclass(slots=True)
class DriverIntent:
    request: str
    peripheral: str | None = None
    instance: str | None = None
    operation: str = "implement"


def parse_request(request: str) -> DriverIntent:
    upper = request.upper()
    aliases = {
        "串口": "UART",
        "通用异步收发": "UART",
        "模数转换": "ADC",
        "脉宽调制": "PWM",
    }
    for alias, replacement in aliases.items():
        if alias in request and replacement not in upper:
            upper = f"{upper} {replacement}"

    peripheral: str | None = None
    instance: str | None = None
    for name in SUPPORTED_PERIPHERALS:
        match = re.search(rf"\b({name})[\s_.-]*(\d+)\b", upper)
        if match:
            peripheral = name
            instance = f"{name}{match.group(2)}"
            break
    if peripheral is None:
        for name in SUPPORTED_PERIPHERALS:
            if re.search(rf"\b{name}\b", upper):
                peripheral = name
                break

    operation = "implement"
    if any(word in request.lower() for word in ("verify", "验证", "测试")):
        operation = "verify"
    if any(word in request.lower() for word in ("repair", "fix", "修复", "诊断")):
        operation = "repair"
    if any(word in request.lower() for word in ("port", "adapt", "移植", "适配")):
        operation = "adapt"
    if any(word in request.lower() for word in ("add", "增加", "新增", "实现", "完成")):
        operation = "implement"

    return DriverIntent(
        request=request,
        peripheral=peripheral,
        instance=instance,
        operation=operation,
    )
