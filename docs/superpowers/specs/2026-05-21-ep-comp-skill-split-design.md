# ep-comp skill 拆分设计

## 背景

当前 `ep-comp:crud-page` 是一个大一统 skill，默认一次性生成列表页、查询表单、操作列以及新增/编辑弹窗。这个模式适合标准 CRUD，但与实际业务使用方式存在几个明显偏差：

1. 真实使用流程通常是先生成 `table-page`，再按需追加新增、编辑、审核、详情等弹窗能力。
2. 非标准弹窗（如审核、复杂联动表单、详情展示）并不总适合 `generateFormItems + GxForm` 的统一模板。
3. 一个 skill 同时承担页面骨架、表单生成、详情展示和增量改造，职责边界不清，后续扩展容易互相覆盖。

因此，需要将 `crud-page` 拆分为多个职责单一、可按需调用的 skill。

## 目标

将当前 `ep-comp:crud-page` 拆分为三个 skill：

- `table-page`
- `form-dialog`
- `detail-dialog`

并建立三者之间的协作契约，确保：

- 页面骨架与增量功能职责分离
- 多个 skill 可安全叠加调用
- 简单场景优先自动生成，复杂场景允许显式切换到原生模式
- 后续 skill 可以基于稳定挂点工作，而不是依赖脆弱的代码猜测

## 非目标

- 本文档不直接定义最终 skill 的实现代码
- 本文档不讨论 Marketplace 注册、版本发布与分发流程
- 本文档不处理与 `OpenSpec` 相关的生成逻辑拆分

## Skill 拆分方案

### 1. `table-page`

职责：生成纯表格页。

负责内容：

- `model/index.ts`
  - `XxxQueryModel`
  - `XxxListItemModel`
  - 列表展示用 options
- `api/index.ts`
  - `loadPage`
- `index.vue`
  - 搜索区
  - 表格区
  - 分页区
  - 根节点结构
  - `#header` / `#action` / `#action-bar` 稳定挂点
  - 列表级 handler（`loadList` / `reloadList` / `onChange`）

不负责内容：

- 新增/编辑/审核/详情弹窗
- 详情 API
- 审批 API
- 弹窗组件代码

### 2. `form-dialog`

职责：生成表单型弹窗，并增量挂接到已有 `table-page`。

负责内容：

- 追加 `FormModel` / `AuditModel` / 其他表单模型
- 追加 API：如 `add`、`update`、`audit`
- 生成 `components/xxx.vue`
- 向 `index.vue` 注入：
  - import
  - ref
  - handler
  - `#action` 或 `#action-bar` 按钮
  - 根节点内部的组件实例

不负责内容：

- 重写 `table-page` 骨架
- 改写 `GxPaginationTable` 结构
- 重排 table columns / searchItems（除非用户明确要求）

### 3. `detail-dialog`

职责：生成只读详情弹窗，并增量挂接到已有 `table-page`。

负责内容：

- 追加 `DetailModel`
- 追加 `loadDetail`
- 生成 `components/detail.vue`
- 向 `index.vue` 注入详情按钮、详情组件和详情 handler

不负责内容：

- 表单逻辑
- 查询条件调整
- 列表骨架改造

## 协作契约

### Ownership 归属边界

`table-page` 是页面骨架 owner；`form-dialog` 和 `detail-dialog` 是增量能力 owner。

即：

- `table-page` 决定页面主结构与稳定挂点
- dialog 类 skill 只能在稳定挂点之上增量注入
- dialog 类 skill 不能越权接管整个页面

### 稳定挂点 contract

`table-page` 生成的 `index.vue` 必须提供以下结构：

1. 唯一根节点：

```vue
<div class="模块名-kebab-case">
```

2. 表格主容器：

```vue
<GxPaginationTable ...>
```

3. 搜索挂点：

```vue
<template #header>...</template>
```

4. 行级操作挂点：

```vue
<template #action="{ row }">...</template>
```

5. 页面级操作挂点：

```vue
<template #action-bar>...</template>
```

### 按钮注入规则

- 行级按钮：只能注入 `#action`
- 页面级按钮：只能注入 `#action-bar`
- 不允许把弹窗触发入口插入 `#header`、`columns.render`、`#default` 等不稳定位置

### 弹窗挂载规则

- 弹窗组件实例必须挂载在根 `<div>` 内部
- 弹窗组件实例位置应位于 `GxPaginationTable` 之后
- 不允许产生多根节点

## 增量修改规则

为保证多个 skill 反复调用仍然稳定，dialog skill 只允许做以下五类增量修改：

1. 追加 import
2. 追加组件 ref
3. 追加 handler
4. 向 `#action` / `#action-bar` 注入按钮
5. 在根 div 内追加组件实例

