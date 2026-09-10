# DriveForge

**Autonomous Embedded Driver Engineering Agent**

**嵌入式驱动自主工程智能体**

---

## 1. 项目定位

DriveForge 是一个面向嵌入式软件开发的 AI 驱动工程智能体。

项目目标不是简单通过大语言模型生成驱动代码，而是将传统嵌入式驱动工程中的：

- 项目分析

- 硬件识别

- 芯片资料检索

- BSP 分析

- 驱动实现

- 驱动移植

- 平台适配

- 工程配置

- 编译验证

- 固件烧录

- 硬件测试

- 故障诊断

- 自动修复

整合为一套完整的 Autonomous Engineering Workflow。

用户只需要提供目标工程以及必要的硬件信息，例如：

```text
操作系统：RT-Thread 5.1.0
MCU：GD32F470ZIT6
目标外设：CAN0
需求：完成 CAN0 驱动适配并验证收发
```

DriveForge 自动分析现有工程、BSP、SDK 和硬件信息，并自主完成从驱动实现到真实硬件验证的完整开发闭环。

DriveForge 最终希望实现的不是：

```text
Prompt
  ↓
LLM
  ↓
drv_can.c
```

而是：

```text
Requirement
    ↓
Project Understanding
    ↓
Hardware Understanding
    ↓
Driver Strategy
    ↓
Implementation / Porting
    ↓
Build
    ↓
Flash
    ↓
Hardware Test
    ↓
Diagnosis
    ↓
Automatic Repair
    ↓
Verified Driver
```

DriveForge 的最终定位是：

> **一个能够像嵌入式驱动工程师一样理解项目、理解硬件、编写驱动、调试驱动并通过真实硬件验证结果的 AI Engineering Agent。**

---

# 2. DriveForge 要解决的问题

传统嵌入式驱动开发存在大量重复工作。

对于 UART、SPI、I2C、CAN、ADC、PWM、GPIO、Flash、Ethernet 等常见外设，工程师通常需要重复进行：

```text
阅读芯片手册
↓
查找 SDK 示例
↓
查找已有 BSP
↓
确认 GPIO / PinMux
↓
确认 Clock
↓
确认 IRQ
↓
确认 DMA
↓
编写初始化代码
↓
接入 RTOS Driver Framework
↓
修改 Kconfig / board.h / DeviceTree
↓
编译
↓
烧录
↓
观察日志
↓
定位错误
↓
修改代码
↓
重新测试
```

其中大量步骤具有明显的模式化特征。

现代 AI Coding Agent 已经具备较强的：

- 大型代码库理解能力

- 多文件修改能力

- 文档理解能力

- 编译错误分析能力

- 命令执行能力

- 代码生成与重构能力

- Debug 日志分析能力

DriveForge 的目标就是把这些能力与嵌入式硬件知识、芯片资料、调试器和真实开发板连接起来。

---

# 3. DriveForge 的核心原则

## 3.1 Adapt First, Rewrite Last

DriveForge 不应该默认重新编写驱动。

第一原则是：

```text
Search Existing Implementation First.
```

优先级：

```text
已有工程驱动
↓
同系列 MCU 驱动
↓
官方 BSP
↓
厂商 SDK
↓
RTOS 官方驱动
↓
已有开源实现
↓
重新实现
```

例如用户要求：

```text
GD32F470 + RT-Thread + CAN0
```

DriveForge 应该首先判断：

```text
工程是否已有 CAN1？
GD32 BSP 是否已有 CAN driver？
CAN0 和 CAN1 是否只是 Peripheral Instance 差异？
```

如果已有 CAN1，则优先完成：

```text
CAN1 implementation
        ↓
difference analysis
        ↓
CAN0 adaptation
```

而不是重新实现整个 CAN Driver。

---

# 4. Hardware Fact 必须来源可追踪

嵌入式开发最大的 AI 风险不是代码语法错误，而是：

> AI 猜硬件。

因此 DriveForge 必须建立 Hardware Fact System。

