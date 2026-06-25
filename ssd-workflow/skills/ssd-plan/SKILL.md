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

开始前必须验证（以下两项均须满足）：

1. 当前 change 的 proposal/spec/design/tasks 已生成（`openspec/changes/<change-name>/` 存在且四件套齐全）
2. 用户已审核通过该提案

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
