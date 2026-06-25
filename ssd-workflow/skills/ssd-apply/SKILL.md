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