例如：

```yaml
mcu:
  vendor: GigaDevice
  model: GD32F470ZIT6

peripheral:
  type: CAN
  instance: CAN0

pins:
  rx:
    pin: PD0
    confidence: VERIFIED
    source: board_config

  tx:
    pin: PD1
    confidence: VERIFIED
    source: board_config

clock:
  bus: APB1
  frequency: 60000000
  confidence: HIGH
  source: project_clock_config

interrupt:
  irq: CAN0_RX0_IRQn
  confidence: VERIFIED
  source: CMSIS
```

对于以下信息：

```text
GPIO
PinMux
Clock
IRQ
DMA
Register
Voltage
Peripheral Instance
Memory Address
```

不得单纯依据 LLM 记忆生成。

信息来源优先级：

```text
当前工程
↓
原理图 / Board Configuration
↓
Vendor BSP / SDK
↓
CMSIS-Pack
↓
CMSIS-SVD
↓
Datasheet
↓
Reference Manual
↓
官方示例
↓
可信开源实现
```

如果关键信息无法确认，应进入：

```text
BLOCKED
```

状态，而不是猜测。

---

# 5. Hardware Manifest

DriveForge 在修改代码之前，需要首先建立当前硬件平台的统一描述：

```text
hardware_manifest.yaml
```

它作为整个 Agent Workflow 的事实来源。

例如：

```yaml
platform:
  os: rt-thread
  version: 5.1.0

mcu:
  vendor: GigaDevice
  family: GD32F4
  model: GD32F470ZIT6

build:
  system: scons
  compiler: arm-none-eabi-gcc

debug:
  probe: J-Link
  interface: SWD

target:
  peripheral: CAN0

pins:
  rx: PD0
  tx: PD1

clock:
  apb1: 60000000

driver:
  framework: rt_device
  existing_reference: CAN1
```

所有代码生成都必须建立在 Hardware Manifest 之上。

---

# 6. DriveForge 终极形态

DriveForge 的终极形态不是一个 Skill 文件，而是一套完整的 Autonomous Embedded Engineering System。

整体架构：

```text
                         User
                           │
                           ▼
                    DriveForge Agent
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
     Project Analyzer              Knowledge Engine
            │                             │
            │                 ┌───────────┼───────────┐
            │                 │           │           │
            │                SVD        SDK        Manual
            │                 │           │           │
            └──────────────┬──┴───────────┴───────────┘
                           │
                           ▼
                 Hardware Context Resolver
                           │
                           ▼
                  Hardware Manifest
                           │
                           ▼
                  Driver Strategy Engine
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ▼            ▼             ▼
          RT-Thread      Linux        Other RTOS
           Adapter       Adapter        Adapter
              │            │             │
              └────────────┼─────────────┘
                           ▼
                    Code Engineering
                           │
                           ▼
                     Build System
                           │
                     ┌─────┴─────┐
                     │           │
                   FAIL         PASS
                     │           │
                     ▼           ▼
                 Diagnose      Flash
                     ▲           │
                     │           ▼
                     │       Hardware Test
                     │           │
                     │      ┌────┴────┐
                     │      │         │
                     └──── FAIL      PASS
                                      │
                                      ▼
                               Verification Report
```

---

# 7. Project Analyzer

DriveForge 首先自动识别目标工程。

识别：

```text
RTOS
RTOS Version
MCU
MCU Family
BSP
Vendor SDK
HAL
Build System
Compiler
Linker Script
Startup Code
Driver Directory
Board Configuration
Kconfig
SConscript
CMake
DeviceTree
```

例如：

```text
Detected Platform

OS:
RT-Thread 5.1.0

MCU:
GD32F470ZIT6

SDK:
GD32F4xx Firmware Library

Build:
SCons

Compiler:
arm-none-eabi-gcc

Existing Drivers:
UART
GPIO
SPI
CAN1
ADC

Target:
CAN0

Reference Implementation:
CAN1
```

---

# 8. Driver Strategy Engine

