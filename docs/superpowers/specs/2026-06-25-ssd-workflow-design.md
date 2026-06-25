# ssd-workflow 插件设计

## 背景

当前 `openspec-workflow` 插件（v1.0.2）尝试把 OpenSpec 与 Superpowers 组合使用，包含两个 skill：

- `brainstorming-to-propose`：brainstorming 需求探索 → `/opsx:propose`
- `apply-with-superpowers`：实现期的执行纪律路由器（TDD / debugging / verify / code-review）

在实际项目使用中暴露出一个核心痛点：**OpenSpec 的 task 没有落实到实处**。

具体来说：

1. OpenSpec 的 `tasks.md` 本质是任务清单（带 checkbox 的「做什么」），它天生不是 implementation plan。
2. `apply-with-superpowers` 只负责「选哪种执行纪律」，不负责把 task 细化成具体的实现步骤（动哪些文件、什么接口、什么顺序）。
3. 于是中间空了一层：**「怎么做」没有人产出**。

这导致执行期只能凭抽象的 task 标题去猜实现方式，既不稳定也容易遗漏。

## 目标

新建一个独立插件 `ssd-workflow`（SSD = Spec-Driven Development），形成一条 **what / when / how 三层分明** 的稳定闭环：

```text
brainstorming → /opsx:propose（做什么）
                    ↓ 审核门
               writing-plans（怎么做）
                    ↓ 审核门
               按 plan 实现 + 执行纪律
                    ↓
               /opsx:archive（归档）
```

- **what**：由 OpenSpec 的 proposal / spec / design / tasks 覆盖。
- **when**：由 ssd-workflow 的阶段化编排覆盖，严格 propose → plan → apply → archive，不跳步。
- **how**：由 Superpowers 的 writing-plans 产出的 implementation plan 覆盖，且必须被执行。

