# Protect to Act Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建、验证并全局安装中文项目管理 Skill `protect-to-act`，然后推送到公开仓库 `redmaplewww/protect-to-act`。

**Architecture:** Skill 用精简 `SKILL.md` 定义路线保护、条件读取与更新协议；五份 Markdown 模板存放在 `assets/templates/`，由无覆盖初始化脚本复制到项目根目录的 `.protect-to-act/`。分享仓库用根级 README 和 docs 包装完整 Skill，避免将分享文档混入运行时目录。

**Tech Stack:** Markdown、YAML、Python 3 标准库、`unittest`、Codex Skill 初始化/验证脚本、Git、GitHub CLI。

## Global Constraints

- Skill 名固定为 `protect-to-act`，项目管理目录固定为 `.protect-to-act/`。
- 所有项目管理模板与仓库 README 使用中文。
- 已存在的项目管理文件不得覆盖，只补齐缺失文件。
- 每次会话默认只读 `PROJECT_OVERVIEW.md`，其他文件按任务条件读取。
- 只在有效工作节点更新文件，历史记录采用追加方式保留。
- 完成声明前必须读取 `PROJECT_ACCEPTANCE.md` 并核对证据。
- Skill 不写死本机路径，可从 GitHub 分享安装。

---

### Task 1: 行为基线测试

**Files:**
- Create: `work/tests/baseline-scenarios.md`
- Create: `work/tests/baseline-results.md`

**Interfaces:**
- Consumes: 已确认设计文档中的预期行为。
- Produces: 未加载 Skill 时 AI 的具体失败模式，用于约束 `SKILL.md`。

- [x] **Step 1: 写三个隔离场景**

场景分别施加 Token 压力、赶工压力和既有文件保护压力，要求代理说明会读取哪些文件、何时更新、遇到路线冲突如何处理。

- [x] **Step 2: 用未加载 Skill 的子代理运行场景**

Expected: 至少出现一项失败，例如全量读取、每条命令都写日志、跳过验收文件、覆盖已有项目文件或未指出路线冲突。

- [x] **Step 3: 记录原始结论**

`baseline-results.md` 必须包含每个场景的读取决策、更新决策、路线保护决策和失败判定。

### Task 2: 初始化工具的 TDD 实现

**Files:**
- Create: `repo/tests/test_init_project_management.py`
- Create: `repo/protect-to-act/scripts/init_project_management.py`
- Create: `repo/protect-to-act/assets/templates/PROJECT_OVERVIEW.md`
- Create: `repo/protect-to-act/assets/templates/PROJECT_PROGRESS.md`
- Create: `repo/protect-to-act/assets/templates/PROJECT_VERSIONS.md`
- Create: `repo/protect-to-act/assets/templates/PROJECT_FEATURES.md`
- Create: `repo/protect-to-act/assets/templates/PROJECT_ACCEPTANCE.md`

**Interfaces:**
- Consumes: `--project-root PATH`，模板目录相对脚本位置解析。
- Produces: `initialize(project_root: Path) -> dict[str, list[str]]`，包含 `created` 与 `skipped` 文件名列表；CLI 成功返回 0。

- [x] **Step 1: 先写失败测试**

测试覆盖：空目录创建五份文件；重复运行保留自定义内容；部分存在时仅补齐缺失文件；普通文件根路径、模板缺失、目标目录或符号链接碰撞、复制失败清理、CLI JSON/错误输出与并发独占创建。

- [x] **Step 2: 验证 RED**

Run: `python -m unittest discover -s repo/tests -v`

Expected: FAIL，原因是 `init_project_management.py` 尚不存在。

- [x] **Step 3: 写最小实现**

实现使用 Python 标准库。先读取全部模板完成类型与可读性预检，再创建管理目录；拒绝非常规目标碰撞；用 `Path.open("xb")` 独占创建后通过 `copyfileobj` 复制，失败时清理本次新建目标；输出 UTF-8 JSON 报告；不提供覆盖开关。

- [x] **Step 4: 验证 GREEN**

Run: `python -m unittest discover -s repo/tests -v`

Expected: Windows 上 17 tests PASS，无警告或跳过；非 Windows 平台仅跳过 junction 专用回归测试。

### Task 3: Skill 主协议与元数据

**Files:**
- Create: `repo/protect-to-act/SKILL.md`
- Create: `repo/protect-to-act/agents/openai.yaml`