AI 不直接开始写代码。

首先生成 Driver Plan。

例如：

```text
CAN0 Implementation Strategy

1. Reuse existing GD32 CAN driver
2. Add CAN0 hardware configuration
3. Configure PD0 / PD1 alternate function
4. Enable CAN0 peripheral clock
5. Configure CAN0 RX interrupt
6. Add CAN0 device registration
7. Update board configuration
8. Enable CAN0 through Kconfig
9. Build
10. Flash
11. Run CAN loopback test
```

这样可以减少 AI 在大型工程中无目的修改代码。

---

# 9. Code Engineering

DriveForge 自动修改：

```text
Driver Source
Driver Header
board.h
board.c
Kconfig
SConscript
CMakeLists.txt
rtconfig.h
startup
DeviceTree
Defconfig
HAL Configuration
```

同时要求：

- 尽量保持项目原有代码风格

- 不引入不必要架构

- 不破坏已有驱动

- 修改范围最小化

- 所有硬件参数均具备来源

- 支持自动生成 Patch/Diff

---

# 10. Build Agent

DriveForge 自动识别并运行：

```text
scons
cmake
make
ninja
west
menuconfig
pkgs
```

发生错误时：

```text
Compiler Error
↓
Error Classification
↓
Source Analysis
↓
Patch
↓
Rebuild
```

直到：

```text
BUILD PASS
```

或者明确报告无法继续的原因。

---

# 11. Flash Agent

DriveForge 最终应支持：

```text
J-Link
OpenOCD
pyOCD
ST-Link
DFU
UART Bootloader
Vendor Programmer
```

自动完成：

```text
Connect Target
↓
Reset
↓
Erase
↓
Program
↓
Verify
↓
Reset
↓
Run
```

---

# 12. Hardware-In-the-Loop

这是 DriveForge 与普通 AI Coding Tool 最重要的区别。

DriveForge 必须能够观察真实硬件。

支持：

```text
UART
SEGGER RTT
GDB
SWO
SSH
Telnet
FinSH
Shell
Test GPIO
CAN Adapter
USB
Network
```

例如：

```text
Build PASS
↓
Flash
↓
Board Boot
↓
Wait RT-Thread Startup
↓
Open FinSH
↓
list_device
↓
detect can0
↓
execute can_test
↓
collect result
```

---

# 13. Peripheral Test Playbook

每种外设建立标准化测试流程。

### UART

```text
Device Registration
TX
RX
Interrupt RX
Loopback
Stress Test
```

### SPI

```text
Controller Registration
CS
Transfer
JEDEC ID
Read/Write
Stress Test
```

### I2C

```text
Bus Registration
Scan
ACK
Read Device ID
Read/Write Register
```

### CAN

```text
Device Registration
Bit Timing
Filter
TX
RX
Interrupt
Loopback
External Node Test
Bus-Off Recovery
```

### ADC

```text
Device Registration
Channel
Raw Sample
Voltage Conversion
Repeated Sampling
Noise Analysis
```

### Flash

```text
Identify
Erase
Write
Read
Compare
CRC
Power Recovery Test
```

### Ethernet

```text
PHY Detection
Link
DHCP
Static IP
Ping
TCP
UDP
iperf
Reconnect
```

---

# 14. Autonomous Debug

测试失败时，DriveForge 不立即交还给用户。

例如：

```text
CAN TX PASS
CAN RX FAIL
```

自动进入：

```text
Driver Code
↓
CAN Status Register
↓
NVIC
↓
Interrupt Pending
↓
CAN Filter
↓
GPIO AF
↓
Clock
↓
Transceiver State
```

形成 Root Cause Hypothesis。

例如：

```text
Hypothesis #1
CAN RX filter is not enabled.

Confidence: 0.87

Evidence:
CAN peripheral reports RX FIFO empty.
TX successfully enters ACK state.
RX IRQ never becomes pending.
Current filter initialization only configures CAN1.
```

然后自动修改并重新验证。

最终实现：

