---
name: apply-with-superpowers
description: Use when implementing OpenSpec tasks from tasks.md and the main question is which Superpowers execution discipline should guide the current task
---

# Apply with Superpowers

## Overview

这是一个面向 OpenSpec implementation 阶段的执行路由 skill。

当 `tasks.md` 已经定义了当前 task，而真正的问题变成“现在该用哪种 Superpowers 执行纪律”时，使用这个 skill。

它适合接在 `brainstorming-to-propose` 或其他 OpenSpec 设计阶段之后，在 implementation 语境下帮助当前 task 选择合适的执行纪律。

OpenSpec 管 task flow，Superpowers 管 task execution。

## When to Use

- 正在根据 `tasks.md` 实现 task
- `/opsx:apply` 已进入执行语境
- 当前 task 已明确，但执行方式还不明确
- 不确定该先进入 TDD、debugging、verification 还是 code review

## When Not to Use

- 仍在编写或修改 `proposal` / `spec` / `design`
- 仍在决定先做哪个 change 或哪个 task
- 需要工作流引擎自动管理 task、重试或并行
- 想替代 `/opsx:apply` 或 OpenSpec 状态管理

## Core Routing Rules

| Situation | Skill | Why |
| --- | --- | --- |
| Starting a feature or bugfix task | `superpowers:test-driven-development` | Define correctness before implementation |
| Hitting a failure, regression, or unexpected result | `superpowers:systematic-debugging` | Find the root cause before changing more code |
| About to claim the task is done | `superpowers:verification-before-completion` | Verify before declaring completion |
| Finishing a meaningful implementation chunk | `superpowers:requesting-code-review` | Add an independent quality check at a natural checkpoint |

如果当前已经出现失败、回归或异常结果，优先进入 `systematic-debugging`。如果当前正在准备宣称完成，优先进入 `verification-before-completion`。

## How to Apply

先用 `Core Routing Rules` 判断当前最主要的执行问题，再切到对应的 Superpowers skill。

如果已经出现失败或异常，优先进入 `superpowers:systematic-debugging`。如果当前正在准备宣称完成，优先进入 `superpowers:verification-before-completion`。其余情况下，再根据当前是“开始实现”还是“阶段性复核”在 `superpowers:test-driven-development` 与 `superpowers:requesting-code-review` 之间选择。

完成该执行步骤后，再回到 OpenSpec task flow。

## Boundary With OpenSpec

OpenSpec 决定当前推进哪个 task，以及何时更新 `tasks.md`、何时进入 `/opsx:verify`。

本 skill 只决定当前 task 应采用哪种 Superpowers execution discipline。

它不管理 change 状态，不读写 `tasks.md`，不重写 specs，也不是任务编排器。

## Common Mistakes

- 把 `tasks.md` 当作完整实现计划
- 把本 skill 写成自动执行器
- 把 debugging 变成自动重试机制
- 把 verification / code review 当成固定流水线节点
- 让 execution routing 反过来覆盖 OpenSpec 的 task flow
