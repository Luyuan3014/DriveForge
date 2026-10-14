# Changelog

DriveForge 的所有重要变更都记录在此文件中。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

开发中的变更必须先写入 `Unreleased`；发布时再移动到对应版本并补充日期。较大的更新还应在 `docs/updates/` 下增加完整记录。

## [0.2.0] - 2026-10-13

### Added

- 增加标准库实现的 CMSIS-SVD 解析器（`driveforge.svd`），输出外设基地址、寄存器、位域和 IRQ 的确定性事实索引。
- 增加带条件编译分支处理的 C 语义扫描器（`driveforge.c_analysis`），识别活动宏和指定成员初始化。
- 增加 CAN、UART、SPI 时序求解器（`driveforge.timing`），返回分频参数、采样点、实际速率和误差。
- 增加锚点唯一匹配的 Adapt-First 补丁引擎（`driveforge.patcher`）和 `driveforge patch`，生成可审查的 unified Git diff。
- 增加硬件轮询超时扫描与 Guard 模板（`driveforge.defensive`）。
- 增加事实集合 SHA-256 摘要（`facts_digest`）、SVD/MCU 一致性门禁和阶段二文档校正。

### Changed

- 工程扫描结果现在包含语义扫描摘要；可选 SVD 会随 `.driveforge` 状态和 Manifest 留存。
- 版本升级到 0.2.0，阶段二产物继续使用零运行时第三方依赖。
- 补丁应用改为整批原子替换；C 候选扫描尊重显式关闭的条件编译分支；SVD 支持寄存器 `dim` 展开。

## [0.1.1] - 2026-09-24

### Added

- 新增 `driveforge view`，从真实 `.driveforge` JSON 产物生成只读本地 HTML 报告，展示事实证据、阶段状态、修改文件和日志。
- 新增官方落地页与 Web 交互式仿真控制台（`website/`），提供 Antigravity 科技风格相对论黑洞视觉引擎与外设驱动仿真体验。
- 增加基于 CDP 的 Headless 浏览器端到端测试套件（`tools/verify_website.py`）。
- 提供生产级 Nginx 配置、容器化构建（`Dockerfile`、`docker-compose.yml`）及跨平台自动化部署脚本（`deploy.ps1`、`deploy.sh`）。

### Changed

- 明确 `website/` 仅为预设产品交互演示，并将模拟构建、烧录和测试结果标记为 `SIMULATED_PASS`，不再呈现为真实 `VERIFIED`。
- 详细说明见 [`docs/updates/2026-09-24-local-report-viewer.md`](docs/updates/2026-09-24-local-report-viewer.md)。

### Fixed

### Deprecated

### Removed

### Security

## [0.1.0] - 2026-09-10

### Added

- 提供 `scan`、`plan`、`run` 三个 CLI 子命令。
- 支持 RT-Thread、GD32F4/STM32F4 以及七类 MVP 外设的工程扫描。
- 建立带来源、证据位置和置信度的 Hardware Fact System。
- 实现关键事实门禁、Adapt First 策略和工程拓扑清单。
- 实现受控构建、烧录、测试、失败分类和有限次数修复。
- 生成 Hardware Manifest、Driver Plan、日志与 Verification Report。
- 提供 Codex Skill、外设测试 Playbook、JSON Schema 和 GD32F470 CAN0 示例。
- 增加 13 项自动化测试，覆盖阻塞、复用规划、恢复和完整状态流转。
- 建立项目文档、更新记录和贡献流程。

详细说明见 [`docs/updates/2026-09-10-mvp.md`](docs/updates/2026-09-10-mvp.md)。

[Unreleased]: https://github.com/Luyuan3014/DriveForge/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Luyuan3014/DriveForge/tree/v0.2.0
[0.1.0]: https://github.com/Luyuan3014/DriveForge/tree/v0.1.0