**Interfaces:**
- Consumes: Task 1 的失败模式、Task 2 的初始化 CLI。
- Produces: 可由 Codex 隐式触发的 Skill，默认提示明确使用 `$protect-to-act`。

- [x] **Step 1: 用官方脚手架初始化 Skill 外壳**

Run: `python C:/Users/redmaple/.codex/skills/.system/skill-creator/scripts/init_skill.py protect-to-act --path repo --resources scripts,assets --interface display_name="Protect to Act" --interface short_description="用项目管理文档保护工作路线并按需维护状态" --interface default_prompt="使用 $protect-to-act 初始化并维护当前项目的管理文档。"`

Expected: 生成合法 frontmatter 与 `agents/openai.yaml`；与 Task 2 文件冲突时先在空临时位置生成，再合并元数据，不覆盖已测试文件。

- [x] **Step 2: 写最小 `SKILL.md`**

内容必须明确：根目录选择、首次初始化、会话读取路由、局部搜索、有效工作节点、追加历史、冲突升级、完成前验收、写入失败不得声称成功。快速参考表映射四类任务到对应文件。

- [x] **Step 3: 生成 UI 元数据**

`openai.yaml` 只包含 `interface.display_name`、`short_description`、`default_prompt`；所有字符串加引号，默认提示显式包含 `$protect-to-act`。

- [x] **Step 4: 快速验证 Skill**

Run: `$env:PYTHONUTF8='1'; python C:/Users/redmaple/.codex/skills/.system/skill-creator/scripts/quick_validate.py repo/protect-to-act`

Expected: validation passed。

### Task 4: 前向行为测试与修订

**Files:**
- Create: `work/tests/forward-results.md`
- Modify: `repo/protect-to-act/SKILL.md`（仅在测试发现漏洞时）

**Interfaces:**
- Consumes: Task 1 的相同场景与完整 Skill 路径。
- Produces: 证明条件读取、路线保护、无覆盖更新和验收门槛均生效的测试记录。

- [x] **Step 1: 用加载 Skill 的隔离子代理重跑场景**

Expected: 默认只读总览；按任务打开相关文件；不为普通命令写日志；路线冲突先报告；完成前核对验收。

- [x] **Step 2: 对新漏洞做最小修订**

若代理仍全量读取、覆盖文件或跳过验收，将其原始理由加入“常见错误”并补充可观察条件；不得增加与失败无关的规则。

- [ ] **Step 3: 重跑直到通过**

Expected: 所有场景满足设计中的读取、更新、路线保护与验收条件。

### Task 5: 分享仓库、全局安装与推送

**Files:**
- Create: `repo/README.md`
- Create: `repo/docs/protect-to-act-design.md`
- Create: `repo/docs/superpowers/plans/2026-07-11-protect-to-act.md`
- Install: `C:/Users/redmaple/.codex/skills/protect-to-act/`

**Interfaces:**
- Consumes: 已验证 Skill 和设计/计划文档。
- Produces: 全局可发现 Skill 与公开 GitHub 仓库 URL。

- [x] **Step 1: 写中文 README**

README 包含：核心价值、五份项目文件说明、按需读取规则、安装命令、调用示例、安全更新行为、仓库结构和许可证说明。README 不放入 Skill 子目录。

- [ ] **Step 2: 安装到全局目录**

先确认目标不存在；复制完整 `repo/protect-to-act` 到 `C:/Users/redmaple/.codex/skills/protect-to-act`。再次运行 `quick_validate.py` 验证安装副本。

- [ ] **Step 3: 运行交付验证**

Run: `python -m unittest discover -s repo/tests -v`

Run: `$env:PYTHONUTF8='1'; python C:/Users/redmaple/.codex/skills/.system/skill-creator/scripts/quick_validate.py C:/Users/redmaple/.codex/skills/protect-to-act`

Expected: 所有测试通过且 Skill 验证通过。

- [x] **Step 4: 初始化 Git 并提交**

Run: `git -C repo init -b main`

Run: `git -C repo add README.md docs protect-to-act tests`

Run: `git -C repo commit -m "feat: add protect-to-act project management skill"`

Expected: 工作树干净，提交包含 README、设计、计划、Skill 与测试。

- [ ] **Step 5: 创建公开仓库并推送**

Run: `gh repo create redmaplewww/protect-to-act --public --source repo --remote origin --push --description "中文 AI 项目管理 Skill：按需读取项目文档，保护项目路线并持续维护状态"`

Expected: 创建 `https://github.com/redmaplewww/protect-to-act`，`main` 分支与本地 HEAD 一致。
