# ssd-workflow 插件 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新建 ssd-workflow 插件，以 4 阶段（propose/plan/apply/archive）+ 主入口的纯文档编排，缝合 OpenSpec(WHAT) 与 Superpowers(HOW)，填补「task 没落实到实处」的缺口，并取代旧 openspec-workflow 插件。

**Architecture:** 纯 SKILL.md 驱动，零脚本、零状态文件。when 靠阶段化 skill 首尾衔接 + 主入口用产物存在性判阶段；how 靠 ssd-plan 产出 implementation plan + ssd-apply 强制读 plan。参考 comet 的阶段化技能拆分，但去除其全部脚本与状态机。

**Tech Stack:** Claude Code 插件（SKILL.md + plugin.json + marketplace.json），无构建/测试/lint。

## Global Constraints

- 纯 SKILL.md 驱动：不创建 reference.md、不创建 scripts/、不创建任何状态文件（.yaml/.json 状态）
- skill 命名前缀统一 `ssd-`，目录 kebab-case
- 每个 SKILL.md 的 frontmatter 必须含 `name` 和 `description`
- SKILL.md 用简体中文撰写，技术术语保留英文
- 遵循 markdown 规范：标题/代码块前后空行、文件以单一换行结尾、代码块指定语言（流程图用 `text`）
- plugin.json 的 version 从 `1.0.0` 起步
- ssd-plan 产出的 plan 文件命名 `YYYY-MM-DD-<change-name>.md`，放 `docs/superpowers/plans/`
- 所有 git 命令用 `git -C "D:/Develop/Project/cj-cc-marketplace"`，stage 具体文件，commit 遵循 `type(ssd-workflow): 描述`

---

## File Structure

**新建：**

- `ssd-workflow/.claude-plugin/plugin.json` — 插件清单（name/version/author）
- `ssd-workflow/skills/ssd/SKILL.md` — 主入口：流程导航（产物判阶段）
- `ssd-workflow/skills/ssd-propose/SKILL.md` — 阶段 1 WHAT（吸收 brainstorming-to-propose）
- `ssd-workflow/skills/ssd-plan/SKILL.md` — 阶段 2 HOW（填补痛点核心）
- `ssd-workflow/skills/ssd-apply/SKILL.md` — 阶段 3 执行（吸收 apply-with-superpowers 路由表 + plan-aware）
- `ssd-workflow/skills/ssd-archive/SKILL.md` — 阶段 4 归档

**修改：**

- `.claude-plugin/marketplace.json` — 注册 ssd-workflow，移除 openspec-workflow
- `CLAUDE.md` — 仓库结构中 openspec-workflow 条目替换为 ssd-workflow
- `AGENTS.md` — 仓库结构中新增 ssd-workflow 条目

**删除：**

- `openspec-workflow/` 整个目录（在 ssd-propose/ssd-apply 吸收其内容之后）

---

### Task 1: 插件骨架与 plugin.json

**Files:**

- Create: `ssd-workflow/.claude-plugin/plugin.json`

**Interfaces:**

- Produces: 插件清单，后续 Task 2-6 的 skill 都归属此插件；marketplace.json（Task 7）按 `./ssd-workflow` source 注册

- [ ] **Step 1: 创建 plugin.json**

写入 `ssd-workflow/.claude-plugin/plugin.json`，结构对齐现有 `openspec-workflow/.claude-plugin/plugin.json`：

```json
{
  "name": "ssd-workflow",
  "description": "Spec-Driven Development 工作流编排插件：OpenSpec(WHAT) × Superpowers(HOW) × ssd-workflow(WHEN)",
  "version": "1.0.0",
  "repository": "https://github.com/changju-web/cj-cc-marketplace",
  "author": {
    "name": "wangjiahui",
    "email": "13226651554@163.com",
    "url": "https://github.com/TurtleWXG"
  }
}
```

- [ ] **Step 2: 验证 JSON 合法性**

Run: `node -e "JSON.parse(require('fs').readFileSync('D:/Develop/Project/cj-cc-marketplace/ssd-workflow/.claude-plugin/plugin.json','utf8')); console.log('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ssd-workflow/.claude-plugin/plugin.json
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 初始化插件骨架与 plugin.json"
```

---

### Task 2: ssd-propose skill（阶段 1 WHAT）

**Files:**

- Create: `ssd-workflow/skills/ssd-propose/SKILL.md`

**Interfaces:**

- Consumes: `superpowers:brainstorming`（需求探索）、`/opsx:propose`（生成提案）
- Produces: `openspec/changes/<change-name>/` 下的 proposal/spec/design/tasks；完成后引导调用 `ssd-plan`
- 吸收自：`openspec-workflow/skills/brainstorming-to-propose/SKILL.md`（末尾指向从「/opsx:apply」改为「ssd-plan」，禁止调用 writing-plans）