禁止行为：

- 重写整个 `index.vue`
- 重排已有代码
- 覆盖已有 slot 内容
- 修改 table columns / searchItems（除非用户明确要求）

### 幂等性要求

每次注入前必须检查：

- import 是否已存在
- ref 是否已存在
- handler 是否已存在
- 按钮是否已存在
- 组件实例是否已存在

如果已存在，则跳过对应注入，避免重复代码。

### 冲突处理

如果发现以下情况：

- `#action` 已被用户高度自定义
- 页面结构不符合 `table-page` 契约
- 无法安全定位挂载区

skill 不应强改，而应暂停，并向用户说明：

- 缺失了哪个锚点
- 为什么当前无法安全注入
- 建议先修复结构或允许一次性结构整理

## 表单生成模式 contract

`form-dialog` 不再采用“混合模式”，只保留两档：

### 1. 自动模式

适用场景：

- 字段大多为标准输入型
- 结构可以自然映射到 `generateFormItems + GxForm`
- 交互联动较轻

生成方式：

- `generateFormItems + GxForm`

### 2. 原生模式

适用场景：

- 审核、强联动、自定义布局、复杂业务组件
- 自动模式会明显变形，或表达成本过高

生成方式：

- 原生 `ElForm + ElFormItem + 业务组件`

### 模式切换规则

- 默认优先尝试自动模式
- 一旦判断复杂度超出自动模式能力，不直接切换原生模式
- skill 必须先向用户解释：
  - 哪些字段或交互导致自动模式不适合
  - 原生模式的收益与代价
- 经用户确认后，再使用原生模式生成

## 统一行为 contract

### 弹窗组件暴露方法

统一约定：

- add：`init()`
- edit：`initEdit(row)`
- audit/custom：`init(row)`
- detail：`init(id)`

### 成功事件

所有提交型弹窗统一触发：

```ts
submitted
```

父页面默认处理：

```vue
@submitted="reloadList"
```

### 关闭行为

所有弹窗组件都应在 `@closed` 时重置自己的内部状态。

不把 reset 职责交给父页面。

### 按钮顺序

建议统一：

- 行级：`详情` → `编辑/审核/业务操作` → `删除`
- 页面级：`新增` 放在 `#action-bar`

## 降级策略

### `table-page` 的降级

当以下信息不明确时：

- request 封装
- 分页参数名
- `records/total` 路径
- 搜索字段类型
- 列展示格式

应降级为：

- 生成最小可用列表骨架
- 保留主链路
- 将不确定项写入“待确认项”

### `form-dialog` 的降级

当自动模式不适配时：

- 停止直接生成
- 先解释复杂点
- 用户确认后，再走原生模式

### `detail-dialog` 的降级

当详情字段过多、分组不明确、展示语义不清时：

- 先生成基础只读展示
- 不擅自做复杂分组
- 将分组、标签语义、展示顺序写入“待确认项”

## Skill 调用关系

推荐调用链：

1. 先调用 `table-page`
   - 生成稳定页面骨架和挂点
2. 再按需调用 `form-dialog` / `detail-dialog`
   - 做增量挂接
3. 两类 dialog skill 可以反复调用
   - 例如先详情，再审核，再新增编辑

换句话说：

- `table-page` 是底座
- `form-dialog` / `detail-dialog` 是可叠加能力

## 对现有 `crud-page` 的启示

现有 `crud-page` 中，以下内容应被拆出或弱化：

- “默认完整 CRUD 页面”不再作为唯一主路径
- “弹窗组件模板”不再默认绑定到 `crud-page`
- “自动一次性生成列表 + 弹窗”应改为可拆分流程

保留下来的可复用能力包括：

- Model / API / 搜索 / 表格的生成规则
- `ep-comp` 组件使用约定
- 响应类型约定
- “待确认项”与“不要强猜”规则

## 后续实现建议

建议在 `ep-comp/skills/` 下新增：

- `table-page/`
- `form-dialog/`
- `detail-dialog/`

并逐步将 `crud-page` 退化为：

- 兼容旧入口
- 或作为 orchestrator，根据用户输入决定调哪一个新 skill

## 待确认项

### 必确认

- `crud-page` 是保留为兼容入口，还是直接拆解后废弃
- 三个新 skill 的最终命名是否保持 `table-page / form-dialog / detail-dialog`
- `table-page` 是否必须始终生成空的 `#action` / `#action-bar` 挂点

### 可后补

- `detail-dialog` 是否需要支持分组展示模板
- `form-dialog` 是否允许对 `generateFormItems` 做更细粒度的 fallback 提示
- 多个 dialog skill 并存时，按钮排序是否需要写成硬规则
