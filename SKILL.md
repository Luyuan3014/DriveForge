---
name: driveforge
description: Implement, adapt, build, flash, diagnose, and verify RT-Thread peripheral drivers on supported GD32F4 or STM32F4 targets using traceable hardware facts. Use for GPIO, UART, SPI, I2C, CAN, ADC, or PWM driver work where a real embedded project is available; do not use for Linux drivers or unsupported SoCs.
---

# DriveForge

Turn an RT-Thread driver request into the smallest reviewable patch and an evidence-backed verification report.

## Establish facts before editing

Run `python tools/driveforge.py plan <project> --request <requirement>` from this skill checkout. Add only user-provided values through flags, a JSON config, or `--set hardware.<fact>=<value>`.

Read `<project>/.driveforge/hardware_manifest.yaml` and `driver_plan.yaml`. Treat project files, board configuration, vendor SDK, CMSIS, schematics supplied by the user, and official manuals as evidence. Never fill a missing pin, PinMux, clock, IRQ, DMA, register, voltage, address, or instance from model memory.

If the manifest is `BLOCKED`, continue read-only investigation when another in-scope project source can resolve the facts. Otherwise stop code changes and report the exact missing facts.

## Engineer adapt-first

Search in this order: current project instance, same MCU family, official BSP, vendor SDK, RT-Thread driver, then a new implementation. Compare the reference and target instance for GPIO/AF, clock, IRQ, DMA, filters/channels, registration, Kconfig, and build scripts.

Edit only what the target needs. Preserve project style and existing devices. Do not bulk-replace peripheral names across vendor code. Keep hardware constants linked to manifest evidence in the engineering report or concise code comments where the project convention supports them.

Read the matching file under `playbooks/` before defining hardware tests.

## Close the loop

Build with the project's normal command, or configure `commands.build` and run `python tools/driveforge.py run <project> --config <config> --execute-build`. Classify each failure, make one evidence-backed correction, and retry no more than the configured repair limit.

Run flash and hardware-test gates only when they are in the user's requested scope and their commands identify the intended target. Enable them explicitly with `--execute-flash` and `--execute-test`; do not treat a build pass as hardware verification.

Finish with `<project>/.driveforge/verification_report.yaml`. State modified files, fact confidence, build/flash/test evidence, unresolved risks, and one of: `BLOCKED`, `FAIL`, `BUILD_PASS`, `FLASH_PASS`, or `VERIFIED`.
