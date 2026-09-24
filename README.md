# DriveForge

> Evidence-first autonomous engineering workflow for RT-Thread peripheral drivers.

DriveForge 是一个面向嵌入式驱动开发的工程智能体。它把项目分析、硬件事实解析、驱动复用规划、代码工程、构建、烧录、硬件测试、诊断与修复组织成一条可审查、可追踪的工作流。

当前仓库提供 DriveForge MVP。它的目标不是支持尽可能多的芯片，而是先可靠跑通：

```text
需求 → 工程扫描 → 硬件事实清单 → 复用策略 → 实现 → 构建 → 烧录 → 测试 → 报告
```

## 当前能力

| 维度 | MVP 支持范围 |
| --- | --- |
| 操作系统 | RT-Thread，优先支持 5.x |
| MCU | GD32F4、STM32F4 |
| 外设 | GPIO、UART、SPI、I2C、CAN、ADC、PWM |
| 构建 | SCons 优先；可识别 Make、west，支持配置自定义命令 |
| 调试与测试 | 通过显式命令接入 J-Link、OpenOCD、pyOCD、ST-Link、串口或 RTT |
| 输出 | Hardware Manifest、Driver Plan、执行日志、Verification Report |

DriveForge 不会凭模型记忆猜测引脚、PinMux、时钟、IRQ、DMA、寄存器、地址或外设实例。关键事实无法追溯到用户输入、当前工程、板级配置、CMSIS 或厂商 SDK 时，流程会进入 `BLOCKED` 并指出缺少的事实。

## 快速开始

环境要求：Python 3.10 或更高版本。核心运行时无第三方依赖。

```powershell
git clone https://github.com/Luyuan3014/DriveForge.git
cd DriveForge
python -m pip install -e .
```

也可以不安装，直接使用源码入口：

```powershell
python tools/driveforge.py --version
```

为一个 RT-Thread 工程生成硬件事实清单和驱动计划：

```powershell
driveforge plan C:\path\to\rtthread-project `
  --request "给这个项目增加 CAN0 驱动" `
  --mcu GD32F470ZIT6 `
  --rx-pin PD0 --tx-pin PD1 `
  --clock-gate RCU_CAN0 `
  --irq CAN0_RX0_IRQn
```

产物默认写入目标工程的 `.driveforge/`：

- `hardware_manifest.yaml`：硬件事实、置信度、来源与证据位置；
- `driver_plan.yaml`：复用策略、候选文件、风险、阻塞项与执行步骤；
- `state.json`：完整的机器可读扫描状态；
- `baseline.json`：规划时的源码基线，用于追踪后续修改；
- `verification_report.yaml/json`：构建、烧录、测试和最终状态；
- `logs/`：每次命令执行的原始输出。

完整配置示例见 [`examples/gd32f470-can0.json`](examples/gd32f470-can0.json)。

## 执行构建、烧录与测试

DriveForge 只执行配置中明确提供、且命令行明确启用的阶段。构建不会自动触发烧录，烧录也不会自动代表硬件验证通过。

```powershell
driveforge run C:\path\to\rtthread-project `
  --config driveforge.json `
  --execute-build `
  --execute-flash `
  --execute-test
```

最终状态含义：

| 状态 | 含义 |
| --- | --- |
| `PLANNED` | 已完成分析与规划，未执行验证阶段 |
| `BUILD_PASS` | 构建通过，尚未证明固件烧录或硬件行为 |
| `FLASH_PASS` | 固件烧录通过，尚未完成硬件测试 |
| `VERIFIED` | 配置的硬件测试命令已通过 |
| `FAIL` | 某个已执行阶段失败 |
| `BLOCKED` | 关键事实、命令或支持范围不足，流程未继续 |

退出码为 `0` 表示请求的阶段完成，`1` 表示执行失败，`2` 表示输入无效或流程被阻塞。

## 使用 Codex Skill

仓库根目录的 [`SKILL.md`](SKILL.md) 定义了 DriveForge 的智能体行为：先建立硬件事实，再按“已有工程 → 同系列实现 → 官方 BSP → 厂商 SDK → RT-Thread 驱动 → 新实现”的顺序寻找复用方案，最后执行有边界的验证与修复。

各外设的测试准则位于 [`playbooks/`](playbooks/)，输出格式位于 [`schemas/`](schemas/)。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [`DriveForge-PRD.md`](DriveForge-PRD.md) | 产品定位、MVP 范围和长期愿景 |
| [`website/`](website/README.md) | 官方落地页与 Web 交互式仿真控制台 |
| [`docs/architecture.md`](docs/architecture.md) | 系统边界、模块职责、数据流与安全不变量 |
| [`docs/configuration.md`](docs/configuration.md) | 配置文件、CLI 参数、事实优先级和命令环境 |
| [`docs/development.md`](docs/development.md) | 本地开发、测试、代码结构和提交要求 |
| [`docs/roadmap.md`](docs/roadmap.md) | 当前完成度与后续演进方向 |
| [`docs/update-process.md`](docs/update-process.md) | 每次项目更新时必须同步的文档和发布流程 |
| [`CHANGELOG.md`](CHANGELOG.md) | 所有版本与未发布变更的摘要 |
| [`docs/updates/`](docs/updates/) | 重要更新的背景、兼容性、验证与限制说明 |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | 贡献流程与变更检查清单 |

## 开发验证

```powershell
python -m unittest discover -s tests -v
```

当前 MVP 的自动化测试覆盖请求解析、工程扫描、事实门禁、复用优先规划、Windows 命令执行、失败恢复、规划基线追踪和完整工作流状态判定。

## 项目状态

DriveForge 目前处于 `0.1.0` MVP 阶段。软件工作流已经可运行；真实板卡上的 `VERIFIED` 仍取决于目标工程、调试器、测试设备和配置命令。详细限制和下一阶段计划见 [`docs/roadmap.md`](docs/roadmap.md)。

## License

[MIT](LICENSE)
