---
name: table-page
description: Generate ep-comp table pages with `generateTableColumns`, `generateFormItems`, `useTablePage`, and `GxPaginationTable`, without generating dialog capabilities by default.
---

# ep-comp 表格页生成

## Overview

这个 skill 只生成表格页底座：

- `model/index.ts`：`XxxQueryModel`、`XxxListItemModel`
- `api/index.ts`：`loadPage`
- `index.vue`：`GxSearch`、`GxPaginationTable`、`#header`、`#action`、`#action-bar`

这个 skill 不负责：

- 新增 / 编辑 / 审核弹窗
- 详情弹窗
- `loadDetail`
- `add` / `update` / `audit` / `removeById`

## When to Use

当用户要的是以下场景时，优先使用这个 skill：

- 根据 Swagger / Knife4j / OpenAPI 生成查询页、分页列表页
- 先生成 `ep-comp` 列表页骨架，后续再逐步追加弹窗能力
- 用户要的是 `generateTableColumns + generateFormItems + useTablePage + GxPaginationTable` 这一条主链路

## When NOT to Use

以下场景不应只使用这个 skill：

- 用户明确要求新增 / 编辑 / 审核弹窗
- 用户要详情弹窗
- 用户要一次性补全复杂表单交互

此时应：

1. 先用 `table-page` 生成底座
2. 再按需切换到 `form-dialog` 或 `detail-dialog`

## Output Scope

固定输出三部分：

1. `Model`
2. `API`
3. `主页面集成`

### Model

至少生成：

- `XxxQueryModel`
- `XxxListItemModel`

### API

至少生成：

- `loadPage`

### 主页面集成

至少生成：

- 搜索区：`#header`
- 行级操作槽：`#action`
- 页面级操作槽：`#action-bar`
- 根节点 `<div class="模块名-kebab-case">`

## Shared Contracts

### 根节点 contract

```vue
<template>
  <div class="module-kebab-case">
    <GxPaginationTable ...>
      <template #header>...</template>
      <template #action="{ row }">...</template>
      <template #action-bar>...</template>
    </GxPaginationTable>
  </div>
</template>
```

### 挂点 contract

- `#header`：查询区
- `#action`：行级操作
- `#action-bar`：页面级操作

### 交接 contract

后续 dialog 类 skill 只能在以下位置做增量注入：

- 追加 import
- 追加组件 ref
- 追加 handler
- 向 `#action` / `#action-bar` 注入按钮
- 在根 `div` 内、`GxPaginationTable` 之后追加组件实例

## Default Behavioral Constraints

- 默认只生成列表页底座
- 默认保留空的 `#action` / `#action-bar` 挂点
- 不擅自生成弹窗组件
- 不重写成整页自定义结构，除非用户明确要求

## Success Criteria

一次成功输出至少应满足：

- 正确生成 `XxxQueryModel` 和 `XxxListItemModel`
- API 只有 `loadPage`
- `index.vue` 使用 `GxSearch`、`GxPaginationTable`、`useTablePage`
- 模板只有一个根节点 `<div class="模块名-kebab-case">`
- 保留稳定挂点，便于 `form-dialog` / `detail-dialog` 继续注入

## API Reference

在生成代码前，先阅读 [API Reference](./reference.md)。
