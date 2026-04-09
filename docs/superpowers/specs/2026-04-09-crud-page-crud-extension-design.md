# crud-page skill 扩展为完整 CRUD 设计

## 背景

当前 `ep-comp:crud-page` skill 只生成**分页查询页面**（Model + API 查询/删除 + 搜索表单 + 表格）。缺少新增/编辑弹窗组件和完整 CRUD API 生成能力。

参考模块 `xbwisdom-web/src/views/system/product-manage` 提供了完整的 CRUD 写法模式，本设计基于该模式扩展 skill。

## 设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 覆盖范围 | 完整 CRUD | 用户期望一次生成完整页面，减少手动补全 |
| 对话框组件 | `ElDialog` | 通用性强，不依赖 `@base-lib` |
| 弹窗表单 | 混合模式 | 简单字段用 `generateFormItems`，复杂字段手动 `ElFormItem` |
| 扩展方式 | 在现有 SKILL.md 中扩展 | 保持单一 skill，避免拆分后的依赖协调 |

## 输出结构变更

### 现有：固定五段式

1. Model
2. API
3. 查询表单
4. 表格分页
5. 待确认项

### 变更后：固定八段式

1. **Model** — 查询模型 + 列表项模型 + 表单模型（新增 `XxxFormModel`）
2. **API** — 完整 CRUD 四接口（扩展 `add` / `update`）
3. **查询表单** — 不变
4. **表格分页 + 操作列** — 扩展操作列（编辑/删除按钮）
5. **弹窗组件** — 新增 `components/xxx-add.vue`
6. **主页面集成** — 完整 `index.vue` 集成弹窗
7. **类型导出** — 各目录 `index.ts` 统一导出
8. **待确认项** — 不变

## 各段落详细设计

### 1. Model 变更

**新增 `XxxFormModel`**：弹窗表单专用模型，与列表展示模型分开。

**字段块注释**：所有字段必须添加 `/** ... */` 块注释，确保 IDE 悬停可见。

```ts
import { FieldName } from '@gx-web/core'

/** 查询参数模型 */
export class XxxQueryModel {
  /** 名称 */
  @FieldName('名称')
  name!: string
}

/** 列表项模型 */
export class XxxListItemModel {
  /** 序号 */
  @FieldName('序号')
  index!: number

  /** 名称 */
  @FieldName('名称')
  name!: string

  /** 备注 */
  @FieldName('备注')
  remark!: string

  /** 创建时间 */
  @FieldName('创建时间')
  createdTime!: string

  id!: string
}

/** 新增/编辑表单模型 */
export class XxxFormModel {
  /** 名称 */
  @FieldName('名称')
  name!: string

  /** 备注 */
  @FieldName('备注')
  remark!: string

  id!: string
}
```

**关键规则**：

- `XxxFormModel` 仅包含可编辑字段，不包含纯展示字段（如 `createdTime`）
- `id` 字段包含在 FormModel 中，用于区分新增/编辑模式
- 块注释内容与 `@FieldName` 保持一致

### 2. API 变更

扩展为完整 CRUD 四接口：

```ts
import useAxios from '@base-lib/hooks/core/useAxios'
import type { XxxListItemModel, XxxQueryModel, XxxFormModel } from '../model'

const request = useAxios()

/** 分页查询 */
export const loadPage = (params: XxxQueryModel) => {
  return request.get<ResPage<XxxListItemModel>>({
    url: '/xxx/page',
    params
  })
}

/** 新增 */
export const add = (data: XxxFormModel) => {
  return request.post({
    url: '/xxx',
    data
  })
}

/** 更新 */
export const update = (data: XxxFormModel) => {
  return request.put({
    url: '/xxx',
    data
  })
}

/** 删除 */
export const removeById = (id: string) => {
  return request.delete({
    url: `/xxx/${id}`
  })
}
```

**规则**：

- `add` 和 `update` 使用 `XxxFormModel` 作为参数类型
- `removeById` 接受 `id: string`
- 所有 API 函数添加块注释说明用途

### 3. 查询表单

不变，继续使用 `generateFormItems` + `GXSearch`。

### 4. 表格分页 + 操作列

**`generateTableColumns` 只配置数据列**，操作列通过 `#action` slot 渲染（不使用 render/JSX）。

```ts
const columns = generateTableColumns(XxxListItemModel, [
  'name',
  'remark',
  'createdTime'
])
```

```vue
<template #action="{ row }">
  <ElButton link type="primary" @click="handleEdit(row)">编辑</ElButton>
  <ElPopconfirm title="是否删除?" placement="left" @confirm="handleDel(row)">
    <template #reference>
      <ElButton link type="danger">删除</ElButton>
    </template>
  </ElPopconfirm>
</template>
```

