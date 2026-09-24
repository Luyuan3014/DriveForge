# 配置与命令参考

DriveForge 使用 JSON 配置文件，核心运行时不依赖第三方 YAML 库。JSON 配置、命令行快捷参数和 `--set` 可以组合使用；命令行值覆盖配置文件。

## 最小配置结构

```json
{
  "request": "给这个项目增加 CAN0 驱动并验证收发",
  "hardware": {
    "platform": {"os": "rt-thread", "version": "5.1.0"},
    "mcu": {"model": "GD32F470ZIT6"},
    "target": {"peripheral": "CAN", "instance": "CAN0"},
    "pins": {"rx": "PD0", "tx": "PD1"},
    "clock": {"gate": "RCU_CAN0", "frequency": 60000000},
    "interrupt": {"irq": "CAN0_RX0_IRQn"},
    "driver": {"reference": "CAN1"}
  },
  "commands": {
    "patch": null,
    "build": "scons -j8",
    "flash": null,
    "test": null,
    "repair": null
  },
  "timeouts": {
    "build": 600,
    "flash": 180,
    "test": 180,
    "repair": 600
  },
  "max_repair_attempts": 2
}
```

完整示例位于 [`examples/gd32f470-can0.json`](../examples/gd32f470-can0.json)，请求格式由 [`driver_request.schema.json`](../schemas/driver_request.schema.json) 描述。

## CLI

```text
driveforge scan PROJECT --request REQUIREMENT [options]
driveforge plan PROJECT --request REQUIREMENT [options]
driveforge run  PROJECT --request REQUIREMENT [options]
driveforge view PROJECT [--output PATH] [--no-open]
```

- `scan`：生成 Hardware Manifest 和原始扫描结果。
- `plan`：额外生成 Driver Plan 与源码基线。
- `run`：重新扫描和规划，并按显式开关执行阶段，最后生成 Verification Report。
- `view`：从已有 `.driveforge` JSON 产物生成只读 `report.html`；不重新扫描，也不执行任何工作流阶段。

通用选项：

| 参数 | 说明 |
| --- | --- |
| `-r, --request` | 自然语言驱动需求；也可以放在配置文件中 |
| `-c, --config` | JSON 配置文件 |
| `-o, --output` | 产物目录，默认是 `PROJECT/.driveforge` |
| `--set KEY=VALUE` | 设置任意嵌套配置值 |
| `--mcu` | 用户确认的 MCU 型号 |
| `--os-version` | 用户确认的 RT-Thread 版本 |
| `--reference` | 要复用的现有外设实例 |
| `--rx-pin / --tx-pin` | 用户确认的 RX/TX 引脚 |
| `--clock-bus / --clock-gate / --clock-frequency` | 时钟事实 |
| `--irq` | 用户确认的 IRQ 符号；保留大小写 |

没有快捷参数的值使用 `--set`：

```powershell
driveforge plan . -r "适配 SPI2" `
  --set hardware.target.instance=SPI2 `
  --set hardware.pins.sck=PB13 `
  --set hardware.pins.miso=PB14 `
  --set hardware.pins.mosi=PB15 `
  --set hardware.clock.gate=RCC_SPI2
```

`--set` 会把布尔值、`null`、整数和浮点数转换为对应 JSON 类型，其他内容保留为字符串。

## 关键事实矩阵

除 `platform.os`、`mcu.model`、`target.peripheral` 和 `target.instance` 外，各外设还必须解析以下事实：

| 外设 | 必需事实 |
| --- | --- |
| GPIO | `pins.pin` |
| UART | `pins.rx`、`pins.tx`、`clock.gate` 或 `clock.bus`、`interrupt.irq` |
| SPI | `pins.sck`、`pins.miso`、`pins.mosi`、`clock.gate` 或 `clock.bus` |
| I2C | `pins.scl`、`pins.sda`、`clock.gate` 或 `clock.bus` |
| CAN | `pins.rx`、`pins.tx`、`clock.gate` 或 `clock.bus`、`interrupt.irq` |
| ADC | `pins.pin`、`target.channel`、`clock.gate` 或 `clock.bus` |
| PWM | `pins.pin`、`target.channel`、`clock.gate` 或 `clock.bus` |

事实解析优先级：

1. 当前命令行或 JSON 配置中的用户确认值；
2. 当前工程与板级配置；
3. 工程内的 CMSIS、BSP、HAL 或厂商 SDK；
4. 从已确认型号或实例派生、不改变硬件语义的值。

自动扫描不到关键事实时应补充配置或工程证据，不应降低门禁等级。

## 命令执行

命令字段只有在对应开关启用时才执行：

| 配置 | 开关 | 说明 |
| --- | --- | --- |
| `commands.patch` | `--execute-patch` | 外部补丁或代码生成器 |
| `commands.build` | `--execute-build` | 构建；SCons/Make/west 可在缺省时安全推导 |
| `commands.flash` | `--execute-flash` | 固件烧录与校验 |
| `commands.test` | `--execute-test` | 串口、RTT 或测试台命令 |
| `commands.repair` | 由失败阶段触发 | Build/Test 的有限次数修复命令 |

配置命令以目标工程为工作目录执行，并收到以下环境变量：

- `DRIVEFORGE_PROJECT`
- `DRIVEFORGE_OUTPUT`
- `DRIVEFORGE_MANIFEST`
- `DRIVEFORGE_PLAN`

Repair 命令支持 `{phase}` 和 `{attempt}` 占位符。例如：

```json
{"repair": "python tools/repair.py --phase {phase} --attempt {attempt}"}
```

所有命令都会通过系统 shell 执行。不要运行来源不可信的配置文件，不要把访问令牌或密码直接写入命令字符串。

## 超时与修复上限

超时单位为秒，最小值为 1。默认值为 Build 600 秒，Flash/Test 180 秒，Repair 600 秒。`max_repair_attempts` 默认为 2，允许范围是 0 到 10；超过 10 时执行器会截断为 10。

Flash 失败不会触发 Repair，以避免在探针、供电或目标连接异常时反复写入设备。

## 输出 Schema

- [`hardware_manifest.schema.json`](../schemas/hardware_manifest.schema.json)
- [`driver_plan.schema.json`](../schemas/driver_plan.schema.json)
- [`verification_report.schema.json`](../schemas/verification_report.schema.json)

变更字段名称、状态枚举或必填项时，代码、Schema、示例、测试和本文件必须在同一次更新中同步。
