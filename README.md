# Protect to Act

`protect-to-act` 是一个面向 AI 编程代理的中文项目管理 Skill。它在项目中维护一组可追溯的 Markdown 文件，让 AI 在实施前核对路线、工作中同步状态、完成前检查验收证据，同时通过条件读取减少不必要的 Token 消耗。

## 核心价值

- 路线保护：识别请求与项目目标、范围、非目标或验收标准的冲突。
- 持久上下文：把项目进度、版本、功能和验收状态保存在项目内。
- 按需读取：每次会话只读总览，再根据任务类型打开相关文件。
- 安全维护：只补齐缺失模板，不覆盖已有项目记录。
- 证据优先：没有测试或验收证据时，不把项目写成已完成。

## 项目文件

启用后，Skill 在项目根目录创建：

```text
.protect-to-act/
├── PROJECT_OVERVIEW.md
├── PROJECT_PROGRESS.md
├── PROJECT_VERSIONS.md
├── PROJECT_FEATURES.md
└── PROJECT_ACCEPTANCE.md
```

| 文件 | 用途 |
|---|---|
| `PROJECT_OVERVIEW.md` | 目标、范围、非目标、路线、约束与读取索引 |
| `PROJECT_PROGRESS.md` | 当前任务、阻塞、下一步与进度证据 |
| `PROJECT_VERSIONS.md` | 当前版本、发布状态、兼容性与版本历史 |
| `PROJECT_FEATURES.md` | 功能清单、优先级、状态、依赖与完成条件 |
| `PROJECT_ACCEPTANCE.md` | 验收标准、检查结果、证据与最终结论 |

## 安装

### 通过 Git 克隆

```powershell
git clone https://github.com/redmaplewww/protect-to-act.git
Copy-Item -Recurse -Force .\protect-to-act\protect-to-act "$HOME\.codex\skills\protect-to-act"
```

复制后重新打开 Codex，让全局 Skill 被重新发现。

### 手动安装

下载仓库后，将仓库中的 `protect-to-act/` 文件夹复制到：

```text
~/.codex/skills/protect-to-act/
```

## 使用

显式调用示例：

```text
使用 $protect-to-act 初始化并维护当前项目的管理文档。
```

也可以直接提出项目规划、功能开发、版本发布、验收或进度维护请求；当任务符合 Skill 描述时，Codex 可以自动加载它。

初始化脚本可单独运行：

```powershell
python "$HOME\.codex\skills\protect-to-act\scripts\init_project_management.py" --project-root "D:\path\to\project"
```

脚本返回创建与跳过的文件列表。重复运行不会覆盖已有文件。

## 按需读取规则

| 任务 | 读取范围 |
|---|---|
| 每次新会话 | 只读总览 |
| 规划、实施、阻塞处理 | 总览 + 进度 |
| 功能变化 | 总览 + 功能；实施时加进度 |
| 版本或发布变化 | 总览 + 版本 |
| 测试、交付或完成声明 | 总览 + 验收 |
| 跨领域路线变更 | 全部文件做一致性审计 |

文件较长时，AI 会先搜索标题、状态、功能名或版本号，再读取命中段落，而不是默认加载全文。

## 安全更新原则

- 目标、范围、功能、阻塞、版本或验收结果发生实际变化后才更新。
- 历史区追加带日期的变化、原因和证据，不覆盖旧决定。
- 当前请求与既有路线冲突时，先说明影响并等待用户确认。
- 写入失败、测试跳过或验收不通过时，如实报告，不声称成功。

## 仓库结构

```text
.
├── README.md
├── docs/
├── protect-to-act/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/init_project_management.py
│   └── assets/templates/
└── tests/
```

## 验证

```powershell
python -m unittest discover -s tests -v
$env:PYTHONUTF8='1'
python "$HOME\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\protect-to-act
```

## 许可证

当前仓库尚未指定开源许可证。公开仓库可供查看和评估；如需正式再分发，请由仓库所有者补充许可证。