**规则**：

- 操作列统一通过 `GXPaginationTable` 的 `#action` slot 渲染
- 不在 `generateTableColumns` 中使用 render 配置操作列
- 删除操作使用 `ElPopconfirm` 二次确认，`placement="left"`

### 5. 弹窗组件

独立文件 `components/xxx-add.vue`，使用 `ElDialog`。

**核心模式**：

- `defineOptions({ name: 'XxxAdd' })` 设置组件名称
- `useToggle` 管理显隐，额外维护 `loading` 状态
- `useStateRef` 管理表单数据（支持 reset）
- `computed` 判断 `isEdit`（基于 `form.value.id` 是否存在）
- `defineExpose({ init, initEdit })` 暴露方法给父组件
- 提交成功后 `emit('submitted')` 通知父组件刷新
- `@closed` 事件中重置表单
- CRUD 操作使用 try/catch/finally 错误处理，finally 中关闭 loading

**表单生成策略（混合模式）**：

1. 简单字段（input、select、textarea）：使用 `generateFormItems` 生成
2. 复杂字段（树选择器、上传、自定义组件）：手动 `ElFormItem`
3. 在输出中明确标注哪些是自动生成、哪些需要手动补充

**弹窗组件模板**：

```vue
<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useCompRef, useStateRef } from '@gx-web/tool'
import { useCompRef, useStateRef, useToggle } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { generateFormItems, GXForm } from '@gx-web/ep-comp'
import { add, update } from '../api'
import type { XxxListItemModel } from '../model'
import { XxxFormModel } from '../model'

defineOptions({
  name: 'XxxAdd'
})

const emit = defineEmits<{
  submitted: []
}>()

const [visible, setVisible] = useToggle(false)

const [loading, setLoading] = useToggle(false)

const [form, , resetForm] = useStateRef(() => getModelFromJson(XxxFormModel))

const isEdit = computed(() => !!form.value.id)

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
})

const dialogTitle = computed(() => `${isEdit.value ? '编辑' : '新增'}xxx`)

// 简单字段自动生成
const formItems = generateFormItems(XxxFormModel, [
  'name',
  'remark'
])

const FormRef = useCompRef<typeof import('element-plus')['ElForm']>()

/** 新增模式 */
const init = () => {
  setVisible(true)
}

/** 编辑模式 */
const initEdit = (row: XxxListItemModel) => {
  resetForm()
  form.value = { ...row }
  setVisible(true)
}

/** 提交 */
const handleSubmit = async () => {
  try {
    setLoading(true)
    await FormRef.value?.validate()
    const { message } = await (isEdit.value ? update(form.value) : add(form.value))
    ElMessage.success(message)
    setVisible(false)
    emit('submitted')
  }
  catch (error) {
    console.error('handleSubmit => error', error)
  }
  finally {
    setLoading(false)
  }
}

/** 关闭重置 */
const close = () => {
  resetForm()
}

defineExpose({ init, initEdit })
</script>

<template>
  <ElDialog v-model="visible" :title="dialogTitle" width="500px" @closed="close">
    <ElForm ref="FormRef" v-loading="loading" :model="form" :rules="rules" label-width="120px">
      <GXForm :items="formItems" :form="form" />
      <!-- 复杂字段手动补充示例 -->
      <!--
      <ElFormItem label="xxx" prop="xxx">
        <CustomComponent v-model="form.xxx" />
      </ElFormItem>
      -->
    </ElForm>
    <template #footer>
      <ElButton :loading="loading" @click="setVisible(false)">取消</ElButton>
      <ElButton type="primary" :loading="loading" @click="handleSubmit">确定</ElButton>
    </template>
  </ElDialog>
</template>
```

### 6. 主页面集成

完整 `index.vue`：

**关键细节**：

- `defineOptions({ name: 'XxxManage' })` 设置组件名称
- `defineAsyncComponent` 异步加载弹窗组件
- 模板根节点为 `<div class="模块名-kebab-case">`
- 操作列通过 `#action` slot 渲染
- 删除操作使用 try/catch 错误处理

