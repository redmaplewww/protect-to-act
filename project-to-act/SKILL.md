---
name: project-to-act
description: Use when an AI starts, plans, implements, tracks, changes scope, releases, tests, accepts, or completes project work that needs durable Markdown context, project progress, version history, feature status, acceptance criteria, route protection, or token-efficient retrieval.
---

# Project to Act

## 核心契约

把 `.project-to-act/` 作为项目路线的持久参考。每次会话只以总览为入口；任务条件决定是否扩读。当前用户的明确指令优先，但不得静默改写既有路线或伪造完成证据。

## 初始化

1. 优先用 Git 仓库根目录；无仓库时用当前工作目录，并说明该选择。
2. 若 `.project-to-act/` 不存在或文件不齐，运行本 Skill 的 `scripts/init_project_management.py --project-root <项目根目录>`。脚本只补缺，不覆盖。
3. 首次使用时根据现有代码、文档和用户确认填写真实内容；未知项保持未定义，不猜测。

## 会话工作流

1. 开始工作时只读 `PROJECT_OVERVIEW.md`，核对目标、范围、非目标、路线、约束和当前焦点。
2. 按任务追加读取：

| 可观察任务条件 | 追加读取 |
|---|---|
| 规划、实施、阻塞处理 | `PROJECT_PROGRESS.md` |
| 新增、修改、删除功能 | `PROJECT_FEATURES.md`；实施时同时读进度 |
| 版本号、发布、升级、兼容性变化 | `PROJECT_VERSIONS.md` |
| 测试、交付、验收、完成声明 | `PROJECT_ACCEPTANCE.md` |
| 跨领域路线变更或一致性审计 | 全部五份文件 |

3. 文件变长时先搜索功能名、版本号、状态或二级标题，只读命中段落。文件数量少或内容“可能相关”都不是扩读条件。
4. 开工前发现请求与既有目标、非目标、范围或验收标准实质冲突时，指出冲突与影响。获得用户确认后，先同步受影响文档，再实施新路线。
5. 在有效工作节点后立即更新相关文件：目标或范围变化、功能状态变化、阻塞变化、版本变化、测试或验收结果。普通查看、搜索和无状态变化的命令不记账。
6. 只修改明确的当前状态字段；历史区按时间倒序追加日期、变化、原因和证据。不得覆盖旧决定，不得把未验证状态写成已完成。

## 完成门槛

声明任务或项目完成前，读取 `PROJECT_ACCEPTANCE.md`，运行适用验证并记录新鲜证据。验收条件未满足、测试被跳过或写入失败时，准确报告未完成状态，不得声称已更新或已通过。

## 常见错误

- 为求安心读取全部文件：改用任务条件表。
- 每条命令都更新进度：只记录有效工作节点。
- 用户改变路线后直接开工：先记录已确认的路线变化。
- 用“看起来可用”替代验收：保存命令、结果、退出状态或其他可复核证据。

## 简例

用户要求修改一个已有功能时：读总览、功能和进度；修改并验证后更新功能状态与进度历史。只有涉及版本或发布工作时才读版本文件；只要代理将要声称任务或项目完成，就必须读验收文件并核对证据，不取决于用户是否使用了“完成”措辞。