- [ ] **Step 1: 创建 ssd-propose/SKILL.md**

写入完整内容（frontmatter + 正文）。末尾必须引导 `/ssd-plan`，禁止跳过 plan 直接实现：

````markdown
---
name: ssd-propose
description: "SSD 工作流阶段 1（WHAT）：将 brainstorming 的需求探索结论流转为 OpenSpec 正式提案。当项目存在 OpenSpec 且用户提出新功能/新页面/新模块开发需求时使用。完成后引导进入阶段 2（ssd-plan）。关键词：'新功能'、'新页面'、'新模块'、'需求开发'、'做个 xxx'。"
---

# SSD 阶段 1：Propose（做什么）

将 brainstorming 的需求探索结论流转为 OpenSpec 正式提案，产出 proposal / spec / design / tasks，然后引导进入阶段 2（ssd-plan）细化「怎么做」。

## 在 SSD 工作流中的位置

```text
[本 skill] ssd-propose     → 阶段 1 WHAT（做什么）
[下一阶段] ssd-plan        → 阶段 2 HOW（怎么做）
[之后]     ssd-apply       → 阶段 3 执行
[最后]     ssd-archive     → 阶段 4 归档
```

本 skill 只负责阶段 1。完成后必须引导用户进入 ssd-plan，而不是直接开始实现。

## 触发方式

### 1. 显式调用（最稳定）

/ssd-workflow:ssd-propose 或简写 /ssd-propose

### 2. 自动触发（语义匹配）

当满足以下条件时主动调用：

- 项目存在 OpenSpec
- 用户提出新功能、新页面、新模块开发需求
- 用户处于功能开发初期阶段（澄清需求、比较方案）

不确定时优先使用显式调用。

## 流程

```text
用户提出功能需求
       ↓
[1] brainstorming 需求探索
       ↓ 硬确认门
[2] 整理结构化摘要
       ↓ 自动流转
[3] /opsx:propose 创建提案
       ↓ 人工审核门
[4] 用户审核并确认
       ↓
[5] 引导进入 ssd-plan（阶段 2）
```

### 阶段 1：brainstorming

调用 `superpowers:brainstorming` skill，但遵循以下约束：

**允许：**

- 澄清需求、目标和约束
- 收敛方案边界、比较可选方案并给出推荐
- 探索技术方案和数据模型
- 产出供 `/opsx:propose` 使用的结构化输入

**禁止：**

- 将结论写入 `docs/superpowers/specs/*`
- 生成与 OpenSpec proposal/spec/design 平级的替代性正式文档
- 调用 `writing-plans` skill（「怎么做」由阶段 2 ssd-plan 接管）

**完成标志：** 需求目标已澄清、方案已比较并选出推荐、用户对推荐方向无异议。

此时暂停，输出确认提示：

> 需求探索阶段完成，结论摘要：
>
> - **目标**：<一句话>
> - **范围**：<做什么 / 不做什么>
> - **推荐方案**：<方案名 + 理由>
> - **核心约束**：<关键限制>
>
> 确认后将进入 `/opsx:propose` 创建正式提案。是否继续？

用户明确肯定后才进入阶段 2。

### 阶段 1 产出

| 产出项 | 内容 | 对应 OpenSpec artifact |
| --- | --- | --- |
| 功能目标 | 一句话描述要做什么、为什么 | proposal.md 的 Why |
| 范围与约束 | 做什么、不做什么 | proposal.md 的 Scope |
| 行为规格 | 用户可见行为、边界条件、错误处理 | spec.md |
| 推荐方案 | 技术选型和理由 | design.md 的依据 |
| 实体与字段 | 核心数据模型 | design.md 的数据设计 |
| API 接口 | 路径、方法、参数、响应（如有） | design.md 的接口设计 |
| 任务拆分建议 | 按阶段/模块拆分的实现步骤 | tasks.md 的依据 |

若用户提供 Swagger/Knife4j URL 或 OpenAPI JSON，一并记录。

### 阶段 2：整理结构化摘要

用户确认后，整理：

1. change-name（kebab-case）
2. proposal 内容
3. spec 内容
4. design 内容
5. tasks 雏形

本 skill 不直接写 OpenSpec 文件，只准备输入。

### 阶段 3：/opsx:propose

调用 `/opsx:propose`，由其在 `openspec/changes/<change-name>/` 下生成 proposal.md / spec.md / design.md / tasks.md。

### 阶段 4：人工审核门

