---
name: brainstorming-spec
description: "编排 brainstorming 到 OpenSpec 提案的自动流转。当项目存在 OpenSpec 时，将 brainstorming 的结论直接转化为 /opsx:propose 的输入，不写独立的 design doc。触发场景：用户提出新功能开发需求、新页面需求、新模块需求，或任何需要从想法到正式提案的场景。关键词：'新功能'、'新页面'、'新模块'、'需求开发'、'做个 xxx'。即使没有明确提到，只要是功能开发的初期阶段，都应主动使用。"
---

# Brainstorming → Spec

将 brainstorming 的需求探索结论自动流转为 OpenSpec 正式提案，避免结论散落在对话中。

## 为什么

当项目存在 OpenSpec 时，`superpowers:brainstorming` 的默认流程会写 design doc 到 `docs/superpowers/specs/`，这与 OpenSpec 的 `proposal/spec/design/tasks` 体系产生冲突——两套平行的正式文档会造成混乱。

本 Skill 通过约束 brainstorming 的输出边界，使其结论无缝流入 `/opsx:propose`，形成一条从"想法"到"正式 artifact"的单向管道。

## 流程

```text
用户提出功能需求
       ↓
[1] brainstorming 需求探索
       ↓ 自动流转
[2] /opsx:propose 创建提案
       ↓ 人工审核门
[3] 用户审核并确认
```

### 阶段 1：brainstorming

调用 `superpowers:brainstorming` skill，但遵循以下约束：

**允许做的事：**
- 澄清需求、目标和约束
- 收敛方案边界、比较可选方案并给出推荐
- 探索技术方案和数据模型
- 产出供 `/opsx:propose` 使用的结构化输入

**禁止做的事：**
- 将结论写入 `docs/superpowers/specs/*`
- 生成与 OpenSpec `proposal/spec/design` 平级的替代性正式文档
- 调用 `writing-plans` skill（后续由 OpenSpec 接管）

**完成标志：** 用户确认了方案方向后，整理结论并直接进入阶段 2。

### 阶段 1 结束时的产出

brainstorming 完成后，必须整理出以下信息供 `/opsx:propose` 使用：

| 产出项 | 内容 | 对应 OpenSpec artifact |
|--------|------|----------------------|
| 功能目标 | 一句话描述要做什么、为什么做 | proposal.md 的 Why |
| 范围与约束 | 做什么、不做什么 | proposal.md 的 Scope |
| 推荐方案 | 技术选型和理由 | design.md 的依据 |
| 实体与字段 | 核心数据模型 | design.md 的数据设计 |
| API 接口 | 路径、方法、参数、响应（如有） | design.md 的接口设计 |
| 任务拆分建议 | 按阶段/模块拆分的实现步骤 | tasks.md 的依据 |

如果用户提供了 Swagger/Knife4j URL 或 OpenAPI JSON，一并记录。

### 阶段 2：/opsx:propose（自动流转）

阶段 1 完成后不暂停，直接调用 `/opsx:propose` 创建 change。

基于阶段 1 的产出，在 `openspec/changes/<change-name>/` 下生成：
- `proposal.md` — 需求描述（Why/What/Impact）
- `design.md` — 技术设计决策
- `tasks.md` — 任务清单（带 checkbox）

### 阶段 3：人工审核门

**必须暂停，等待用户明确确认：**

> OpenSpec 提案已创建在 `openspec/changes/<change-name>/`，请审核：
>
> 1. **proposal.md** — 需求描述是否准确
> 2. **design.md** — 技术方案是否合理
> 3. **tasks.md** — 任务拆分是否完整
>
> 确认后可以使用 `/opsx:apply` 开始实现，或选择其他方式。

**只有用户明确同意后才算完成。** 用户修改意见则更新后重新提交审核。

## 项目没有 OpenSpec 时的降级

如果项目未初始化 OpenSpec，流程回归 brainstorming skill 的默认行为。

## 与其他 Skill 的关系

本 Skill 不替代 brainstorming 或 OpenSpec，而是作为桥接层：

| Skill | 关系 |
|-------|------|
| `superpowers:brainstorming` | 被调用，阶段 1 使用，但约束输出边界 |
| `/opsx:propose` | 被调用，阶段 2 使用，创建正式 artifact |

审核通过后的实现阶段不在本 Skill 范围内——用户可选择：
- `/opsx:apply` 推进任务（配合 superpowers 执行闭环）
- `ep-comp:crud-page` 生成 CRUD 代码（如适用）
- 其他实现方式