```vue
<script setup lang="ts">
import { defineAsyncComponent, h, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCompRef, useStateRef, useTablePage } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GXPaginationTable, GXSearch, generateFormItems, generateTableColumns } from '@gx-web/ep-comp'
import { XxxQueryModel, XxxListItemModel } from './model'
import { loadPage, removeById } from './api'

defineOptions({
  name: 'XxxManage'
})

const XxxAdd = defineAsyncComponent(() => import('./components/xxx-add.vue'))

const XxxAddRef = useCompRef(XxxAdd)

const [search, , resetSearch] = useStateRef(() => getModelFromJson(XxxQueryModel))

const [list, { page, loading, loadList, reloadList, onChange }] = useTablePage<XxxListItemModel>(
  ({ current, size }) =>
    loadPage({ ...search.value, pageNum: current, pageSize: size }).then(res => ({
      records: res.data.records,
      total: res.data.total
    }))
)

const columns = generateTableColumns(XxxListItemModel, [
  'name',
  'remark',
  'createdTime'
])

const searchItems = generateFormItems(XxxQueryModel, [
  'name'
])

/** 新增 */
const handleAdd = () => {
  XxxAddRef.value?.init()
}

/** 编辑 */
const handleEdit = (row: XxxListItemModel) => {
  XxxAddRef.value?.initEdit(row)
}

/** 删除 */
const handleDel = async (row: XxxListItemModel) => {
  try {
    const { message } = await removeById(row.id)
    ElMessage.success(message)
    loadList()
  }
  catch (error) {
    console.error('error =>', error)
  }
}

onMounted(loadList)
</script>

<template>
  <div class="xxx-manage">
    <GXPaginationTable
      v-model:page="page.current"
      v-model:limit="page.size"
      :columns="columns"
      :data="list"
      :loading="loading"
      :total="page.total"
      @pagination="onChange"
    >
      <template #header>
        <GXSearch v-model="search" :items="searchItems" @submit="loadList" @reset="resetSearch();reloadList()" />
      </template>

      <template #action="{ row }">
        <ElButton link type="primary" @click="handleEdit(row)">编辑</ElButton>
        <ElPopconfirm title="是否删除?" placement="left" @confirm="handleDel(row)">
          <template #reference>
            <ElButton link type="danger">删除</ElButton>
          </template>
        </ElPopconfirm>
      </template>

      <template #action-bar>
        <ElButton type="primary" @click="handleAdd">新增</ElButton>
      </template>
    </GXPaginationTable>
    <XxxAdd ref="XxxAddRef" @submitted="reloadList" />
  </div>
</template>
```

### 7. 类型导出

各目录 `index.ts` 统一导出：

```ts
// model/index.ts — 已在模型定义文件中直接 export
// api/index.ts — 已在 API 定义文件中直接 export
```

### 8. 待确认项

扩展现有待确认项，新增：

- 弹窗表单字段是否与列表展示字段一致
- 是否有复杂字段需要手动覆盖（树选择器、上传等）
- 操作列按钮权限控制
- 是否需要详情页
- 弹窗宽度是否合适

## reference.md 变更

需要补充以下内容：

### `useCompRef`（来自 `@gx-web/tool`）

```ts
function useCompRef<T extends abstract new (...args: any) => any>(
  component: T
): Ref<InstanceType<T> | undefined>
```

用于获取子组件 ref，配合 `defineExpose` 使用。

### `useToggle`（来自 `@gx-web/tool`）

```ts
function useToggle(defaultValue?: boolean): [Ref<boolean>, (value?: boolean) => void]
```

布尔值状态切换，常用于 loading 切换和对话框显隐。默认值为 `false`。

## examples/ 变更

### 新增文件

- `examples/components/xxx-add.vue` — 弹窗组件示例
- `examples/components/index.ts` — 导出

### 更新文件

- `examples/model/index.ts` — 新增 `XxxFormModel`
- `examples/api/index.ts` — 新增 `add` / `update` / `removeById`
- `examples/index.vue` — 集成弹窗 + 操作列 + 新增按钮

## SKILL.md 关键变更点

1. **Overview**：更新描述为"生成完整 CRUD 页面"而非"单个分页查询页面"
2. **Output Format**：从五段式改为八段式
3. **新增"弹窗组件"段落**：定义弹窗组件的生成规则和混合模式策略
4. **新增"主页面集成"段落**：定义完整 index.vue 的集成模板
5. **扩展 Model 段落**：新增 `XxxFormModel` 规则和字段块注释要求
6. **扩展 API 段落**：新增 CRUD 四接口生成规则
7. **扩展表格分页段落**：操作列统一使用 `#action` slot，不使用 render/JSX
8. **When NOT to Use**：移除"用户要做的是新增页、详情页、弹窗页"的限制
9. **Default Behavioral Constraints**：从"默认只做单个分页查询页面"改为"默认生成完整 CRUD 页面"
10. **代码规范细节**：`defineOptions` 设置组件名称、`defineAsyncComponent` 异步加载弹窗、模板单根节点 `<div class="模块名">`、CRUD 操作 try/catch 错误处理、弹窗提交 loading 状态

## 不变更的部分

- 查询表单生成逻辑（段落 3）
- 待确认项的核心规则（段落 8）
- Field Inference Rules
- Response Structure Convention
- Do Not Guess 规则
- Degrade Gracefully 策略
- Input Sources 支持范围