必须暂停等待用户确认：

> OpenSpec 提案已创建在 `openspec/changes/<change-name>/`，请审核：
>
> 1. proposal.md — 需求描述是否准确
> 2. spec.md — 行为规格是否完整
> 3. design.md — 技术方案是否合理
> 4. tasks.md — 任务拆分是否完整
>
> 确认后进入阶段 2（ssd-plan）细化「怎么做」。

只有用户明确同意后才算完成。

### 阶段 5：引导进入 ssd-plan（与旧 brainstorming-to-propose 的关键差异）

审核通过后，输出明确的下一步指引：

> 阶段 1（WHAT）完成。tasks.md 描述了「做什么」，但尚未细化「怎么做」。
>
> 下一步：调用 /ssd-plan，基于本提案产出 implementation plan（docs/superpowers/plans/YYYY-MM-DD-<change-name>.md），把每个 task 细化成具体实现步骤。

不得跳过 ssd-plan 直接进入实现。

## 项目没有 OpenSpec 时

仅执行阶段 1 的需求澄清与方案比较，不生成正式文档。提示：

> 项目未检测到 OpenSpec。建议先初始化 OpenSpec，再使用 SSD 工作流。

## 边界

- 不写 implementation plan（归 ssd-plan）
- 不路由执行纪律（归 ssd-apply）
- 不管理 change 归档（归 ssd-archive）
````

- [ ] **Step 2: 验证契约（对照设计文档）**

确认 SKILL.md 满足：
- frontmatter 含 `name: ssd-propose` 和 `description`
- 流程含 5 阶段，阶段 5 显式引导 `/ssd-plan`
- 禁止项含「调用 writing-plans」
- 含「项目没有 OpenSpec 时」降级

Run: `grep -c "ssd-plan" "D:/Develop/Project/cj-cc-marketplace/ssd-workflow/skills/ssd-propose/SKILL.md"`
Expected: `>= 2`（流程图 + 阶段 5 引导）

- [ ] **Step 3: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ssd-workflow/skills/ssd-propose/SKILL.md
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 新增 ssd-propose skill（阶段 1 WHAT）"
```

---

### Task 3: ssd-plan skill（阶段 2 HOW）

**Files:**

- Create: `ssd-workflow/skills/ssd-plan/SKILL.md`

**Interfaces:**

- Consumes: `openspec/changes/<change-name>/`（proposal/spec/design/tasks，来自 ssd-propose）、`superpowers:writing-plans`
- Produces: `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`；完成后引导调用 `ssd-apply`
- 这是填补「task 没落实到实处」的核心 skill

- [ ] **Step 1: 创建 ssd-plan/SKILL.md**

写入完整内容：

````markdown
---
name: ssd-plan
description: "SSD 工作流阶段 2（HOW）：基于已审核的 OpenSpec 提案，调用 superpowers:writing-plans 产出 implementation plan，把抽象的 tasks 细化为具体的实现步骤。当 OpenSpec change 的 tasks.md 已生成且用户审核通过、需要明确「怎么做」时使用。完成后引导进入阶段 3（ssd-apply）。"
---

# SSD 阶段 2：Plan（怎么做）

填补 OpenSpec tasks.md「只说做什么、没说怎么做」的缺口。读取已审核的提案，调用 `superpowers:writing-plans` 产出 implementation plan。

## 在 SSD 工作流中的位置

```text
[上一阶段] ssd-propose  → 阶段 1 WHAT（做什么）
[本 skill] ssd-plan     → 阶段 2 HOW（怎么做）
[下一阶段] ssd-apply    → 阶段 3 执行
[最后]     ssd-archive  → 阶段 4 归档
```

## 触发方式

/ssd-workflow:ssd-plan 或简写 /ssd-plan

也可由 ssd-propose 审核通过后引导调用，或由 ssd 主入口根据产物判阶段后引导。

## 前置检查（审核门即前置检查）

开始前必须验证：

1. 当前 change 的 proposal/spec/design/tasks 已生成（`openspec/changes/<change-name>/` 存在且四件套齐全）
2. 用户已审核通过提案

若不满足，暂停并提示：

> 阶段 2 需要已审核的提案。当前未检测到完整提案，请先调用 /ssd-propose 完成阶段 1。

## 流程

```text
前置检查：提案已审核
       ↓
[1] 读取 proposal / spec / design / tasks 作为输入
       ↓
[2] 调用 superpowers:writing-plans
       ↓
[3] 产出 docs/superpowers/plans/YYYY-MM-DD-<change-name>.md
       ↓
[4] 人工审核门：用户审核 plan
       ↓
