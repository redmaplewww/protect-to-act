# Protect to Act Skill 设计

日期：2026-07-11  
状态：已确认

## 目标

创建并全局安装中文项目管理 Skill `protect-to-act`。该 Skill 在项目根目录建立 `.protect-to-act/`，让 AI 在工作前确认项目路线、工作中维护状态、完成前核对验收要求，同时通过索引和条件读取控制 Token 消耗。

## 安装与可移植性

- 全局安装位置：`$CODEX_HOME/skills/protect-to-act`；未设置 `CODEX_HOME` 时使用 `~/.codex/skills/protect-to-act`。
- Skill 不写死本机路径。
- Skill 自包含中文模板与初始化工具，便于后续复制或分享。
- 创建公开 GitHub 仓库 `redmaplewww/protect-to-act` 并推送交付内容。
- 仓库根目录提供中文 `README.md`，说明用途、安装、触发场景、目录结构和使用示例。

## 项目管理目录

启用后，在项目根目录创建：

```text
.protect-to-act/
├── PROJECT_OVERVIEW.md
├── PROJECT_PROGRESS.md
├── PROJECT_VERSIONS.md
├── PROJECT_FEATURES.md
└── PROJECT_ACCEPTANCE.md
```

各文件职责：

- `PROJECT_OVERVIEW.md`：项目目标、范围、非目标、技术路线、当前阶段、关键约束和按需读取索引。
- `PROJECT_PROGRESS.md`：当前任务、已完成事项、阻塞项、下一步及工作证据。
- `PROJECT_VERSIONS.md`：当前版本、版本历史、变更、兼容性与发布状态。
- `PROJECT_FEATURES.md`：功能清单、优先级、状态、依赖及完成条件。
- `PROJECT_ACCEPTANCE.md`：验收标准、检查结果、证据、遗留问题和验收结论。

## AI 工作协议

### 初始化

1. 确定项目根目录，优先使用版本库根目录；没有版本库时使用当前工作目录。
2. 如果 `.protect-to-act/` 不存在，则创建目录与五份模板。
3. 如果目录已存在，只补齐缺失文件，不覆盖已有内容。

### 读取

1. 每次新工作会话先读 `PROJECT_OVERVIEW.md`。
2. 根据总览中的读取索引，仅打开当前任务相关文件：
   - 规划、实施、阻塞处理：读取 `PROJECT_PROGRESS.md`。
   - 新增、修改或删除功能：读取 `PROJECT_FEATURES.md`。
   - 发布、升级、兼容性或版本变更：读取 `PROJECT_VERSIONS.md`。
   - 测试、交付或完成声明：读取 `PROJECT_ACCEPTANCE.md`。
3. 文件变长后，先搜索标题、状态、功能名或版本号，再局部读取命中段落。
4. 只有跨领域决策或一致性审计才读取全部五份文件。

### 路线保护

- 开工前比较用户请求与项目目标、范围、路线、功能定义和验收条件。
- 请求与记录存在实质冲突时，指出具体冲突及影响，等待用户确认后再改变路线。
- 用户确认改变路线后，同步更新受影响的管理文件，再继续实施。
- 管理文件是工作参考，不替代用户在当前对话中的最新明确指令。

### 更新

在有效工作节点后立即更新相关文件。有效节点包括：

- 目标、范围、约束或技术路线发生变化；
- 功能开始、完成、暂停或取消；
- 发现或解除阻塞；
- 版本号、发布状态或兼容性发生变化；
- 获得测试、验证或验收结果。

更新采用带日期的简短条目并附证据路径或命令结果。保留历史记录；只更新明确标识的“当前状态”字段，不覆盖历史结论。不为普通文件查看、搜索或无状态变化的命令创建日志。

## Skill 结构

```text
protect-to-act/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── init_project_management.py
└── assets/
    └── templates/
        ├── PROJECT_OVERVIEW.md
        ├── PROJECT_PROGRESS.md
        ├── PROJECT_VERSIONS.md
        ├── PROJECT_FEATURES.md
        └── PROJECT_ACCEPTANCE.md
```

初始化脚本只负责安全创建目录、复制缺失模板和报告结果；AI 负责结合项目事实填写及维护内容。脚本重复运行必须保持已有文件不变。

## GitHub 仓库结构

```text
protect-to-act-repository/
├── README.md
├── docs/
│   └── protect-to-act-design.md
└── protect-to-act/
    └── （完整 Skill）
```

`README.md` 属于分享仓库，不放入 `protect-to-act/` Skill 目录，避免给运行时 Skill 增加无关文件。README 使用中文，提供通过仓库复制安装的说明，并明确默认在项目根目录创建 `.protect-to-act/`。

## 错误处理

- 无法确定项目根目录时，使用当前工作目录并明确说明。
- 管理文件格式损坏时，不自动覆盖；报告问题并进行最小修复。
- 内容互相矛盾时，以当前用户明确指令为最高优先级，并在相关文件中记录已确认的变更。
- 写入失败时，报告文件路径和错误，不声称状态已经更新。

## 验证标准

- Skill 目录结构和 YAML 元数据通过官方快速验证脚本。
- 初始化脚本能在空目录创建五份文件。
- 初始化脚本重复运行不修改已有文件。
- 已存在部分文件时只补齐缺失文件。
- 模板不包含无法解释的占位符，且职责之间没有重复冲突。
- 场景测试证明 AI 会先读总览、按任务读取相关文件、在有效节点更新文件，并在完成声明前核对验收标准。
- `SKILL.md` 保持精简，详细模板不默认加载进上下文。

## 范围边界

本次创建、验证并全局安装 Skill，同时创建公开 GitHub 仓库并推送 README、设计文档和 Skill。不自动改造现有项目，不发布到 Slack 或市场。
