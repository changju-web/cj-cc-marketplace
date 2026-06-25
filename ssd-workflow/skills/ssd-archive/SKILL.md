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