[5] 引导进入 ssd-apply（阶段 3）
```

### 阶段 1：读取提案

读取 `openspec/changes/<change-name>/` 下的：

- proposal.md — 目标、范围
- spec.md — 行为规格、边界条件
- design.md — 技术方案、数据模型、接口
- tasks.md — 任务清单（「做什么」的粒度）

将这些作为 writing-plans 的输入上下文。

### 阶段 2：调用 writing-plans

调用 `superpowers:writing-plans`，传入：

- 提案内容作为 spec/requirements
- change-name 作为 feature-name

**plan 粒度策略：**

- 默认 change 级：一个 change 一份 plan，内部按 task 组织实现步骤
- change 过大时，由 writing-plans 自行判断拆分为多份 plan，文件名仍以 change-name 关联

### 阶段 3：产出 plan

plan 文件位置与命名：

```text
docs/superpowers/plans/YYYY-MM-DD-<change-name>.md
```

遵循 Superpowers 的 plans 目录命名风格，change-name 部分与 `openspec/changes/<change-name>/` 一一对应。

### 阶段 4：人工审核门

必须暂停等待用户确认：

> implementation plan 已生成：`docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`
>
> 请审核：
>
> 1. 每个 task 的实现步骤是否具体可执行（动哪些文件、什么接口、什么顺序）
> 2. task 拆分粒度是否合理
> 3. 是否覆盖 tasks.md 的所有任务
>
> 确认后进入阶段 3（ssd-apply）按 plan 实现。

### 阶段 5：引导进入 ssd-apply

审核通过后，输出明确的下一步指引：

> 阶段 2（HOW）完成。「怎么做」已细化为 implementation plan。
>
> 下一步：调用 /ssd-apply，按 plan 逐 task 实现。ssd-apply 会强制先读 plan，确保实现不偏离。

## 边界

- 不重写提案（归 OpenSpec / ssd-propose）
- 不执行实现（归 ssd-apply）
- plan 产出后不自动进入实现，必须经用户审核
````

- [ ] **Step 2: 验证契约**

确认 SKILL.md 满足：
- frontmatter 含 `name: ssd-plan`
- 前置检查要求「proposal/spec/design/tasks 四件套齐全 + 用户审核」
- plan 路径明确为 `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`
- 阶段 5 显式引导 `/ssd-apply`

Run: `grep -c "YYYY-MM-DD-<change-name>" "D:/Develop/Project/cj-cc-marketplace/ssd-workflow/skills/ssd-plan/SKILL.md"`
Expected: `>= 3`

- [ ] **Step 3: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ssd-workflow/skills/ssd-plan/SKILL.md
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 新增 ssd-plan skill（阶段 2 HOW）"
```

---

### Task 4: ssd-apply skill（阶段 3 执行）

**Files:**

- Create: `ssd-workflow/skills/ssd-apply/SKILL.md`

**Interfaces:**

- Consumes: `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`（来自 ssd-plan）、`openspec/changes/<change-name>/tasks.md`
- Produces: 代码实现 + tasks.md 勾选；完成后引导调用 `ssd-archive`
- 吸收自：`openspec-workflow/skills/apply-with-superpowers/SKILL.md` 的执行纪律路由表，叠加 plan-aware 前置检查

- [ ] **Step 1: 创建 ssd-apply/SKILL.md**

写入完整内容：

````markdown
---
name: ssd-apply
description: "SSD 工作流阶段 3（执行）：按 implementation plan 逐 task 实现，每个 task 内路由 Superpowers 执行纪律（TDD/debugging/verify/code-review）。当 plan 已生成且用户审核通过、准备开始写代码时使用。强制先读 plan，防止「写完不看的死文档」。完成后引导进入阶段 4（ssd-archive）。"
---

# SSD 阶段 3：Apply（按 plan 实现）

按 implementation plan 逐 task 实现。强制先读 plan，每个 task 内路由 Superpowers 执行纪律，完成一个 task 勾选 tasks.md，全部完成后引导归档。

## 在 SSD 工作流中的位置

```text
[上一阶段] ssd-plan    → 阶段 2 HOW（怎么做）
[本 skill] ssd-apply   → 阶段 3 执行（按 plan 实现）
[下一阶段] ssd-archive → 阶段 4 归档
```

## 触发方式

/ssd-workflow:ssd-apply 或简写 /ssd-apply

也可由 ssd-plan 审核通过后引导调用，或由 ssd 主入口根据产物判阶段后引导。

## 前置检查（plan-aware 的关键）

开始前必须验证 plan 存在：

1. 定位 `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`
2. 若不存在，暂停并提示：

