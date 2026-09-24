# Changelog

DriveForge 的所有重要变更都记录在此文件中。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

开发中的变更必须先写入 `Unreleased`；发布时再移动到对应版本并补充日期。较大的更新还应在 `docs/updates/` 下增加完整记录。

## [Unreleased]

### Added

- 新增官方落地页与 Web 交互式仿真控制台（`website/`），提供 Antigravity 科技风格相对论黑洞视觉引擎与外设驱动仿真体验。
- 增加基于 CDP 的 Headless 浏览器端到端测试套件（`tools/verify_website.py`）。
- 提供生产级 Nginx 配置、容器化构建（`Dockerfile`、`docker-compose.yml`）及跨平台自动化部署脚本（`deploy.ps1`、`deploy.sh`）。

### Changed

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

[Unreleased]: https://github.com/Luyuan3014/DriveForge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Luyuan3014/DriveForge/tree/v0.1.0
