# Contributing to DriveForge

感谢参与 DriveForge。项目仍处于 MVP 阶段，任何变更都应优先维护硬件事实可追踪、执行边界明确以及最终状态可信这三个不变量。

## 开发流程

1. 从最新的 `main` 创建短生命周期分支。
2. 先确认变更属于当前 MVP 范围，范围变化需要同步更新 PRD 或 Roadmap。
3. 实现最小变更，并为新增行为或修复补充测试。
4. 运行 `python -m unittest discover -s tests -v`。
5. 在 [`CHANGELOG.md`](CHANGELOG.md) 的 `Unreleased` 下记录本次更新。
6. 按 [`docs/update-process.md`](docs/update-process.md) 检查是否需要同步 README、架构、配置、Schema、Playbook 或详细更新记录。
7. 提交 Pull Request，并完整填写仓库模板。

## 提交信息

推荐使用清晰的前缀：

- `feat:` 新能力；
- `fix:` 缺陷修复；
- `docs:` 文档更新；
- `test:` 测试变更；
- `refactor:` 不改变外部行为的重构；
- `chore:` 构建或维护工作。

一个提交应表达一个可以独立解释和回滚的意图。不要把无关的格式化、重构和功能修改混在一起。

## 行为要求

- 不得用模型记忆补全硬件事实。
- 新增硬件事实来源时，必须保留来源、置信度和证据位置。
- 新增可执行命令时，必须由用户配置并通过明确开关启用。
- `BUILD_PASS`、`FLASH_PASS` 和 `VERIFIED` 不得互相替代。
- 修复循环必须有明确的次数上限。
- 修改配置或报告格式时，应同步更新对应 Schema 和文档。

## 测试要求

至少覆盖新增行为的成功路径和一个关键失败路径。涉及硬件状态时，自动化测试可以使用模拟命令验证工作流，但文档和报告必须明确区分模拟结果与真实板卡验证。

真实硬件测试记录应包含目标板、MCU、RT-Thread 版本、探针、固件版本、连接方式、测试命令和原始日志位置。