```text
Observe
↓
Hypothesize
↓
Patch
↓
Build
↓
Flash
↓
Test
↓
Observe
```

这就是 DriveForge 最核心的 Agent Loop。

---

# 15. 最终输出

DriveForge 不应该只输出：

```text
代码已经修改完成。
```

而应该生成 Engineering Report。

例如：

```text
DriveForge Driver Report

Target:
GD32F470ZIT6

OS:
RT-Thread 5.1.0

Peripheral:
CAN0

Implementation:
PASS

Build:
PASS

Flash:
PASS

Device Registration:
PASS

CAN TX:
PASS

CAN RX:
PASS

Interrupt:
PASS

Loopback:
10,000 / 10,000 PASS

Modified Files:
board.h
drv_can.c
Kconfig

Hardware Facts:
8 VERIFIED
2 HIGH CONFIDENCE
0 UNKNOWN

Final Status:

VERIFIED
```

---

# 16. DriveForge 最终支持范围

终极版本计划支持：

## Operating Systems

```text
RT-Thread
Linux
Zephyr
FreeRTOS
ThreadX
NuttX
Bare-metal
```

## MCU / SoC

```text
STM32
GD32
NXP
TI
ESP32
Nordic
Renesas
Rockchip
Allwinner
NXP i.MX
TI Sitara
其他主流 MCU / MPU
```

## Peripheral

```text
GPIO
UART
SPI
I2C
CAN
CAN FD
ADC
DAC
PWM
Timer
DMA
RTC
Watchdog

QSPI
NOR Flash
NAND
SDIO
eMMC

Ethernet
USB
PCIe

Display
Touch
Audio
Camera
Sensor
```

DriveForge 的最终目标是：

> **让大部分标准嵌入式驱动工作从“人工实现”转变为“AI 自主实现 + 工程师审核”。**

---

# 17. DriveForge MVP

DriveForge 第一阶段不支持 Linux。

MVP 定位：

**DriveForge RTOS Driver Agent**

目标不是追求支持大量硬件，而是首先跑通：

```text
Analyze
↓
Adapt
↓
Build
↓
Flash
↓
Test
↓
Diagnose
↓
Repair
```

完整闭环。

---

# 18. MVP 平台范围

第一版只支持：

```text
RT-Thread
```

优先版本：

```text
RT-Thread 5.x
```

优先 MCU：

```text
GD32F4
STM32F4
```

后续扩展：

```text
STM32H7
STM32G4
GD32H7
其他 Cortex-M MCU
```

---

# 19. MVP 外设范围

第一阶段：

```text
GPIO
UART
SPI
I2C
CAN
ADC
PWM
```

暂不处理：

```text
Ethernet
USB
SDIO
MIPI
PCIe
复杂 Display Pipeline
DDR
```

这些等基础框架成熟后再扩展。

---

# 20. MVP 输入

用户指定工程目录，例如：

```bash
driveforge ./rtthread_project
```

然后提出：

```text
给这个项目增加 CAN0 驱动。
```

或者：

```text
把当前 UART7 适配到 RT-Thread serial framework，
要求支持中断接收。
```

用户可以补充：

```text
MCU: GD32F470ZIT6
RT-Thread: 5.1.0
CAN0:
RX = PD0
TX = PD1
```

其余信息优先自动分析。

---

# 21. MVP Workflow

完整流程：

```text
                     User Request
                          │
                          ▼
                   Project Scanner
                          │
                          ▼
                 Platform Detection
                          │
                          ▼
                Existing Driver Search
                          │
                          ▼
                Hardware Manifest
                          │
                          ▼
                   Driver Plan
                          │
                          ▼
                    Code Patch
                          │
                          ▼
                       SCons
                          │
                    ┌─────┴─────┐
                    │           │
                   FAIL        PASS
                    │           │
                    ▼           ▼
                 Repair       J-Link
                    ▲           │
                    │           ▼
                    │         Flash
                    │           │
                    │           ▼
                    │      Serial / RTT
                    │           │
                    │           ▼
                    │      Driver Test
                    │           │
                    │      ┌────┴────┐
                    │      │         │
                    └──── FAIL      PASS
                                     │
                                     ▼
                                  Report
```

