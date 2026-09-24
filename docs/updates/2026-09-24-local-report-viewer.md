# 2026-09-24：真实产物只读报告页

## 背景

DriveForge 的确定性核心已经输出 Hardware Manifest、Driver Plan、Verification Report 和日志，但用户只能直接阅读 YAML/JSON。与此同时，`website/` 的预设产品演示可能被误解为真实执行结果。

## 变更范围

- 新增 `driveforge view PROJECT`，从已有 `.driveforge` JSON 产物生成并打开 `report.html`。
- 报告页展示硬件事实、证据位置、规划、阶段结果、修改文件、阻塞项、警告和日志链接。
- 为 `website/` 增加全局演示边界说明，并把模拟流程结果标记为 `SIMULATED_PASS`。

## 用户影响

用户先运行 `driveforge plan` 或 `driveforge run`，再运行：

```powershell
driveforge view C:\path\to\rtthread-project
```

`--no-open` 只生成页面，不打开默认浏览器。查看操作不会重新扫描工程，也不会执行构建、烧录或硬件测试。

## 兼容性

该变更向后兼容，不修改配置、既有产物 Schema、工作流状态或退出码。

## 验证

- 自动化测试：新增 CLI 报告生成及 HTML 转义覆盖，完整测试通过。
- 编译检查：`python -m compileall -q src tools` 通过。
- 真实硬件：未进行真实硬件验证；本次变更仅涉及只读展示和演示边界。

## 已知限制

- 报告页是生成时快照，不会自动刷新。
- 页面只读；执行和审批仍通过 CLI 或 Codex Skill 完成。
- `website/` 仍使用预设数据，仅用于产品交互演示。

## 相关文档

- [Changelog](../../CHANGELOG.md)
- [架构](../architecture.md)
- [配置与命令参考](../configuration.md)
