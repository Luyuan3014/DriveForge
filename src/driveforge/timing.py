from __future__ import annotations

from dataclasses import asdict, dataclass
from math import inf
from typing import Any


@dataclass(frozen=True, slots=True)
class TimingSolution:
    peripheral: str
    clock_hz: int
    requested_rate: int
    actual_rate: float
    error_ratio: float
    sample_point: float | None = None
    prescaler: int | None = None
    bs1: int | None = None
    bs2: int | None = None
    sjw: int | None = None
    oversampling: int | None = None
    divider: float | None = None
    sck_hz: int | None = None
    safe: bool = False
    constraints: dict[str, Any] | None = None

    @property
    def error_percent(self) -> float:
        return self.error_ratio * 100.0

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["error_percent"] = round(self.error_percent, 6)
        return value


def solve_can_bittiming(
    clock_hz: int,
    bitrate: int,
    *,
    sample_point: float | None = None,
    prescaler_range: tuple[int, int] = (1, 1024),
    bs1_range: tuple[int, int] = (1, 16),
    bs2_range: tuple[int, int] = (1, 8),
    sjw_range: tuple[int, int] = (1, 4),
    max_error: float = 0.005,
) -> TimingSolution:
    """Find CAN nominal bit timing by exhaustive integer search.

    ``sample_point`` is a fraction (0.80 means 80%). The default scores the
    industrial 80--87.5% window and then minimizes rate error and oscillator
    tolerance sensitivity. A ValueError is raised for impossible inputs.
    """
    if clock_hz <= 0 or bitrate <= 0:
        raise ValueError("clock_hz and bitrate must be positive")
    requested_sp = 0.8333333333 if sample_point is None else sample_point
    if not 0.5 <= requested_sp < 1.0:
        raise ValueError("sample_point must be between 0.5 and 1.0")
    best: tuple[tuple[float, ...], TimingSolution] | None = None
    for prescaler in range(prescaler_range[0], prescaler_range[1] + 1):
        for bs1 in range(bs1_range[0], bs1_range[1] + 1):
            for bs2 in range(bs2_range[0], bs2_range[1] + 1):
                tq = 1 + bs1 + bs2
                actual = clock_hz / (prescaler * tq)
                error = abs(actual - bitrate) / bitrate
                sp = (1 + bs1) / tq
                industrial_penalty = 0.0 if 0.80 <= sp <= 0.875 else 1.0
                score = (industrial_penalty, error, abs(sp - requested_sp), -tq, prescaler)
                candidate = TimingSolution(
                    peripheral="CAN",
                    clock_hz=clock_hz,
                    requested_rate=bitrate,
                    actual_rate=actual,
                    error_ratio=error,
                    sample_point=sp,
                    prescaler=prescaler,
                    bs1=bs1,
                    bs2=bs2,
                    sjw=sjw_range[0] if sjw_range[0] <= bs2 else bs2,
                    safe=error <= max_error,
                    constraints={"sample_point_min": 0.80, "sample_point_max": 0.875, "max_error": max_error},
                )
                if best is None or score < best[0]:
                    best = (score, candidate)
    if best is None or best[1].error_ratio > max_error:
        raise ValueError(f"no CAN timing solution within {max_error * 100:.3g}% error")
    return best[1]


def solve_uart_baudrate(
    clock_hz: int,
    baudrate: int,
    *,
    oversampling: int | None = None,
    max_error: float = 0.015,
) -> TimingSolution:
    """Solve UART integer/fractional divider for oversampling 8 or 16."""
    if clock_hz <= 0 or baudrate <= 0:
        raise ValueError("clock_hz and baudrate must be positive")
    modes = (oversampling,) if oversampling else (16, 8)
    best: tuple[tuple[float, ...], TimingSolution] | None = None
    for mode in modes:
        if mode not in (8, 16):
            raise ValueError("UART oversampling must be 8 or 16")
        divider = clock_hz / (mode * baudrate)
        if divider <= 0:
            continue
        # Hardware usually stores a fixed point divider.  4 fractional bits
        # cover STM32/GD32 style BRR registers and remain deterministic.
        rounded = round(divider * 16) / 16
        actual = clock_hz / (mode * rounded)
        error = abs(actual - baudrate) / baudrate
        candidate = TimingSolution(
            peripheral="UART",
            clock_hz=clock_hz,
            requested_rate=baudrate,
            actual_rate=actual,
            error_ratio=error,
            oversampling=mode,
            divider=rounded,
            safe=error <= max_error,
            constraints={"max_error": max_error},
        )
        score = (error, 0 if mode == 16 else 1, abs(rounded - divider))
        if best is None or score < best[0]:
            best = (score, candidate)
    if best is None or best[1].error_ratio > max_error:
        raise ValueError(f"no UART timing solution within {max_error * 100:.3g}% error")
    return best[1]


def solve_spi_clock(
    clock_hz: int,
    max_sck_hz: int,
    *,
    divisors: tuple[int, ...] = (2, 4, 8, 16, 32, 64, 128, 256),
) -> TimingSolution:
    """Choose the fastest supported SPI divider that does not exceed max_sck."""
    if clock_hz <= 0 or max_sck_hz <= 0:
        raise ValueError("clock_hz and max_sck_hz must be positive")
    valid = [(divisor, clock_hz // divisor) for divisor in divisors if clock_hz // divisor <= max_sck_hz]
    if not valid:
        raise ValueError("no SPI divider can satisfy max_sck_hz")
    divisor, actual = max(valid, key=lambda item: item[1])
    return TimingSolution(
        peripheral="SPI",
        clock_hz=clock_hz,
        requested_rate=max_sck_hz,
        actual_rate=float(actual),
        error_ratio=abs(actual - max_sck_hz) / max_sck_hz,
        divider=float(divisor),
        sck_hz=actual,
        safe=True,
        constraints={"max_sck_hz": max_sck_hz, "divisors": list(divisors)},
    )


# Short aliases used by integrations.
solve_can = solve_can_bittiming
solve_uart = solve_uart_baudrate
solve_spi = solve_spi_clock