---

# 22. MVP 项目结构

推荐：

```text
driveforge/

├── SKILL.md

├── core/
│   ├── project_analyzer/
│   ├── hardware_resolver/
│   ├── driver_planner/
│   ├── build_agent/
│   ├── flash_agent/
│   ├── debug_agent/
│   └── test_agent/

├── adapters/
│   └── rtthread/

├── platforms/
│   ├── gd32/
│   └── stm32/

├── drivers/
│   ├── gpio/
│   ├── uart/
│   ├── spi/
│   ├── i2c/
│   ├── can/
│   ├── adc/
│   └── pwm/

├── schemas/
│   ├── hardware_manifest.yaml
│   ├── driver_request.yaml
│   ├── driver_plan.yaml
│   └── verification_report.yaml

├── tools/
│   ├── project_scan.py
│   ├── svd_parser.py
│   ├── build.py
│   ├── jlink.py
│   ├── openocd.py
│   ├── serial.py
│   └── test_runner.py

├── playbooks/
│   ├── uart.md
│   ├── spi.md
│   ├── i2c.md
│   ├── can.md
│   ├── adc.md
│   └── pwm.md

└── tests/
```

---

# 23. MVP 的第一项 Benchmark

建议第一套真实 Benchmark：

```text
Board:
GD32F470ZIT6

OS:
RT-Thread 5.1.0

Build:
SCons

Debugger:
J-Link

Target:
CAN0
```

目标：

```text
已有 CAN1 正常
CAN0 尚未完成
```

让 DriveForge 自动：

```text
扫描工程
↓
发现 CAN1
↓
分析 CAN0 / CAN1 差异
↓
确认 PD0 / PD1
↓
配置 Clock
↓
配置 GPIO AF
↓
配置 CAN
↓
配置 Filter
↓
配置 IRQ
↓
注册 RT-Thread CAN Device
↓
修改 Kconfig
↓
SCons Build
↓
J-Link Flash
↓
执行 CAN Test
↓
分析结果
↓
自动修复
↓
PASS
```

如果这个 Benchmark 真正跑通：

```text
Requirement → Verified Hardware Driver
```

DriveForge 的核心技术路线就基本成立。

---

# 24. MVP 成功标准

第一版不以：

```text
支持100种MCU
支持30种外设
```

作为成功标准。

真正的成功标准只有一个：

> **能否在一块真实开发板上，在几乎无人干预的情况下，从用户一句驱动需求开始，一直到生成可运行、已通过真实硬件测试的驱动。**

如果能够做到：

```text
用户：
“给这个RT-Thread工程增加CAN0驱动。”

DriveForge：
分析 → 修改 → 编译 → 烧录 → 测试 → 修复

最终：

CAN0 VERIFIED
```

这个 MVP 就已经成功。

---

# 25. 项目长期愿景

DriveForge 最终希望改变嵌入式驱动开发的工作方式。

传统模式：

```text
Engineer writes driver.
Engineer debugs driver.
Engineer verifies driver.
```

DriveForge 模式：

```text
Engineer defines requirement.
          ↓
DriveForge implements.
          ↓
DriveForge verifies.
          ↓
Engineer reviews.
```

工程师从大量重复性的：

```text
查寄存器
抄初始化
改 GPIO
改 IRQ
改 DMA
编译
烧录
看串口
重复 Debug
```

逐渐转移到：

```text
系统架构
硬件设计
异常场景
性能优化
可靠性设计
Safety
产品决策
```

最终目标不是取代驱动工程师，而是把大量标准化、重复性驱动工程工作自动化。

**DriveForge 的最终产品形态，是一个能够自主理解嵌入式硬件和软件工程，并在真实硬件上完成实现与验证的 AI Embedded Engineering Agent。**
