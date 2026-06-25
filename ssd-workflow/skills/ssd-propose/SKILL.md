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
