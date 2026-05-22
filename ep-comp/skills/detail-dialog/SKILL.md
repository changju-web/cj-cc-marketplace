---
name: detail-dialog
description: Add read-only detail dialogs to an existing ep-comp table page without changing the table-page skeleton.
---

# ep-comp 详情弹窗生成

## Overview

这个 skill 只负责：

- `DetailModel`
- `loadDetail`
- `components/detail.vue`
- 向现有 `index.vue` 注入详情按钮、详情 handler、详情组件实例

这个 skill 不负责：

- 表单提交
- 查询条件改造
- 改写 `GxPaginationTable` 主结构

## Modes

### 自动模式

- 适用于标准只读字段展示
- 生成方式：`generateDescriptionsItems + GxDescriptions`

### 原生模式

- 适用于自定义渲染、条件显隐、复杂布局
- 生成方式：`ElDescriptions + ElDescriptionsItem`
- 触发条件：先解释复杂点，再经用户确认后生成

## When to Use

当用户要的是以下场景时，优先使用这个 skill：

- 详情按钮
- 只读弹窗
- 在现有 `table-page` 上追加详情能力

## Incremental Injection Rules

详情能力只允许做以下增量修改：

1. 追加 import
2. 追加详情组件 ref
3. 追加 `handleDetail`
4. 向 `#action` 注入详情按钮
5. 在根 `div` 内追加详情组件实例

## Expose Contract

- detail：`init(id)`

## Success Criteria

一次成功输出至少应满足：

- 生成 `DetailModel`
- 生成 `loadDetail`
- 详情组件暴露 `init(id)`
- 自动模式与原生模式边界清晰
- 复杂场景切原生模式前明确需要用户确认
- 详情按钮只注入到 `#action`
- 不混入提交型表单逻辑

## API Reference

在生成代码前，先阅读 [API Reference](./reference.md)。
