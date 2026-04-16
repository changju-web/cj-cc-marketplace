---
name: apply-with-superpowers
description: "面向 OpenSpec tasks 的 executing-plans 变体。在 task 执行过程中嵌入 Superpowers 执行型 skill（TDD、debugging、verification、code-review），确保每个 task 按工程闭环高质量完成。触发场景：用户准备实现 OpenSpec change 的 tasks.md，需要带 Superpowers 工程纪律执行。关键词：'apply'、'实现 task'、'执行 task'、'带 superpowers 执行'。当用户在 OpenSpec change 中准备进入实现阶段时，都应主动使用。"
---

# Apply with Superpowers

面向 OpenSpec tasks 的 executing-plans 变体，在 task 执行过程中嵌入 Superpowers 执行型 skill，确保每个 task 按工程闭环高质量完成。

## 为什么

`/opsx:apply` 本身只负责读取 tasks.md、逐项实现、更新状态——它是 change 级别的执行调度器，但不规定每个 task 应该如何被高质量地完成。

Superpowers 提供了执行型 skill（TDD、debugging、verification、code-review），但它们不会自动被 `/opsx:apply` 调用。

本 Skill 通过编排层将两者桥接，让 `/opsx:apply` 的执行过程自动嵌入 Superpowers 内层闭环，避免 task 变成机械勾选。

## 在 Superpowers Workflow 中的位置

```text
步骤 1-3：brainstorming-to-propose 已覆盖
          brainstorming → writing-plans → 产出 tasks.md
                                       ↓
步骤 4：  apply-with-superpowers 衔接（本 skill）
          → 等价于 executing-plans，但以 OpenSpec tasks.md 为输入
          → 内嵌 TDD / debugging / verification / code-review
          → 支持并行执行独立 task
```

**关键映射**：OpenSpec 的 `tasks.md` ≈ Superpowers 的 plan（来自 `writing-plans`）。

## 触发方式

本 skill 支持两种触发：

### 1. 显式调用（最稳定）

用户直接输入：

```text
/openspec-workflow:apply-with-superpowers
```

或简写为：

```text
/apply-with-superpowers
```

### 2. 自动触发（语义匹配）

当满足以下条件时，Claude 应主动调用本 skill：

- 项目存在 OpenSpec
- 当前 change 存在未完成 task
- 用户表达了"开始实现 task"、"执行 task"的意图
- 用户调用了 `/opsx:apply` 但希望更严格的执行纪律

当不确定是否应触发时，优先使用显式调用。

## 适用前提

- 项目已初始化 OpenSpec
- 当前 change 存在 `tasks.md` 且至少有一个未完成 task
- 项目已安装 Superpowers 插件

如果前提不满足，输出对应提示并终止：

| 情况 | 提示 |
|------|------|
| 项目未初始化 OpenSpec | "项目未检测到 OpenSpec。请先初始化 OpenSpec。" |
| 当前无 change | "当前没有活跃的 change。请先通过 /opsx:propose 创建 change。" |
| tasks.md 无未完成 task | "所有 task 已完成，可进入 /opsx:verify。" |

## 与其他 Skill 的关系

本 Skill 不替代任何 Superpowers skill 或 OpenSpec 命令，而是作为编排层：

### 编排层（本 skill 自身）

- 读取 tasks.md，分析 task 依赖关系
- 独立 task 通过 `dispatching-parallel-agents` 并行执行
- 有依赖的 task 按序执行

### 执行策略（按需选择）

- `executing-plans` — 顺序执行，适合有依赖的 task
- `subagent-driven-development` — 独立子代理执行，适合复杂 task
- `dispatching-parallel-agents` — 并行执行独立 task

### 执行型 skill（内层闭环）

- `superpowers:test-driven-development` — 按需
- `superpowers:systematic-debugging` — 失败时自动
- `superpowers:verification-before-completion` — 必选
- `superpowers:requesting-code-review` — 按需

### 与 brainstorming-to-propose 的关系

`brainstorming-to-propose` 覆盖 Superpowers workflow 的步骤 1-3（从想法到 tasks.md），本 skill 覆盖步骤 4（从 tasks.md 到实现完成）。两者形成完整的前后端衔接：

```text
brainstorming-to-propose → /opsx:propose → tasks.md → apply-with-superpowers → /opsx:verify
```

## 流程

```text
用户调用 /apply-with-superpowers
       ↓
[1] 读取与规划 → 分析 task 复杂度与依赖，映射 skill 组合
       ↓
[2] 用户确认   → 汇总执行计划，一次审阅确认
       ↓
[3] 逐 task 执行 → 内层 Superpowers 闭环
       ↓
[4] 状态更新与报告 → 更新 tasks.md，输出执行报告
```

### 阶段 1：读取与规划

**输入**：当前 change 的 `tasks.md`

**处理**：

1. 读取 tasks.md，筛选未完成 task
2. 分析每个 task 的复杂度（基于描述内容）
3. 分析 task 之间的依赖关系
4. 为每个 task 映射推荐 skill 组合
5. 确定执行策略（并行 / 顺序）

**复杂度分类与 skill 映射**：

