from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .intent import DriverIntent, SUPPORTED_PERIPHERALS
from .models import Confidence, DriverCandidate, Evidence, Fact, ScanResult
from .utils import excerpt_at, iter_text_files, line_number, read_text, relative_posix


class ProjectAnalyzer:
    """Collect project facts without inferring undocumented hardware values."""

    def __init__(self, project: Path, intent: DriverIntent | None = None) -> None:
        self.project = project.resolve()
        self.intent = intent or DriverIntent(request="")
        self._documents: list[tuple[Path, str, str]] = []

    def analyze(self) -> ScanResult:
        warnings: list[str] = []
        for path in iter_text_files(self.project):
            try:
                self._documents.append((path, relative_posix(path, self.project), read_text(path)))
            except OSError as exc:
                warnings.append(f"Could not read {relative_posix(path, self.project)}: {exc}")

        facts: dict[str, Fact] = {}
        facts.update(self._detect_platform())
        facts.update(self._detect_mcu())
        facts.update(self._detect_build())
        facts.update(self._detect_debug_probe())
        if self.intent.instance:
            facts.update(self._detect_target_hardware(self.intent.instance))

        candidates = self._detect_driver_candidates()
        if len(self._documents) >= 5000:
            warnings.append("Project scan stopped at the 5000-file safety limit.")
        return ScanResult(
            project=str(self.project),
            files_scanned=len(self._documents),
            facts=facts,
            driver_candidates=candidates,
            inventory=self._detect_inventory(),
            warnings=warnings,
        )

    def _evidence(self, rel: str, text: str, match: re.Match[str]) -> Evidence:
        return Evidence(
            path=rel,
            line=line_number(text, match.start()),
            excerpt=excerpt_at(text, match.start()),
        )

    def _first_match(self, pattern: str, flags: int = re.IGNORECASE) -> tuple[str, Evidence] | None:
        compiled = re.compile(pattern, flags)
        for _, rel, text in self._documents:
            match = compiled.search(text)
            if match:
                return match.group(1), self._evidence(rel, text, match)
        return None

    def _detect_platform(self) -> dict[str, Fact]:
        evidence: list[Evidence] = []
        for _, rel, text in self._documents:
            match = re.search(r"\bRT_(?:THREAD|VERSION|USING_[A-Z0-9_]+)\b|#\s*include\s*[<\"]rtthread\.h", text)
            if match:
                evidence.append(self._evidence(rel, text, match))
                if len(evidence) >= 5:
                    break
        facts: dict[str, Fact] = {}
        if evidence:
            facts["platform.os"] = Fact(
                key="platform.os",
                value="rt-thread",
                confidence=Confidence.VERIFIED,
                source="project",
                evidence=evidence,
            )

        version_parts: dict[str, tuple[str, Evidence]] = {}
        version_patterns = {
            "major": r"^\s*#\s*define\s+RT_VERSION\s+(\d+)",
            "minor": r"^\s*#\s*define\s+RT_SUBVERSION\s+(\d+)",
            "patch": r"^\s*#\s*define\s+RT_REVISION\s+(\d+)",
        }
        for name, pattern in version_patterns.items():
            found = self._first_match(pattern, re.MULTILINE)
            if found:
                version_parts[name] = found
        if "major" in version_parts:
            value = ".".join(
                version_parts.get(part, ("0", Evidence(path="")))[0]
                for part in ("major", "minor", "patch")
            )
            facts["platform.version"] = Fact(
                key="platform.version",
                value=value,
                confidence=Confidence.VERIFIED,
                source="project:rtdef.h",
                evidence=[item[1] for item in version_parts.values()],
            )
        return facts

    def _detect_mcu(self) -> dict[str, Fact]:
        token_pattern = re.compile(r"\b(?:GD32F4[0-9A-Z]{2,}|STM32F4[0-9A-Z]{2,})\b", re.IGNORECASE)
        counts: Counter[str] = Counter()
        evidence_by_token: dict[str, list[Evidence]] = {}
        for _, rel, text in self._documents:
            search_text = f"{rel}\n{text}"
            for match in token_pattern.finditer(search_text):
                token = match.group(0).upper().rstrip("_X")
                if token in {"GD32F4XX", "STM32F4XX", "GD32F4X", "STM32F4X"}:
                    continue
                counts[token] += 1
                if len(evidence_by_token.setdefault(token, [])) < 4:
                    if match.start() < len(rel) + 1:
                        evidence_by_token[token].append(Evidence(path=rel, excerpt=rel))
                    else:
                        text_offset = match.start() - len(rel) - 1
                        adjusted = token_pattern.search(text, max(0, text_offset))
                        if adjusted:
                            item = self._evidence(rel, text, adjusted)
                            if not any(
                                existing.path == item.path and existing.line == item.line
                                for existing in evidence_by_token[token]
                            ):
                                evidence_by_token[token].append(item)
        if not counts:
            return {}
        model = sorted(counts, key=lambda item: (counts[item], len(item), item), reverse=True)[0]
        if model.startswith("GD32"):
            vendor = "GigaDevice"
            family_match = re.match(r"(GD32F4)", model)
        else:
            vendor = "STMicroelectronics"
            family_match = re.match(r"(STM32F4)", model)
        family = family_match.group(1) if family_match else model[:6]
        evidence = evidence_by_token[model]
        return {
            "mcu.vendor": Fact("mcu.vendor", vendor, Confidence.HIGH, "project:model", evidence),
            "mcu.family": Fact("mcu.family", family, Confidence.HIGH, "project:model", evidence),
            "mcu.model": Fact("mcu.model", model, Confidence.VERIFIED, "project", evidence),
        }

    def _detect_build(self) -> dict[str, Fact]:
        markers = (
            ("SConstruct", "scons"),
            ("CMakeLists.txt", "cmake"),
            ("west.yml", "west"),
            ("Makefile", "make"),
        )
        facts: dict[str, Fact] = {}
        for marker, system in markers:
            path = self.project / marker
            if path.exists():
                facts["build.system"] = Fact(
                    "build.system",
                    system,
                    Confidence.VERIFIED,
                    "project:file",
                    [Evidence(path=marker, excerpt=f"Detected {marker}")],
                )
                break
        compiler_patterns = (
            (r"\barm-none-eabi-gcc\b", "arm-none-eabi-gcc"),
            (r"\barmclang\b", "armclang"),
            (r"\b(?:iccarm|IAR)\b", "iar"),
        )
        for pattern, name in compiler_patterns:
            found = self._first_match(f"({pattern})")
            if found:
                facts["build.compiler"] = Fact(
                    "build.compiler", name, Confidence.VERIFIED, "project", [found[1]]
                )
                break
        return facts

    def _detect_debug_probe(self) -> dict[str, Fact]:
        probes = ((r"\bJ-?Link\b", "J-Link"), (r"\bST-?Link\b", "ST-Link"), (r"\bpyOCD\b", "pyOCD"))
        for pattern, name in probes:
            found = self._first_match(f"({pattern})")
            if found:
                return {
                    "debug.probe": Fact(
                        "debug.probe", name, Confidence.HIGH, "project", [found[1]]
                    )
                }
        return {}

    @staticmethod
    def _normalize_pin(value: str) -> str | None:
        match = re.fullmatch(r"P?([A-K])[._-]?(\d{1,2})", value.strip(), re.IGNORECASE)
        return f"P{match.group(1).upper()}{int(match.group(2))}" if match else None

    def _detect_signal_pin(self, instance: str, signal: str) -> Fact | None:
        macro = rf"(?:BSP_)?{re.escape(instance)}_{signal}_PIN"
        direct_patterns = (
            rf"{macro}\s+(?:\"|')?(P[A-K][._-]?\d{{1,2}})",
            rf"{macro}\s+GET_PIN\s*\(\s*([A-K])\s*,\s*(\d{{1,2}})\s*\)",
        )
        for _, rel, text in self._documents:
            match = re.search(direct_patterns[0], text, re.IGNORECASE)
            if match:
                value = self._normalize_pin(match.group(1))
                if value:
                    return Fact(
                        f"pins.{signal.lower()}", value, Confidence.VERIFIED, "project:board_config", [self._evidence(rel, text, match)]
                    )
            match = re.search(direct_patterns[1], text, re.IGNORECASE)
            if match:
                value = f"P{match.group(1).upper()}{int(match.group(2))}"
                return Fact(
                    f"pins.{signal.lower()}", value, Confidence.VERIFIED, "project:board_config", [self._evidence(rel, text, match)]
                )

            pin_match = re.search(rf"{macro}\s+GPIO_PIN_(\d{{1,2}})", text, re.IGNORECASE)
            port_match = re.search(
                rf"(?:BSP_)?{re.escape(instance)}_{signal}_(?:GPIO_)?PORT\s+GPIO([A-K])",
                text,
                re.IGNORECASE,
            )
            if pin_match and port_match:
                value = f"P{port_match.group(1).upper()}{int(pin_match.group(1))}"
                return Fact(
                    f"pins.{signal.lower()}",
                    value,
                    Confidence.VERIFIED,
                    "project:board_config",
                    [self._evidence(rel, text, pin_match), self._evidence(rel, text, port_match)],
                )
        return None

    def _detect_target_hardware(self, instance: str) -> dict[str, Fact]:
        facts: dict[str, Fact] = {}
        signals_by_peripheral = {
            "GPIO": ("PIN",),
            "UART": ("RX", "TX"),
            "SPI": ("SCK", "MISO", "MOSI"),
            "I2C": ("SCL", "SDA"),
            "CAN": ("RX", "TX"),
            "ADC": ("PIN",),
            "PWM": ("PIN",),
        }
        peripheral = re.sub(r"\d+$", "", instance)
        for signal in signals_by_peripheral.get(peripheral, ()):
            fact = self._detect_signal_pin(instance, signal)
            if fact:
                facts[fact.key] = fact

        irq_pattern = rf"\b({re.escape(instance)}(?:_[A-Z0-9]+)?_IRQn)\b"
        found = self._first_match(irq_pattern)
        if found:
            facts["interrupt.irq"] = Fact(
                "interrupt.irq", found[0], Confidence.VERIFIED, "project:cmsis_or_board", [found[1]]
            )

        clock_pattern = rf"\b((?:RCU|RCC)_[A-Z0-9_]*{re.escape(instance)}[A-Z0-9_]*)\b"
        found = self._first_match(clock_pattern)
        if found:
            facts["clock.gate"] = Fact(
                "clock.gate", found[0], Confidence.VERIFIED, "project:sdk", [found[1]]
            )

        channel_pattern = rf"(?:BSP_)?{re.escape(instance)}_CHANNEL\s+([A-Z0-9_]+)"
        found = self._first_match(channel_pattern)
        if found:
            facts["target.channel"] = Fact(
                "target.channel", found[0], Confidence.VERIFIED, "project:board_config", [found[1]]
            )
        return facts

    def _origin(self, rel: str) -> str:
        lower = rel.lower()
        if any(part in lower for part in ("firmware", "libraries", "vendor", "sdk")):
            return "vendor_sdk"
        if "bsp" in lower:
            return "rtos_bsp"
        return "project"

    def _detect_inventory(self) -> dict[str, list[str]]:
        buckets: dict[str, set[str]] = {
            "bsp": set(),
            "vendor_sdk": set(),
            "hal": set(),
            "startup": set(),
            "linker_scripts": set(),
            "driver_directories": set(),
            "board_configuration": set(),
            "kconfig": set(),
            "scons": set(),
            "cmake": set(),
            "device_tree": set(),
        }
        for path, rel, _ in self._documents:
            lower = rel.lower()
            name = path.name.lower()
            parent = Path(rel).parent.as_posix()
            if "/bsp/" in f"/{lower}/" or lower.startswith("bsp/"):
                buckets["bsp"].add(parent)
            if any(part in lower for part in ("firmware", "libraries", "vendor", "/sdk/")):
                buckets["vendor_sdk"].add(parent)
            if re.search(r"(?:^|/)(?:stm32f4xx_hal|gd32f4xx)[_/]", lower) or "_hal_" in name:
                buckets["hal"].add(parent)
            if name.startswith("startup") and path.suffix.lower() in {".s", ".c"}:
                buckets["startup"].add(rel)
            if path.suffix.lower() in {".ld", ".icf", ".sct"}:
                buckets["linker_scripts"].add(rel)
            if re.match(r"(?:drv_|board)", name) and path.suffix.lower() in {".c", ".h", ".cpp", ".hpp"}:
                buckets["driver_directories"].add(parent)
            if name in {"board.c", "board.h", "rtconfig.h", "defconfig"} or path.suffix.lower() in {".dts", ".dtsi"}:
                buckets["board_configuration"].add(rel)
            if name == "kconfig" or name.endswith("kconfig"):
                buckets["kconfig"].add(rel)
            if name in {"sconstruct", "sconscript"}:
                buckets["scons"].add(rel)
            if name == "cmakelists.txt" or path.suffix.lower() == ".cmake":
                buckets["cmake"].add(rel)
            if path.suffix.lower() in {".dts", ".dtsi"}:
                buckets["device_tree"].add(rel)
        return {key: sorted(values)[:100] for key, values in buckets.items()}

    def _detect_driver_candidates(self) -> list[DriverCandidate]:
        candidates: list[DriverCandidate] = []
        target = self.intent.peripheral
        for path, rel, text in self._documents:
            if path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".xml"}:
                continue
            lower_name = path.name.lower()
            for peripheral in SUPPORTED_PERIPHERALS:
                if target and peripheral != target:
                    continue
                token = peripheral.lower()
                filename_hit = token in lower_name or (peripheral == "UART" and "serial" in lower_name)
                matches = list(re.finditer(rf"\b{peripheral}\d+\b", text, re.IGNORECASE))
                framework_hit = bool(re.search(rf"\bRT_USING_{peripheral}\b|\brt_hw_{token}_init\b", text, re.IGNORECASE))
                if not filename_hit and not matches and not framework_hit:
                    continue
                instances = sorted({match.group(0).upper() for match in matches})
                origin = self._origin(rel)
                origin_score = {"project": 30, "rtos_bsp": 20, "vendor_sdk": 10}[origin]
                score = origin_score + (25 if filename_hit else 0) + (15 if framework_hit else 0) + min(len(matches), 20)
                evidence = [self._evidence(rel, text, match) for match in matches[:3]]
                if not evidence:
                    evidence = [Evidence(path=rel, excerpt=path.name)]
                candidates.append(
                    DriverCandidate(
                        peripheral=peripheral,
                        path=rel,
                        instances=instances,
                        origin=origin,
                        score=score,
                        evidence=evidence,
                    )
                )
        return sorted(candidates, key=lambda item: (-item.score, item.path))[:50]
