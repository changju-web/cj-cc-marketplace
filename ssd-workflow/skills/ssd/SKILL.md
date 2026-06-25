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