设计参考 [comet](https://github.com/rpamis/comet) 的阶段化技能拆分思路，但**去除其全部脚本与状态机**，纯靠 SKILL.md 文档驱动 + 产物存在性判断阶段，做到「轻量但稳定」。

## 非目标

- 不引入任何守护脚本（comet 有 7 个 sh 脚本）。
- 不引入任何状态文件（comet 有双 YAML + 10 字段）。
- 不引入 PreToolUse hook 的强制写入保护。
- 不替代 OpenSpec 或 Superpowers，只做编排层。
- 不实现 comet 的快捷路径（`hotfix` / `tweak`），遵循 YAGNI，留作后续扩展点。
- 不处理项目未初始化 OpenSpec 的场景，ssd-workflow 假设项目已安装并初始化 OpenSpec。
- 不处理 Marketplace 版本发布与分发流程。
- 本文档不直接定义各 skill 的最终 SKILL.md 全文，只定义职责、边界与衔接契约。

## 设计原则

### 三层职责分明

| 层 | 含义 | 归属 | 产物 |
| --- | --- | --- | --- |
| what | 做什么 | OpenSpec | proposal / spec / design / tasks |
| when | 何时做、什么顺序 | ssd-workflow | 阶段编排 + 衔接指引 |
| how | 怎么做 | Superpowers | implementation plan + 执行纪律 |

ssd-workflow 只拥有 **when** 这一层，不越界写 what（不重写 proposal），也不越界定 how（不替代 writing-plans）。

### 轻量但稳定

「稳定」靠三件事，且都不依赖状态机：

1. **阶段化 skill**：每个阶段一个 skill，职责单一。
2. **首尾衔接**：每个阶段 skill 的末尾显式指向下一阶段，上一阶段的审核门是下一阶段的前置检查。
3. **产物判阶段**：主入口用产物存在性（有无 proposal / plan、tasks 是否全勾）判断当前阶段，中断后可直接恢复，无需状态文件。

## 整体架构

### 目录结构

```text
ssd-workflow/
  .claude-plugin/plugin.json
  skills/
    ssd/              — 主入口：流程导航（4 阶段总览 + 用产物判当前阶段）
    ssd-propose/      — 阶段 1 WHAT：brainstorming → /opsx:propose
    ssd-plan/         — 阶段 2 HOW ：propose 审核后 → superpowers:writing-plans
    ssd-apply/        — 阶段 3 执行：读 plan → 按 task 实现 → 纪律路由 → 引导 archive
    ssd-archive/      — 阶段 4 归档：确认完成 → /opsx:archive
```

所有 skill 纯 SKILL.md 驱动，不依赖外部库 API，因此不需要 `reference.md`。

### 流程

```text
[1] WHAT                    [2] HOW                 [3] 执行               [4] 归档
superpowers:brainstorming   superpowers:            按 plan 逐 task        /opsx:archive
        ↓                    writing-plans           实现 + 纪律路由             ↓
/opsx:propose               docs/superpowers/       tasks.md 勾选          openspec/changes/
        ↓                    plans/<change>.md             ↓                 → archive
proposal.md                       ↑                       ↓                spec 同步
spec.md                           ↑                       ↓
design.md                         ↑                       ↓
tasks.md  ──── 审核门 ────────────┘                  引导 → ssd-archive ────┘
                                                   (tasks 全勾 + verify)
```

### 阶段产物与判据

| 阶段 | skill | 归属 | 产物 | 进入下一阶段判据 |
| --- | --- | --- | --- | --- |
| 1 WHAT | `ssd-propose` | OpenSpec | proposal / spec / design / tasks | tasks.md 生成 + 用户审核通过 |
| 2 HOW | `ssd-plan` | Superpowers | `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md` | plan 存在 + 用户审核通过 |
| 3 执行 | `ssd-apply` | Superpowers + OpenSpec | 代码 + tasks 勾选 | tasks 全勾 + verification 通过 |
| 4 归档 | `ssd-archive` | OpenSpec | archive 目录 + spec 同步 | `/opsx:archive` 完成 |

## 各 skill 详细职责

### `ssd`（主入口 / 流程导航）

纯导航 skill，无状态文件。向用户展示 4 阶段总览，并用**产物存在性**判断当前阶段：

| 观察到的产物 | 当前阶段 | 引导调用 |
| --- | --- | --- |
| 无 proposal | 1 WHAT | `/ssd-propose` |
| 有 proposal、无 plan | 2 HOW | `/ssd-plan` |
| 有 plan、tasks 未全勾 | 3 执行 | `/ssd-apply` |
| tasks 全勾、未归档 | 4 归档 | `/ssd-archive` |

职责边界：

- 只做阶段判定与导航
- 不读写 OpenSpec artifact
- 不替代任何阶段 skill 的执行

### `ssd-propose`（阶段 1 WHAT）

吸收现有 `brainstorming-to-propose` 的全部能力，唯一关键差异是**末尾指向 `ssd-plan`**。

```text
superpowers:brainstorming（约束：不写独立 design doc）
  → 整理结构化摘要
  → /opsx:propose 生成 proposal / spec / design / tasks
  → 审核门：用户审核通过
  → 末尾明确指向 /ssd-plan
```

保留的约束：

- 禁止将结论写入 `docs/superpowers/specs/*`
- 禁止生成与 OpenSpec 平级的替代性正式文档
- 禁止直接调用 `writing-plans`（由 `ssd-plan` 接管）

### `ssd-plan`（阶段 2 HOW）

**填补「task 没落实到实处」的核心环节。**

```text
前置检查：proposal 已审核（否则退回 ssd-propose）
  → 读 proposal / spec / design / tasks 作为输入
  → 调 superpowers:writing-plans
  → 产出 docs/superpowers/plans/YYYY-MM-DD-<change-name>.md
  → 审核门：用户审核 plan
  → 末尾明确指向 /ssd-apply
```

粒度策略：

- 默认 **change 级**：一个 change 一份 plan，plan 内部按 task 组织实现步骤。
- change 过大时，由 `writing-plans` 自行判断拆分为多份 plan，文件名仍以 change-name 关联。

### `ssd-apply`（阶段 3 执行）

吸收现有 `apply-with-superpowers` 的执行纪律路由表，叠加 **plan-aware** 能力。

```text
前置检查：plan 存在（强制读 plan，否则提示先 /ssd-plan）   ← 防「死文档」的关键
  → 读 plan + tasks.md
  → 按 task 顺序实现：
      每个 task 内 → 路由执行纪律
      完成一个 task → 勾选 tasks.md
  → 全部完成 + verification 通过
  → 末尾明确指向 /ssd-archive
```

执行纪律路由表（来自 `apply-with-superpowers`）：

| 情境 | 执行纪律 |
| --- | --- |
| 开始 feature / bugfix | `superpowers:test-driven-development` |
| 遇到失败 / 回归 / 异常 | `superpowers:systematic-debugging` |
| 准备宣称完成 | `superpowers:verification-before-completion` |
| 阶段性检查点 | `superpowers:requesting-code-review` |

与 OpenSpec `/opsx:apply` 的关系：

- `/opsx:apply` 是 OpenSpec 原生的 apply 阶段命令，负责 task flow（选 task、更新 tasks.md、何时进入 verify）。
- `ssd-apply` 是 ssd-workflow 在 apply 阶段的执行入口，涵盖 task flow 推进（含勾选 tasks.md），并叠加两件增强：**强制先读 plan** + **执行纪律路由**。
- 在 ssd-workflow 体系下，apply 阶段统一走 `/ssd-apply`；它遵循 OpenSpec task flow 语义，按 plan + tasks 自行推进，而非转发到 `/opsx:apply` 命令。

### `ssd-archive`（阶段 4 归档）

```text
前置检查：tasks 全勾 + verification 通过
  → 调 /opsx:archive 归档
  → plan 产物保留在 docs/superpowers/plans/（留档不删）
```

plan 留档原则：plan 是实现决策的历史记录，归档时不删除，便于回溯。

## 阶段衔接契约（when 保证）

### 审核门即前置检查

每个阶段的「审核门」同时是下一阶段的「前置检查」。任何阶段 skill 在开始时必须先验证上一阶段产物，未通过则退回：

| 阶段 skill | 前置检查（不通过则退回） |
| --- | --- |
| `ssd-plan` | proposal 已生成且用户审核通过 → 否则退回 `ssd-propose` |
| `ssd-apply` | plan 文件存在 → 否则提示先 `ssd-plan` |
| `ssd-archive` | tasks 全勾 + verification 通过 → 否则退回 `ssd-apply` |

### 显式指向下一阶段

每个阶段 skill 完成后，必须输出一段明确的「下一步」提示，指向下一阶段 skill，而不是静默结束。这是 when 不跳步的硬约束。

### 中断可恢复

因不依赖状态文件，恢复方式是重新调用 `/ssd` 主入口，由产物判别当前阶段。任何阶段的审核门保证不会在产物不完整时贸然推进。

## plan 落地契约（how 保证）

### plan 必须被读

`ssd-apply` 的第一个动作是定位并读取 `docs/superpowers/plans/YYYY-MM-DD-<change-name>.md`。若 plan 不存在，必须暂停并提示用户先走 `ssd-plan`，不允许凭 task 标题直接实现。

### plan 与 tasks 双向关联

- plan 文件名格式为 `YYYY-MM-DD-<change-name>.md`，遵循 Superpowers 命名风格；change-name 部分与 `openspec/changes/<change-name>/` 一一对应。
- plan 内部按 tasks.md 的 task 组织实现步骤，task 编号与 tasks.md 对齐。
- `ssd-apply` 每完成一个 task，同步勾选 tasks.md 的对应 checkbox。

### plan 的粒度默认值

change 级（一个 change 一份 plan）。这是 `writing-plans` 的自然行为，不需要额外机制约束。

## 轻量保证（对比 comet）

| 维度 | comet | ssd-workflow |
| --- | --- | --- |
| 状态管理 | 双 YAML（`.openspec` + `.comet`）+ 10 字段 | 零状态文件，靠产物存在性 |
| 守护脚本 | 7 个 sh | 0 个 |
| 阶段衔接 | 脚本强制 + hook-guard 拦截写入 | skill 首尾衔接（文档驱动） |
| 阶段判别 | 读 `.comet.yaml` 的 phase | 看产物（proposal / plan / tasks） |
| 强制写入保护 | PreToolUse hook | 无（靠 skill 指引 + 审核门） |
| 设计交接 | SHA256 追踪的确定性上下文包 | plan 文件直接作为 apply 输入 |

**取舍说明**：comet 用重机制换取「防跳步 / 防漏 / 可恢复」的强保证；ssd-workflow 认为这些保证可以通过「阶段化 skill + 审核门前置检查 + 产物判阶段」以纯文档方式达到足够稳定的程度，而避免了脚本与状态机的运维负担。

## 与 OpenSpec / Superpowers 的关系

ssd-workflow 是**编排层**，不替代两者：

- **WHAT 归 OpenSpec**：`ssd-propose` 调 `/opsx:propose`，`ssd-archive` 调 `/opsx:archive`。
- **HOW 归 Superpowers**：`ssd-plan` 调 `superpowers:writing-plans`，`ssd-apply` 调执行纪律 skill。
- **WHEN 归 ssd-workflow**：4 阶段 skill + 主入口导航 + 衔接契约。

边界：

- ssd-workflow 不定义 proposal / spec 的写法（归 OpenSpec）。
- ssd-workflow 不定义 plan 的写法（归 writing-plans）。
- ssd-workflow 不定义 TDD / verify 的做法（归 Superpowers）。
- ssd-workflow 只定义「什么时候调谁、前后置条件是什么」。

## 迁移计划（取代 openspec-workflow）

`ssd-workflow` 完全取代 `openspec-workflow`：

1. 在仓库根新建 `ssd-workflow/` 目录与 `.claude-plugin/plugin.json`。
2. 新建 5 个 skill 目录（`ssd` / `ssd-propose` / `ssd-plan` / `ssd-apply` / `ssd-archive`）。
3. `ssd-propose` 吸收 `brainstorming-to-propose` 的 SKILL.md 内容，调整末尾指向。
4. `ssd-apply` 吸收 `apply-with-superpowers` 的路由表，叠加 plan-aware。
5. 在 `.claude-plugin/marketplace.json` 注册 `ssd-workflow`，移除 `openspec-workflow`。
6. 同步更新根 `CLAUDE.md` 与 `AGENTS.md` 的仓库结构说明。
7. 删除 `openspec-workflow/` 目录。
8. 版本从 `1.0.0` 起步。

## 决策记录（本轮定稿）

- plan 文件名格式：`YYYY-MM-DD-<change-name>.md`，遵循 Superpowers 的 `docs/superpowers/plans/` 目录命名风格，topic 部分用 change-name 保持与 OpenSpec change 的关联。
- 主入口 `/ssd`：保留，承担流程导航 + 产物判阶段 + 中断恢复。
- apply 阶段入口：`/ssd-apply` 为唯一入口，对用户屏蔽 `/opsx:apply`。

## 待确认项

### 可后补

- 是否需要 comet 式快捷路径（`hotfix` / `tweak`），用于跳过 brainstorming 的小改动场景。
- plan 留档是否需要额外的索引（如 `docs/superpowers/plans/README.md` 列出所有 plan 与 change 的对应关系）。
- `ssd` 主入口的阶段判别是否需要支持「一个项目多个并行 change」的场景。
