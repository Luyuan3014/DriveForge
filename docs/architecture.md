# DriveForge 架构（0.2 阶段一）

本文描述 `0.2.x` 阶段一的已实现架构。产品长期愿景和完整需求以 [`DriveForge-PRD.md`](../DriveForge-PRD.md) 为准；本文只记录当前代码能够完成的事情。

## 设计目标

DriveForge MVP 围绕四个不变量设计：

1. **Hardware facts are evidence-backed**：硬件相关值必须有用户输入或工程证据。
2. **Adapt first, rewrite last**：优先复用已有实例和官方实现。
3. **Execution is explicit**：构建、烧录和测试阶段分别启用，互不隐式授权。
4. **Verification levels are distinct**：构建通过、烧录通过和硬件验证通过是不同状态。

## 数据流

```mermaid
flowchart TD
    A[用户需求与可选配置] --> B[Intent Parser]
    B --> C[Project Analyzer]
    C --> D[Hardware Fact Resolver]
    D --> E{Critical Fact Gate}
    E -- 缺少事实 --> F[BLOCKED Report]
    E -- 事实完整 --> G[Adapt-first Planner]
    G --> H[Codex Skill / Patch Command]
    H --> I[Build Gate]
    I --> J[Flash Gate]
    J --> K[Hardware Test Gate]
    I -.失败.-> L[Bounded Repair]
    K -.失败.-> L
    L --> I
    K --> M[Verification Report]
    M --> N[Read-only Local HTML View]
```

CLI 负责确定性扫描、门禁、规划、命令执行和报告；根目录的 `SKILL.md` 负责指导 Codex 完成需要工程判断的代码修改。独立运行时也可以通过 `commands.patch` 和 `commands.repair` 接入外部自动化实现器。

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `src/driveforge/cli.py` | 参数解析、配置合并、产物写入和退出码 |
| `src/driveforge/intent.py` | 从中英文需求中识别外设、实例和操作类型 |
| `src/driveforge/analyzer.py` | 扫描 RT-Thread、MCU、构建工具、探针、驱动候选、工程拓扑和语义摘要 |
| `src/driveforge/svd.py` | 解析 CMSIS-SVD，提供外设、寄存器、位域和 IRQ 模型 |
| `src/driveforge/c_analysis.py` | 解析活动条件编译分支、宏和指定成员初始化 |
| `src/driveforge/timing.py` | CAN、UART、SPI 的确定性时序求解 |
| `src/driveforge/patcher.py` | 基于唯一锚点生成/应用 Adapt-First unified diff |
| `src/driveforge/defensive.py` | 检测无界硬件轮询并生成超时 Guard 模板 |
| `src/driveforge/resolver.py` | 合并项目事实与用户事实，规范化值并执行关键事实门禁 |
| `src/driveforge/planner.py` | 选择参考实例，生成最小改动导向的 Driver Plan |
| `src/driveforge/runner.py` | 执行 patch/build/flash/test/repair 命令，保存日志并计算最终状态 |
| `src/driveforge/viewer.py` | 从真实 JSON 产物生成只读、自包含的本地 HTML 报告 |
| `src/driveforge/models.py` | Fact、Evidence、ScanResult、CommandResult 等领域模型 |
| `src/driveforge/utils.py` | 文件遍历、序列化、哈希基线和变更计算 |
| `playbooks/` | 七类外设的最小硬件验收准则 |
| `schemas/` | 请求、Manifest、Plan、Report 的 JSON Schema |

## Project Analyzer

扫描器只读取文本型工程文件，并忽略 `.git`、`.driveforge`、构建目录、依赖目录和缓存。单次扫描最多处理 5000 个文件，每个文件最大 2 MB，防止意外读取超大生成物。

当前识别内容包括：

- RT-Thread 与版本宏；
- GD32F4、STM32F4 型号与厂商；
- SCons、CMake、Make、west 和 ARM 编译器；
- J-Link、ST-Link、pyOCD 线索；
- 同类外设实例和驱动文件；
- C/C++ 文件的活动宏分支与指定成员初始化摘要；关闭的 `#if` 分支不会进入语义摘要。
- BSP、厂商 SDK、HAL、启动文件、链接脚本、驱动目录、板级配置、Kconfig、SCons、CMake 和 DeviceTree 文件。

扫描结果只是事实候选。用户通过配置提供的值优先级更高，并被标记为 `user_config`，不会与扫描证据混淆。

