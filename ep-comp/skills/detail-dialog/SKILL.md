---
name: detail-dialog
description: "Generate or incrementally add @gx-web/ep-comp read-only detail dialogs to a table/list page. Use for requests like 详情弹窗、查看详情、详情按钮、只读详情、loadDetail、DetailModel、GxDescriptions, or adding a detail action to an existing table-page. Creates DetailModel, loadDetail, components/detail.vue, detail button, ref, handler, and component instance without changing the GxPaginationTable skeleton."
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

### 自动模式（默认）

- 生成方式：`generateDescriptionsItems + GxDescriptions`
- 适用于绝大多数场景，包含以下扩展手段：
  - 枚举映射：`render: (d) => h('span', labelMap[d.status])`
  - 多字段合并：`render: (d) => h('span', \`${d.start} ~ ${d.end}\`)` + `span: N`
  - 条件显隐：`hide: (d) => boolean`
  - 自定义 span：`{ prop: 'xxx', span: 2 }`
- **不能因为有一两个字段复杂就切换原生模式**
- 前置要求：`DetailModel` 的展示字段必须有 `@FieldName` 装饰器，或在配置中手动提供 `label`

### 原生模式（降级）

- 生成方式：`ElDescriptions + ElDescriptionsItem`
- 仅当自动模式所有扩展手段都无法覆盖时使用
- 触发流程：**先列出哪些扩展手段已尝试、为何不适用，再经用户确认后生成**

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