> 阶段 3 需要 implementation plan。当前未检测到 plan，请先调用 /ssd-plan 完成阶段 2。
>
> 不允许凭 tasks.md 的标题直接实现——那是「做什么」，不是「怎么做」。

这是防止 plan 变成「写完不看的死文档」的硬约束。

## 流程

```text
前置检查：plan 存在
       ↓
[1] 读取 plan + tasks.md
       ↓
[2] 按 task 顺序实现：
      每个 task → 路由执行纪律
      完成 → 勾选 tasks.md
       ↓
[3] 全部 task 完成 + verification 通过
       ↓
[4] 引导进入 ssd-archive（阶段 4）
```

### 阶段 1：读取 plan + tasks

- 读取 `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md` 获取实现步骤
- 读取 `openspec/changes/<change-name>/tasks.md` 获取 task 清单与 checkbox 状态

### 阶段 2：按 task 顺序实现

对 plan 中的每个 task：

1. 按 plan 的实现步骤执行
2. 在执行过程中，根据当前情境路由执行纪律（见下表）
3. 完成并验证该 task 后，勾选 tasks.md 的对应 checkbox

### 执行纪律路由表

| 情境 | 执行纪律 | 说明 |
| --- | --- | --- |
| 开始 feature / bugfix task | `superpowers:test-driven-development` | 实现前先定义正确性 |
| 遇到失败 / 回归 / 异常结果 | `superpowers:systematic-debugging` | 改更多代码前先定位根因 |
| 准备宣称 task 完成 | `superpowers:verification-before-completion` | 宣称完成前先验证 |
| 阶段性检查点 | `superpowers:requesting-code-review` | 自然检查点加独立质量复核 |

路由优先级：

- 已出现失败或异常 → 优先 `systematic-debugging`
- 正在准备宣称完成 → 优先 `verification-before-completion`
- 其余按「开始实现」或「阶段性复核」在 TDD 与 code-review 间选择

### 阶段 3：全部完成 + 验证

所有 task 完成后：

- 确认 tasks.md 所有 checkbox 已勾选
- 通过 `superpowers:verification-before-completion` 做最终验证

### 阶段 4：引导进入 ssd-archive

输出明确的下一步指引：

> 阶段 3（执行）完成。所有 task 已实现并验证，tasks.md 全部勾选。
>
> 下一步：调用 /ssd-archive 归档本次 change。

## 与 OpenSpec /opsx:apply 的关系

- `/opsx:apply` 是 OpenSpec 原生 apply 阶段命令，负责 task flow（选 task、更新 tasks.md、何时 verify）
- `/ssd-apply` 是 SSD 体系在 apply 阶段的唯一入口，涵盖 task flow 推进（含勾选 tasks.md），并叠加两件增强：强制先读 plan + 执行纪律路由
- 在 SSD 体系下，apply 阶段统一走 /ssd-apply；遵循 OpenSpec task flow 语义，按 plan + tasks 自行推进，而非转发到 /opsx:apply 命令

## 边界

- 不重写 plan（归 ssd-plan）
- 不管理 change 归档（归 ssd-archive）
- 不把 tasks.md 当作完整实现计划（那是 plan 的职责）
````

- [ ] **Step 2: 验证契约**

确认 SKILL.md 满足：
- frontmatter 含 `name: ssd-apply`
- 前置检查要求 plan 存在，否则提示先 `/ssd-plan`（plan-aware）
- 含执行纪律路由表 4 行（TDD/debugging/verification/code-review）
- 明确 `/ssd-apply` 为 apply 阶段唯一入口

Run: `grep -c "superpowers:" "D:/Develop/Project/cj-cc-marketplace/ssd-workflow/skills/ssd-apply/SKILL.md"`
Expected: `>= 4`（四个执行纪律 skill）