## Hardware Fact Gate

每个事实包含：

```yaml
value: "PD0"
confidence: "VERIFIED"
source: "project:board_config"
evidence:
  - path: "board.h"
    line: 42
    excerpt: "#define CAN0_RX_PIN PD0"
```

事实置信度为 `VERIFIED`、`HIGH`、`MEDIUM`、`LOW` 或 `UNKNOWN`。关键门禁只接受已解析且置信度不低于 `HIGH` 的事实。各外设的具体要求见 [`configuration.md`](configuration.md)。

以下情况也会阻塞：

- 目标不是 RT-Thread；
- MCU 不属于 GD32F4 或 STM32F4；
- 外设不在 MVP 范围；
- 外设类型与实例名称不一致；
- GPIO 名称不在 `PA0..PK15` 范围；
- 显式提供的时钟频率不是正整数。

## Planning 与 Adapt First

Planner 根据候选文件来源和匹配度进行排序。项目内实现优先于 RTOS BSP，RTOS BSP 优先于厂商 SDK。若存在不同实例，例如目标是 `CAN0` 而项目已有 `CAN1`，计划采用 `adapt_existing_instance`；否则依次进入扩展已有驱动或基于已验证 SDK 证据的新实现策略。

Planner 只产生策略与验收条件，不对厂商代码进行全局字符串替换。阶段一增加 `driveforge patch`：补丁配置必须声明文件、唯一旧文本和新文本；预览阶段会生成 `.driveforge/driver.patch`，锚点缺失或多次命中时保持源文件不变。外部 `commands.patch` 仍可用于复杂工程修改。

## 阶段一确定性引擎

- `parse_svd(path)` 将 CMSIS-SVD 转换为 `SVDDevice`，寄存器地址由 `base_address + address_offset` 明确计算，位域提供掩码。
- `solve_can_bittiming(clock_hz, bitrate)` 遍历整数 Prescaler/BS1/BS2，在 80%~87.5% 采样点窗口内优先选择零误差解。
- `solve_uart_baudrate` 和 `solve_spi_clock` 分别返回过采样分频和不超过器件上限的最快 SPI 分频。
- `CSourceAnalyzer` 使用依赖无关的预处理分支模型；后续接入 tree-sitter 只需替换后端，不改变 `CSourceModel` 消费接口。
- `find_unbounded_waits` 为状态/就绪/收发标志的无界 `while` 提供审查发现，`add_timeout_guard` 生成带预算的退出模板。

## 执行与修复

执行器只运行命令配置中的字符串。对应 CLI 开关未提供时，该阶段记录为 `SKIPPED`：

- `--execute-patch`
- `--execute-build`
- `--execute-flash`
- `--execute-test`

Build 和 Test 可以使用 `commands.repair` 进行有限次数修复。默认最多 2 次，代码强制上限为 10 次。Flash 失败不会自动按代码缺陷处理或反复烧录。

最终状态按照各阶段最后一次结果计算，因此“首次失败、修复后通过”会正确进入通过状态，同时历史失败仍保留在报告中供审计。

## 产物与可追踪性

`plan` 在目标工程中创建源码哈希基线。随后执行 `run` 时，Verification Report 会列出规划之后发生变化的文本文件。构建、烧录、测试和修复命令的标准输出与错误输出分别写入 `.driveforge/logs/`。

YAML 产物便于人工审查，JSON 产物便于后续工具消费。核心实现使用 JSON 兼容的 YAML 子集，从而保持零第三方运行时依赖。

`driveforge view` 只读取 `state.json`、可选的 `verification_report.json` 和日志目录，并在同一产物目录生成 `report.html`。页面不提供执行按钮，不引入服务端，也不改变任何工作流状态。仓库中的 `website/` 是独立的产品演示，不连接 CLI，其预设结果不属于证据链。

## 当前边界

- CLI 本身不包含大模型 API；复杂工程判断仍由 Codex Skill 或外部命令完成，阶段一的显式锚点补丁可独立运行。
- 当前没有内置 J-Link/OpenOCD 参数生成器，探针命令由项目配置提供。
- 没有真实开发板时，只能验证工作流，不能声称目标驱动 `VERIFIED`。
- Linux、Zephyr、FreeRTOS、复杂高速外设和非 Cortex-M 平台不属于当前 MVP。
