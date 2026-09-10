# 开发指南

## 环境

- Python 3.10+
- Windows PowerShell、Linux shell 或 macOS shell
- 核心运行时无第三方依赖
- 测试使用 Python 标准库 `unittest`

从源码运行：

```powershell
python tools/driveforge.py --version
```

可编辑安装：

```powershell
python -m pip install -e .
driveforge --version
```

## 目录结构

```text
DriveForge/
├── src/driveforge/       Python 核心
├── tools/                源码仓库入口
├── schemas/              JSON Schema
├── playbooks/            外设测试准则
├── examples/             可运行配置示例
├── tests/                自动化测试
├── docs/                 架构、配置、路线图和更新记录
├── SKILL.md              Codex Skill 入口
├── DriveForge-PRD.md      产品需求与愿景
└── CHANGELOG.md           版本变更摘要
```

## 运行测试

```powershell
python -m unittest discover -s tests -v
```

发布或推送前还应运行：

```powershell
python -m compileall -q src tools
python tools/driveforge.py --version
```

`compileall` 会产生 `__pycache__`，已被 `.gitignore` 忽略。

## 新增扫描规则

扫描规则应满足：

- 只把可定位的工程内容作为证据；
- 记录相对路径、行号和简短摘录；
- 避免把 README 中的示例误认为唯一硬件事实；
- 限制文件数量、文件大小和候选数量；
- 对无法确认的值保持 `UNKNOWN`，不要构造“看起来合理”的值。

新增规则至少需要一个真实格式的成功样例和一个容易误判的反例测试。

## 新增 MCU 或平台

1. 在 Analyzer 中增加明确识别规则。
2. 在 Resolver 中定义支持边界和派生事实。
3. 为平台特有的引脚、时钟和 IRQ 证据增加测试。
4. 更新 README、Architecture、Configuration 和 Roadmap。
5. 如果支持范围发生产品层变化，同步更新 PRD。
6. 在 `CHANGELOG.md` 的 `Unreleased` 下记录。

不应只删除“unsupported”门禁就宣称支持一个新平台。

## 新增外设

1. 更新 `SUPPORTED_PERIPHERALS`。
2. 定义该外设的关键事实组。
3. 增加工程扫描与参考驱动识别规则。
4. 在 `playbooks/` 中定义设备注册、基础功能、IRQ/DMA、错误恢复和真实硬件验收条件。
5. 更新 Request、Manifest、Plan 和 Report Schema（如字段变化）。
6. 增加成功、缺事实阻塞和最终状态测试。
7. 更新文档与 Changelog。

## 修改工作流状态

`PLANNED`、`BUILD_PASS`、`FLASH_PASS`、`VERIFIED`、`FAIL` 和 `BLOCKED` 是对外契约。修改状态规则时，必须同时审查：

- `runner.final_status`；
- CLI 退出码；
- Verification Report Schema；
- README 状态表；
- 恢复后通过和历史失败保留测试。

## 文档与版本

每次项目更新都必须按 [`update-process.md`](update-process.md) 处理。代码和文档是同一个变更的一部分，不在发布后补写。

版本号定义在 `src/driveforge/models.py` 和 `pyproject.toml`。发布时两处必须一致，同时更新 Changelog 链接和新增详细更新记录。