- [ ] **Step 3: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ssd-workflow/skills/ssd-apply/SKILL.md
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 新增 ssd-apply skill（阶段 3 执行，plan-aware）"
```

---

### Task 5: ssd-archive skill（阶段 4 归档）

**Files:**

- Create: `ssd-workflow/skills/ssd-archive/SKILL.md`

**Interfaces:**

- Consumes: `openspec/changes/<change-name>/tasks.md`（全勾状态，来自 ssd-apply）、`/opsx:archive`
- Produces: 归档完成的 change；plan 产物保留留档

- [ ] **Step 1: 创建 ssd-archive/SKILL.md**

写入完整内容：

````markdown
---
name: ssd-archive
description: "SSD 工作流阶段 4（归档）：确认所有 task 完成并验证通过后，调用 /opsx:archive 归档 change，plan 产物保留留档。当 ssd-apply 阶段全部 task 完成时使用。"
---

# SSD 阶段 4：Archive（归档）

确认实现完成，调用 `/opsx:archive` 归档 change，plan 产物保留留档。

## 在 SSD 工作流中的位置

```text
[上一阶段] ssd-apply   → 阶段 3 执行
[本 skill] ssd-archive → 阶段 4 归档（闭环终点）
```

## 触发方式

/ssd-workflow:ssd-archive 或简写 /ssd-archive

也可由 ssd-apply 全部 task 完成后引导调用，或由 ssd 主入口根据产物判阶段后引导。

## 前置检查

开始前必须验证：

1. `openspec/changes/<change-name>/tasks.md` 所有 checkbox 已勾选
2. 已通过 `superpowers:verification-before-completion` 验证

若不满足，暂停并提示：

> 阶段 4 需要所有 task 完成并验证。当前仍有未完成 task，请先调用 /ssd-apply 完成阶段 3。

## 流程

```text
前置检查：tasks 全勾 + 验证通过
       ↓
[1] 调用 /opsx:archive 归档 change
       ↓
[2] plan 产物保留留档（不删除）
       ↓
[3] 闭环完成提示
```

### 阶段 1：调用 /opsx:archive

调用 `/opsx:archive`，由 OpenSpec 负责：

- delta spec 同步到 main spec
- change 移至 archive

### 阶段 2：plan 留档

plan 产物（`docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`）保留在原位，不随归档删除。

理由：plan 是实现决策的历史记录，保留便于后续回溯「为什么这样实现」。

### 阶段 3：闭环完成

输出：

> SSD 工作流闭环完成。
>
> - WHAT：OpenSpec proposal/spec/design/tasks
> - HOW：docs/superpowers/plans/YYYY-MM-DD-<change-name>.md
> - 执行：代码已实现并验证
> - 归档：change 已归档
>
> 本次 change 的 spec-driven 开发完成。

## 边界

- 不删除 plan 产物
- 不替代 OpenSpec 的归档机制，只做前置检查 + 调用 + 留档说明
````

- [ ] **Step 2: 验证契约**

确认 SKILL.md 满足：
- frontmatter 含 `name: ssd-archive`
- 前置检查要求 tasks 全勾 + verification 通过
- 明确 plan 留档不删

Run: `grep -c "opsx:archive" "D:/Develop/Project/cj-cc-marketplace/ssd-workflow/skills/ssd-archive/SKILL.md"`
Expected: `>= 2`

- [ ] **Step 3: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ssd-workflow/skills/ssd-archive/SKILL.md
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 新增 ssd-archive skill（阶段 4 归档）"
```

---

### Task 6: ssd 主入口 skill（流程导航）

**Files:**

- Create: `ssd-workflow/skills/ssd/SKILL.md`

**Interfaces:**

- Consumes: 产物存在性判断（proposal/plan/tasks 状态）
- Produces: 阶段判定 + 引导调用 `ssd-propose` / `ssd-plan` / `ssd-apply` / `ssd-archive` 之一
- 依赖：Task 2-5 的 skill 命名已定（ssd-propose/ssd-plan/ssd-apply/ssd-archive）

- [ ] **Step 1: 创建 ssd/SKILL.md**

写入完整内容：

````markdown
---
name: ssd
description: "SSD (Spec-Driven Development) 工作流主入口与流程导航。当用户开始一个需要 OpenSpec 提案的新功能/变更，或询问「现在该做什么 / 下一步走哪个阶段 / 继续之前的 change」时使用。根据产物存在性判断当前处于 propose/plan/apply/archive 哪个阶段，引导调用对应阶段 skill。"
---

# SSD 工作流主入口

Spec-Driven Development 工作流的流程导航。用产物存在性判断当前阶段，引导调用对应 skill。

## 三层职责

- **WHAT**（做什么）：OpenSpec — proposal/spec/design/tasks
- **HOW**（怎么做）：Superpowers — implementation plan + 执行纪律
- **WHEN**（何时做、什么顺序）：本工作流 — 阶段编排

## 四个阶段

```text
[1] WHAT                [2] HOW              [3] 执行           [4] 归档
ssd-propose             ssd-plan             ssd-apply          ssd-archive
brainstorming           writing-plans        按 plan 实现        /opsx:archive
→ /opsx:propose         → plan 文件          → 纪律路由
proposal/spec/          docs/superpowers/    → 勾选 tasks
design/tasks            plans/
```

## 根据产物判断当前阶段

观察当前 change 的产物，判断处于哪个阶段：

