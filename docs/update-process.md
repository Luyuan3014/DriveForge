# 项目更新与发布流程

本文件是每次 DriveForge 更新的文档检查清单。目标是让任意提交都能从仓库文档中回答：改了什么、为什么改、是否兼容、如何验证、还有什么限制。

## 每次更新都必须做

1. 在 [`CHANGELOG.md`](../CHANGELOG.md) 的 `Unreleased` 对应分类下增加一条摘要。
2. 运行完整自动化测试并记录结果。
3. 检查 README 中的能力范围、示例命令和项目状态是否仍准确。
4. 检查配置、Schema、Playbook、架构和 Roadmap 是否受影响。
5. 确认没有把模拟测试描述成真实硬件验证。
6. 在 Pull Request 中勾选文档检查项。

即使只是文档修正，也要在 `Unreleased / Changed` 或 `Fixed` 下留下记录，确保仓库历史可读。

## 变更与文档映射

| 变更类型 | 必须同步 |
| --- | --- |
| CLI 参数或退出码 | README、Configuration、CLI 测试、Changelog |
| 配置字段或默认值 | Configuration、示例 JSON、Request Schema、测试、Changelog |
| Manifest/Plan/Report 字段 | 对应 Schema、Architecture、测试、Changelog |
| 状态或门禁规则 | README 状态表、Architecture、Configuration、测试、Changelog |
| 新 MCU/RTOS | README、PRD 或 Roadmap、Architecture、测试、Changelog |
| 新外设 | README、Configuration、Playbook、Schema、测试、Roadmap、Changelog |
| 构建/烧录/测试能力 | README、Architecture、Configuration、测试、Changelog |
| 内部重构 | Architecture（职责变化时）、测试、Changelog |
| 安全边界变化 | README、Architecture、Configuration、Changelog |

## 什么时候增加详细更新记录

以下任一情况应在 `docs/updates/YYYY-MM-DD-short-name.md` 增加记录：

- 新版本发布；
- 新平台、新 MCU 或新外设；
- 配置、产物 Schema 或状态语义发生兼容性变化；
- 完成一次真实硬件 Benchmark；
- 修复可能导致错误硬件配置、错误烧录或错误验证结论的问题；
- 变更无法用一条 Changelog 摘要完整解释。

从 [`docs/updates/README.md`](updates/README.md) 复制模板，填写背景、范围、兼容性、验证和限制，并从 Changelog 链接过去。

## 发布版本

1. 确认 `main` 测试通过且 `Unreleased` 内容完整。
2. 按语义化版本确定新版本号。
3. 同步修改 `pyproject.toml` 与 `src/driveforge/models.py`。
4. 把 `Unreleased` 条目移动到 `## [X.Y.Z] - YYYY-MM-DD`。
5. 保留一个新的空 `Unreleased` 区域。
6. 新增详细更新记录并更新 Changelog 底部比较链接。
7. 运行测试、编译检查、CLI 版本检查和文档链接检查。
8. 合并后创建带注释标签 `vX.Y.Z`。
9. 发布说明直接基于 Changelog 和详细更新记录，不另写一份相互漂移的事实源。

## 提交前快速检查

```text
[ ] CHANGELOG 的 Unreleased 已更新
[ ] 用户行为变化已更新 README/Configuration
[ ] 内部职责变化已更新 Architecture
[ ] 支持范围变化已更新 PRD/Roadmap
[ ] Schema、示例和代码保持一致
[ ] 自动化测试通过
[ ] 真实硬件结论附带可追踪证据
[ ] 版本号仅在发布时修改，且两处一致
```
