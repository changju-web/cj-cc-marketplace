---
name: form-dialog
description: Add form-based dialogs to an existing ep-comp table page. Supports automatic mode with `generateFormItems + GxForm` and native mode with `ElForm`, but native mode requires explicit user confirmation.
---

# ep-comp 表单弹窗生成

## Overview

这个 skill 用于在已有 `table-page` 底座上，增量追加提交型弹窗能力。

负责内容：

- 追加 `FormModel` / `AuditModel`
- 追加 API：如 `add`、`update`、`audit`
- 生成 `components/*.vue`
- 向已有 `index.vue` 注入 import、ref、handler、按钮、组件实例

不负责内容：

- 重写整个 `table-page` 骨架
- 改写 `GxPaginationTable` 主结构
- 擅自重排 `columns` / `searchItems`

## Modes

### 自动模式

- 适用于标准 input/select/textarea 等字段
- 生成方式：`generateFormItems + GxForm`

### 原生模式

- 适用于审核、强联动、自定义布局、复杂业务组件
- 生成方式：`ElForm + ElFormItem + 业务组件`
- 触发条件：先解释复杂点，再经用户确认后生成

## Incremental Injection Rules

每次注入只允许做以下五类增量修改：

1. 追加 import
2. 追加组件 ref
3. 追加 handler
4. 向 `#action` / `#action-bar` 注入按钮
5. 在根 `div` 内追加组件实例

## Idempotency Checklist

每次注入前必须检查：

- import 是否已存在
- ref 是否已存在
- handler 是否已存在
- 按钮是否已存在
- 组件实例是否已存在

## Success Criteria

一次成功输出至少应满足：

- 自动模式与原生模式边界清晰
- 复杂场景切原生模式前明确需要用户确认
- 生成的按钮只注入到 `#action` 或 `#action-bar`
- 组件实例只挂载在根 `div` 内部
- 不覆盖已有列表页结构

## API Reference

在生成代码前，先阅读 [API Reference](./reference.md)。