| 观察到的产物 | 当前阶段 | 引导调用 |
| --- | --- | --- |
| 无 proposal | 1 WHAT | `/ssd-propose` |
| 有 proposal、无 plan | 2 HOW | `/ssd-plan` |
| 有 plan、tasks 未全勾 | 3 执行 | `/ssd-apply` |
| tasks 全勾、未归档 | 4 归档 | `/ssd-archive` |

判断步骤：

1. 确定当前 change-name（询问用户，或从最近的 `openspec/changes/` 目录推断）
2. 检查 `openspec/changes/<change-name>/` 是否有 proposal/spec/design/tasks
3. 检查 `docs/superpowers/plans/` 是否有 `YYYY-MM-DD-<change-name>.md`
4. 检查 tasks.md 的 checkbox 是否全部勾选
5. 据上表引导调用对应阶段 skill

## 使用方式

### 开始一个新 change

用户提出新功能需求 → 当前无 proposal → 引导 `/ssd-propose`。

### 继续一个进行中的 change

用户询问「下一步」「继续」→ 按上表判断阶段 → 引导对应 skill。

中断后恢复也走这条路径——无需状态文件，靠产物判阶段。

## 边界

- 只做阶段判定与导航
- 不读写 OpenSpec artifact
- 不替代任何阶段 skill 的执行
- 不引入状态文件（靠产物存在性判断）
````

- [ ] **Step 2: 验证契约**

确认 SKILL.md 满足：
- frontmatter 含 `name: ssd` 和描述覆盖「现在该做什么/下一步/继续」
- 含产物判阶段表 4 行
- 含判断步骤 5 步
- 明确「不引入状态文件」

Run: `grep -c "ssd-propose\|ssd-plan\|ssd-apply\|ssd-archive" "D:/Develop/Project/cj-cc-marketplace/ssd-workflow/skills/ssd/SKILL.md"`
Expected: `>= 4`

- [ ] **Step 3: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ssd-workflow/skills/ssd/SKILL.md
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 新增 ssd 主入口 skill（流程导航）"
```

---

### Task 7: 注册 ssd-workflow 并下架 openspec-workflow

**Files:**

- Modify: `.claude-plugin/marketplace.json`（注册 ssd-workflow，移除 openspec-workflow）
- Modify: `CLAUDE.md`（仓库结构 openspec-workflow → ssd-workflow）
- Modify: `AGENTS.md`（仓库结构新增 ssd-workflow 条目）
- Delete: `openspec-workflow/` 整个目录

**Interfaces:**

- 前置：Task 2-6 已完成，ssd-workflow 5 个 skill 就位，ssd-propose/ssd-apply 已吸收 openspec-workflow 两个 skill 的内容

- [ ] **Step 1: 修改 marketplace.json**

读 `.claude-plugin/marketplace.json`，将 plugins 数组中的 openspec-workflow 条目替换为 ssd-workflow。最终 plugins 数组应为：

```json
"plugins": [
  {
    "name": "ep-comp",
    "source": "./ep-comp",
    "description": "基于 @gx-web/ep-comp 的业务代码生成插件"
  },
  {
    "name": "notify-hook",
    "source": "./notify-hook",
    "description": "Windows 任务栏闪烁通知 hook 插件"
  },
  {
    "name": "ssd-workflow",
    "source": "./ssd-workflow",
    "description": "Spec-Driven Development 工作流编排插件：OpenSpec(WHAT) × Superpowers(HOW) × ssd-workflow(WHEN)"
  },
  {
    "name": "cj-mcp",
    "source": "./mcp",
    "description": "共享 MCP 服务器配置（tavily / github / chrome-devtools / context7 / codegraph）"
  }
]
```

- [ ] **Step 2: 验证 marketplace.json**

Run: `node -e "const m=JSON.parse(require('fs').readFileSync('D:/Develop/Project/cj-cc-marketplace/.claude-plugin/marketplace.json','utf8')); const n=m.plugins.map(p=>p.name); console.log(n.join(',')); console.log('has ssd:', n.includes('ssd-workflow'), 'has old:', n.includes('openspec-workflow'))"`
Expected: `ep-comp,notify-hook,ssd-workflow,cj-mcp` / `has ssd: true has old: false`

- [ ] **Step 3: 修改 CLAUDE.md 仓库结构**

读 `CLAUDE.md`，定位仓库结构代码块中的 openspec-workflow 条目（形如 `openspec-workflow/ — OpenSpec × Superpowers 协作流程编排插件` 及其下 skills 子项），整段替换为：

```text
ssd-workflow/                 — Spec-Driven Development 工作流编排插件（OpenSpec × Superpowers）
  skills/
    ssd/                      — 主入口：流程导航（用产物判阶段）
    ssd-propose/              — 阶段 1 WHAT：brainstorming → /opsx:propose
    ssd-plan/                 — 阶段 2 HOW：→ superpowers:writing-plans
    ssd-apply/                — 阶段 3 执行：按 plan 实现 + 执行纪律路由
    ssd-archive/              — 阶段 4 归档：→ /opsx:archive
