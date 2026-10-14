# Roadmap

Roadmap 用来描述实现顺序，不代表对具体发布日期的承诺。详细的系统架构优化、工业级规范、Studio 交互重构与四阶段实施计划见 [`docs/evolution-blueprint.md`](evolution-blueprint.md)。

## 0.1 MVP：软件闭环基础

已完成：

- RT-Thread、GD32F4/STM32F4 和七类外设的范围门禁；
- 工程拓扑、MCU、构建系统、探针和参考驱动扫描；
- 带证据和置信度的 Hardware Manifest；
- Adapt First Driver Plan；
- 显式 Build/Flash/Test 命令执行；
- Build/Test 的有限修复循环和失败分类；
- 日志、基线变更追踪和 Verification Report；
- 基于真实 `.driveforge` 产物的只读本地 HTML 报告；
- Codex Skill、JSON Schema、Playbook、示例与自动化测试。

尚未完成：

- 在真实 GD32F470 + RT-Thread 5.x + CAN0 开发板上跑通第一套公开 Benchmark；
- 内置 J-Link/OpenOCD/pyOCD 命令生成和工具可用性诊断；
- 串口/RTT 交互协议与结构化硬件测试结果采集；
- 原理图和芯片手册的专用解析器（CMSIS-SVD 阶段二已提供）；
- 独立的大模型 Provider 与工具调用循环。

## 0.2 阶段二：确定性事实底座与代码闭环（已完成）

- `driveforge.svd` 解析 CMSIS-SVD，并将基地址、寄存器、位域、IRQ 固化到扫描状态。
- `driveforge.c_analysis` 先处理活动条件编译分支，再提取宏和指定成员初始化，降低正则误判。
- `driveforge.timing` 提供 CAN 位时序、UART 过采样和 SPI 安全分频求解。
- `driveforge.patcher` 与 `driveforge patch` 使用唯一锚点生成可审查 unified diff，支持显式应用。
- `driveforge.defensive` 提供屏蔽注释/字符串后的无界硬件轮询检查和超时 Guard 模板。
- Manifest 增加稳定的 `facts_digest`，并在 SVD 设备与 MCU 不一致时阻塞事实门禁；补丁应用使用整批原子替换。

阶段二不宣称完成真实板卡验证；它把硬件事实和代码变更变成可重复、可审查的输入，为 0.3 阶段三探针闭环提供稳定接口。具体用法见 [`docs/evolution-blueprint.md`](evolution-blueprint.md) 和 [`docs/architecture.md`](architecture.md)。

## 下一里程碑：CAN0 真实 Benchmark

目标平台：

- GD32F470ZIT6；
- RT-Thread 5.x；
- SCons；
- J-Link/SWD；
- 已有 CAN1，新增 CAN0；
- CAN0 RX=PD0、TX=PD1，最终硬件参数以目标板证据为准。

验收标准：

1. 从一句自然语言需求开始。
2. 自动发现 CAN1 并形成差异计划。
3. 生成或修改驱动、板级配置、Kconfig 和构建文件。
4. 构建、烧录、设备注册、TX、RX、IRQ 和环回测试通过。
5. 至少演示一次失败诊断和有限修复。
6. 保存可复现的配置、补丁、日志和 Verification Report。

只有真实硬件测试通过后，Benchmark 才能标记为 `VERIFIED`。

## 后续方向

优先顺序：

1. 加固 RT-Thread 5.x 的 GD32F4/STM32F4 驱动适配。
2. 扩充 SVD、CMSIS-Pack、厂商 SDK 与官方手册证据源。
3. 标准化 J-Link、OpenOCD、pyOCD、串口与 RTT 适配器。
4. 为七类外设提供结构化测试执行器与诊断规则。
5. 增加 STM32H7、STM32G4、GD32H7。
6. 框架成熟后再考虑 Zephyr、FreeRTOS、Linux 和复杂高速外设。

新增范围必须伴随实际工程样例、门禁规则、Playbook、测试和更新文档。