| 复杂度 | 判断依据 | 推荐 skill 组合 |
|--------|----------|----------------|
| 简单 | 单文件改动、配置变更、纯文本修改 | verification-only |
| 中等 | 多文件改动、新增组件/接口 | verification + TDD |
| 复杂 | 跨模块改动、架构变更、核心逻辑修改 | verification + TDD + code-review |

**并行策略**：

- 无依赖的 task 标记为"可并行"，使用 `dispatching-parallel-agents`
- 有依赖的 task 按序执行

**执行策略选择**：

| 场景 | 推荐策略 | 理由 |
|------|----------|------|
| 有 2+ 独立 task | `dispatching-parallel-agents` | 并行提速 |
| 单个复杂 task | `subagent-driven-development` | 隔离上下文，避免污染主对话 |
| 简单顺序 task | `executing-plans` | 轻量顺序执行 |

阶段 1 根据上述规则自动推荐，阶段 2 用户可调整。

### 阶段 2：用户确认

**输入**：阶段 1 的执行计划摘要

**处理**：

1. 汇总成一张表，展示：
   - 每个 task 的编号与标题
   - 复杂度判断
   - 推荐的 skill 组合
   - 执行顺序（并行/顺序分组）
2. 用户一次审阅，可：
   - 整体确认
   - 调整某个 task 的 skill 组合
   - 调整执行顺序

**输出**：用户确认后的最终执行计划

无论 task 数量多少，用户只需一次确认。

确认后输出提示：

> 执行计划已确认。即将开始逐 task 执行，每个 task 将按确认的 skill 组合运行 Superpowers 内层闭环。

只有用户明确确认后才进入阶段 3。

### 阶段 3：逐 task 执行

对每个 task（按确认的计划）执行以下内层闭环：

```text
  1. 确认 task 边界与验收标准
  2. 如启用 TDD → 调用 superpowers:test-driven-development
  3. 实现当前最小改动
  4. 如失败 → 调用 superpowers:systematic-debugging，自动重试（最多 3 次）
  5. 调用 superpowers:verification-before-completion（必选）
  6. 如启用 code-review → 调用 superpowers:requesting-code-review
  7. 验证通过 → 更新 tasks.md 中该 task 状态为完成
  8. 重试 3 次仍失败 → 标记为 failed，跳过，继续下一个
```

**并行 task**：每个独立 task 在各自子代理中运行上述闭环，互不阻塞。

**顺序 task**：按依赖顺序逐个执行，前一个完成后才开始下一个。

每个 task 完成后，输出简短状态：

> Task N: <标题> — ✅ 完成 / ❌ 失败（<原因>）

### 阶段 4：状态更新与报告

**输入**：所有 task 的执行结果

**处理**：

1. 更新 tasks.md（完成/失败状态）
2. 输出执行报告：

```text
## 执行报告

**Change**: <change-name>
**总 task 数**: N
**完成**: X
**失败**: Y
**完成率**: X/N (P%)

### 完成的 task
- [x] Task 1: <标题>
- [x] Task 2: <标题>

### 失败/跳过的 task
- [ ] Task 3: <标题> — 失败原因: <原因>
```

3. 如有失败 task → 提示用户后续处理建议
4. 如全部完成 → 提示可进入 `/opsx:verify`

## 失败处理

### 重试策略

```text
第 1 次失败 → 调用 superpowers:systematic-debugging → 自动修复 → 重新 verification
第 2 次失败 → 再次 debugging + 修复 → 重新 verification
第 3 次仍失败 → 标记 task 为 failed，记录失败原因，跳过
```

默认重试次数为 3 次。

### 并行执行中的失败

- 不阻塞其他并行 task 的执行
- 失败的 task 单独标记为 failed
- 依赖该 task 的后续 task 自动标记为 blocked
- 在阶段 4 报告中提示依赖链影响

## 边界情况

| 情况 | 处理方式 |
|------|----------|
| tasks.md 无未完成 task | 提示"所有 task 已完成，可进入 /opsx:verify" |
| 项目未初始化 OpenSpec | 提示用户先初始化 OpenSpec |
| 当前无 change | 提示用户先创建 change |
| task 描述不明确 | 在阶段 2 确认时标注"需澄清"，请用户补充 |
| 所有 task 都失败 | 阶段 4 报告后建议回退到 brainstorming 重新评估 |
| verification 发现回归 | 自动进入 debugging 闭环 |

## 不做的事

- 不自动创建 git commit（由 `/opsx:verify` 或用户决定）
- 不自动调用 `finishing-a-development-branch`（留给用户手动触发）
- 不修改 proposal/spec/design（只读写 tasks.md）
- 不处理 worktree 创建（用户在调用前自行决定是否隔离）

## 与 brainstorming-to-propose 的完整衔接

```text
brainstorming-to-propose（前置 bridge）
  → brainstorming → /opsx:propose → proposal/spec/design/tasks

apply-with-superpowers（执行 bridge）
  → tasks.md → Superpowers 内层闭环 → 更新 tasks.md

后续：
  → /opsx:verify → /opsx:archive
```

两个 bridge skill 分别覆盖 Superpowers workflow 的前半段（设计）和后半段（执行），形成完整闭环。