```

- [ ] **Step 4: 修改 AGENTS.md 仓库结构**

读 `AGENTS.md`，在仓库结构代码块中 ep-comp 子树结束（`examples/ — 可落地的代码示例` 行）之后、代码块结束之前，插入 ssd-workflow 条目：

```text
      examples/               — 可落地的代码示例
ssd-workflow/                 — Spec-Driven Development 工作流编排插件（OpenSpec × Superpowers）
  .claude-plugin/
    plugin.json               — 插件元数据
  skills/                     — 纯 SKILL.md 驱动，无 reference.md / 脚本 / 状态文件
    ssd/                      — 主入口：流程导航（用产物判阶段）
    ssd-propose/              — 阶段 1 WHAT：brainstorming → /opsx:propose
    ssd-plan/                 — 阶段 2 HOW：→ superpowers:writing-plans
    ssd-apply/                — 阶段 3 执行：按 plan 实现 + 执行纪律路由
    ssd-archive/              — 阶段 4 归档：→ /opsx:archive
```

- [ ] **Step 5: 删除 openspec-workflow 目录**

确认 ssd-propose（Task 2）与 ssd-apply（Task 4）已吸收旧 skill 内容后，删除旧目录：

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" rm -r openspec-workflow
```

- [ ] **Step 6: 最终验证**

Run: `ls "D:/Develop/Project/cj-cc-marketplace/ssd-workflow/skills"`
Expected: `archive  apply  plan  propose  ssd`（5 个目录）

Run: `ls "D:/Develop/Project/cj-cc-marketplace/openspec-workflow" 2>&1`
Expected: 报错「No such file or directory」（旧目录已删）

Run: `grep -l "openspec-workflow" "D:/Develop/Project/cj-cc-marketplace/CLAUDE.md" "D:/Develop/Project/cj-cc-marketplace/AGENTS.md" "D:/Develop/Project/cj-cc-marketplace/.claude-plugin/marketplace.json" 2>&1`
Expected: 无输出（三个文件均已无 openspec-workflow 引用）

- [ ] **Step 7: Commit**

```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add .claude-plugin/marketplace.json CLAUDE.md AGENTS.md openspec-workflow
git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "feat(ssd-workflow): 注册 ssd-workflow 并下架 openspec-workflow"
```

---

## Self-Review

**1. Spec coverage（对照设计文档各节）：**

- 定位 / 三层职责（what/when/how）→ Task 6 主入口「三层职责」节 ✓
- 目录结构（5 skill + plugin.json）→ Task 1 + Task 2-6 ✓
- 流程图（4 阶段 + 产物 + 衔接）→ 每个 skill 的「在 SSD 工作流中的位置」+ Task 6 四阶段图 ✓
- 各 skill 详细职责 → Task 2-6 逐一对应 ✓
- 阶段衔接契约（审核门即前置检查）→ ssd-plan/ssd-apply/ssd-archive 的「前置检查」节 ✓
- plan 落地契约（强制读 plan）→ ssd-apply「前置检查」节 ✓
- 轻量保证（零脚本零状态）→ Global Constraints + 每个 skill「边界」节 ✓
- 与 OpenSpec/Superpowers 关系 → ssd-apply「与 /opsx:apply 关系」节 + 主入口三层职责 ✓
- 迁移计划（取代 openspec-workflow）→ Task 7 ✓
- 决策记录（plan 命名 / 主入口 / apply 入口）→ Global Constraints + Task 3/4/6 ✓

无遗漏章节。

**2. Placeholder scan：**

- 无 TBD/TODO/"实现略"
- 每个 SKILL.md 均给出完整 frontmatter + 正文，可直接写入
- marketplace.json / CLAUDE.md / AGENTS.md 改动均给出精确目标内容
- 验证步骤均给出可运行命令与期望输出

无 placeholder。

**3. Type/naming consistency：**

- skill 命名全程一致：`ssd` / `ssd-propose` / `ssd-plan` / `ssd-apply` / `ssd-archive`
- plan 文件路径全程一致：`docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`
- 引导调用命令全程一致：`/ssd-propose` → `/ssd-plan` → `/ssd-apply` → `/ssd-archive`
- 执行纪律 skill 名全程一致：`test-driven-development` / `systematic-debugging` / `verification-before-completion` / `requesting-code-review`

无不一致。
