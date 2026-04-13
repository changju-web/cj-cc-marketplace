# crud-page skill 扩展为完整 CRUD 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 ep-comp:crud-page skill 从分页查询页生成扩展为完整 CRUD 页面生成，包含新增/编辑弹窗组件和完整 API 脚手架。

**Architecture:** 在现有 SKILL.md 基础上扩展输出结构（五段式→八段式），新增弹窗组件和 CRUD API 生成规则，同步更新 reference.md 和 examples/。

**Tech Stack:** Vue 3 + TypeScript + @gx-web/ep-comp + Element Plus

---

## File Structure

| 操作 | 文件路径 | 职责 |
|------|----------|------|
| Modify | `ep-comp/skills/crud-page/reference.md` | 新增 `useCompRef`、`useToggle` API 参考，更新完整列表页模板 |
| Modify | `ep-comp/skills/crud-page/examples/model/index.ts` | 新增 `AlarmFormModel`，补充块注释 |
| Modify | `ep-comp/skills/crud-page/examples/api/index.ts` | 新增 `add`、`update`、`removeById` 接口 |
| Create | `ep-comp/skills/crud-page/examples/components/alarm-add.vue` | 新增/编辑弹窗组件示例 |
| Modify | `ep-comp/skills/crud-page/examples/index.vue` | 集成弹窗 + 操作列 + 新增按钮 |
| Modify | `ep-comp/skills/crud-page/SKILL.md` | 核心规则文档更新（最大改动） |

---

### Task 1: 更新 reference.md — 新增 API 参考

**Files:**

- Modify: `ep-comp/skills/crud-page/reference.md`

- [ ] **Step 1: 在 `## 2. @gx-web/tool — Hooks` 末尾新增 `useCompRef` 和 `useToggle` 小节**

在 `useStateRef` 小节的 `---` 分隔线之前，插入以下内容：

```markdown
### useCompRef

用于获取子组件 ref，配合 `defineExpose` 使用。

**签名：**

```ts
function useCompRef<T extends abstract new (...args: any) => any>(
  component: T
): Ref<InstanceType<T> | undefined>
```

**使用示例：**

```ts
// 引用自定义组件
import XxxAdd from './components/xxx-add.vue'
const XxxAddRef = useCompRef(XxxAdd)
XxxAddRef.value?.init()

// 引用 Element Plus 组件
const FormRef = useCompRef<typeof import('element-plus')['ElForm']>()
await FormRef.value?.validate()
```

**要点：**

- 对于自定义组件，传入组件本身（非字符串），返回类型自动推断 `defineExpose` 暴露的方法
- 对于 Element Plus 内置组件，使用 `typeof import('element-plus')['ElXxx']` 获取类型

### useToggle

布尔值状态切换，常用于 loading 切换和对话框显隐。默认值为 `false`。

**签名：**

```ts
function useToggle(defaultValue?: boolean): [Ref<boolean>, (value?: boolean) => void]
```

**使用示例：**

```ts
// 对话框显隐
const [visible, setVisible] = useToggle(false)
setVisible(true)   // 打开
setVisible(false)  // 关闭

// Loading 状态
const [loading, setLoading] = useToggle(false)
setLoading(true)   // 开始加载
setLoading(false)  // 结束加载
```
```

- [ ] **Step 2: 更新 `## 6. 完整列表页模板`，替换为完整 CRUD 模板**

将现有的 `## 6. 完整列表页模板` 整个章节替换为以下内容：

```markdown
## 6. 完整 CRUD 页面模板

### Model 文件模板

```ts
// model/index.ts
import { FieldName } from '@gx-web/core'

/** 查询参数模型 */
export class XxxQueryModel {
  /** 关键字 */
  @FieldName('关键字')
  keyword!: string
}

/** 列表项模型 */
export class XxxListItemModel {
  /** 字段1 */
  @FieldName('字段1')
  field1!: string

  /** 字段2 */
  @FieldName('字段2')
  field2!: string

  id!: string
}

/** 新增/编辑表单模型 */
export class XxxFormModel {
  /** 字段1 */
  @FieldName('字段1')
  field1!: string

  /** 字段2 */
  @FieldName('字段2')
  field2!: string

  id!: string
}
```

### API 文件模板

```ts
// api/index.ts
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

### 弹窗组件模板

```vue
<!-- components/xxx-add.vue -->
<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
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
  field1: [{ required: true, message: '请输入字段1', trigger: 'blur' }]
})

const dialogTitle = computed(() => `${isEdit.value ? '编辑' : '新增'}xxx`)

// 简单字段自动生成
const formItems = generateFormItems(XxxFormModel, [
  'field1',
  'field2'
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

### 主页面模板

```vue
<!-- index.vue -->
<script setup lang="ts">
import { defineAsyncComponent, onMounted } from 'vue'
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
  'field1',
  'field2'
])

const searchItems = generateFormItems(XxxQueryModel, [
  'keyword'
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
```

- [ ] **Step 3: 更新 reference.md 开头的 API Reference 总览**

在 `## API Reference` 总览部分（SKILL.md 引用的内容），需要确保 `useCompRef` 和 `useToggle` 已在 `@gx-web/tool` 条目中列出。这一步仅做确认，无需修改（已在 Step 1 中添加）。

- [ ] **Step 4: Commit**

```bash
git add ep-comp/skills/crud-page/reference.md
git commit -m "docs: 更新 reference.md，新增 useCompRef/useToggle API 参考和完整 CRUD 模板"
```

---

### Task 2: 更新 examples/model/index.ts — 新增 FormModel + 块注释

**Files:**

- Modify: `ep-comp/skills/crud-page/examples/model/index.ts`

- [ ] **Step 1: 用完整内容替换现有文件**

将文件替换为以下内容（新增 `AlarmFormModel`，为所有字段添加块注释，为类添加块注释）：

```ts
import { FieldName } from '@gx-web/core'

/** 告警查询模型 */
export class AlarmQueryModel {
  /** 设备SN */
  @FieldName('设备SN')
  deviceSn!: string
}

/** 告警列表项模型 */
export class AlarmVO {
  /** 告警代码 */
  @FieldName('告警代码')
  alarmCode!: string

  /** 告警详情 */
  @FieldName('告警详情')
  alarmDetail!: string

  /** 告警时间 */
  @FieldName('告警时间')
  alarmTime!: string

  /** 告警标题 */
  @FieldName('告警标题')
  alarmTitle!: string

  /** 入库时间 */
  @FieldName('入库时间')
  createTime!: string

  /** 设备SN */
  @FieldName('设备SN')
  deviceSn!: string

  /** 主键ID */
  @FieldName('主键ID')
  id!: string

  /** 场所ID */
  @FieldName('场所ID')
  placeId!: string
}

/** 告警新增/编辑表单模型 */
export class AlarmFormModel {
  /** 告警代码 */
  @FieldName('告警代码')
  alarmCode!: string

  /** 告警标题 */
  @FieldName('告警标题')
  alarmTitle!: string

  /** 告警详情 */
  @FieldName('告警详情')
  alarmDetail!: string

  id!: string
}
```

- [ ] **Step 2: Commit**

```bash
git add ep-comp/skills/crud-page/examples/model/index.ts
git commit -m "docs: 新增 AlarmFormModel 和块注释到 examples/model"
```

---

### Task 3: 更新 examples/api/index.ts — 完整 CRUD API

**Files:**

- Modify: `ep-comp/skills/crud-page/examples/api/index.ts`

- [ ] **Step 1: 用完整内容替换现有文件**

将文件替换为以下内容（扩展为完整 CRUD 四接口）：

```ts
import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmVO, AlarmQueryModel, AlarmFormModel } from '../model'

const request = useAxios()

/** 分页查询 */
export const loadPage = (params: AlarmQueryModel) => {
  return request.get<ResPage<AlarmVO>>({
    url: `/zl-business/alarm/record/page`,
    params: {
      ...params,
      pageOrder: 'create_time desc'
    }
  })
}

/** 新增 */
export const add = (data: AlarmFormModel) => {
  return request.post({
    url: `/zl-business/alarm/record`,
    data
  })
}

/** 更新 */
export const update = (data: AlarmFormModel) => {
  return request.put({
    url: `/zl-business/alarm/record`,
    data
  })
}

/** 删除 */
export const removeById = (id: string) => {
  return request.delete({
    url: `/zl-business/alarm/record/${id}`
  })
}
```

- [ ] **Step 2: Commit**

```bash
git add ep-comp/skills/crud-page/examples/api/index.ts
git commit -m "docs: 扩展 examples/api 为完整 CRUD 四接口"
```

---

### Task 4: 创建 examples/components/alarm-add.vue — 弹窗组件示例

**Files:**

- Create: `ep-comp/skills/crud-page/examples/components/alarm-add.vue`

- [ ] **Step 1: 创建弹窗组件文件**

```vue
<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useCompRef, useStateRef, useToggle } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { generateFormItems, GXForm } from '@gx-web/ep-comp'
import { add, update } from '../api'
import type { AlarmVO } from '../model'
import { AlarmFormModel } from '../model'

defineOptions({
  name: 'AlarmAdd'
})

const emit = defineEmits<{
  submitted: []
}>()

const [visible, setVisible] = useToggle(false)

const [loading, setLoading] = useToggle(false)

const [form, , resetForm] = useStateRef(() => getModelFromJson(AlarmFormModel))

const isEdit = computed(() => !!form.value.id)

const rules = reactive<FormRules>({
  alarmCode: [{ required: true, message: '请输入告警代码', trigger: 'blur' }],
  alarmTitle: [{ required: true, message: '请输入告警标题', trigger: 'blur' }]
})

const dialogTitle = computed(() => `${isEdit.value ? '编辑' : '新增'}告警`)

// 简单字段自动生成
const formItems = generateFormItems(AlarmFormModel, [
  'alarmCode',
  'alarmTitle',
  'alarmDetail'
])

const FormRef = useCompRef<typeof import('element-plus')['ElForm']>()

/** 新增模式 */
const init = () => {
  setVisible(true)
}

/** 编辑模式 */
const initEdit = (row: AlarmVO) => {
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
    </ElForm>
    <template #footer>
      <ElButton :loading="loading" @click="setVisible(false)">取消</ElButton>
      <ElButton type="primary" :loading="loading" @click="handleSubmit">确定</ElButton>
    </template>
  </ElDialog>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add ep-comp/skills/crud-page/examples/components/alarm-add.vue
git commit -m "docs: 新增弹窗组件示例 alarm-add.vue"
```

---

### Task 5: 更新 examples/index.vue — 完整 CRUD 主页面

**Files:**

- Modify: `ep-comp/skills/crud-page/examples/index.vue`

- [ ] **Step 1: 用完整内容替换现有文件**

```vue
<script setup lang="ts">
import { defineAsyncComponent, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCompRef, useStateRef, useTablePage } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GXPaginationTable, GXSearch, generateFormItems, generateTableColumns } from '@gx-web/ep-comp'
import { AlarmQueryModel, AlarmVO } from './model'
import { loadPage, removeById } from './api'

defineOptions({
  name: 'AlarmManage'
})

const AlarmAdd = defineAsyncComponent(() => import('./components/alarm-add.vue'))

const AlarmAddRef = useCompRef(AlarmAdd)

const [search, , resetSearch] = useStateRef(() => getModelFromJson(AlarmQueryModel))

const [list, { page, loading, loadList, reloadList, onChange }] = useTablePage<AlarmVO>(
  ({ current, size }) =>
    loadPage({ ...search.value, pageNum: current, pageSize: size }).then(res => ({
      records: res.data.records,
      total: res.data.total
    }))
)

const columns = generateTableColumns(AlarmVO, [
  'deviceSn',
  'placeId',
  'alarmCode',
  'alarmTitle',
  'alarmDetail',
  'alarmTime',
  'createTime'
])

const searchItems = generateFormItems(AlarmQueryModel, [
  'deviceSn'
])

/** 新增 */
const handleAdd = () => {
  AlarmAddRef.value?.init()
}

/** 编辑 */
const handleEdit = (row: AlarmVO) => {
  AlarmAddRef.value?.initEdit(row)
}

/** 删除 */
const handleDel = async (row: AlarmVO) => {
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
  <div class="alarm-manage">
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
    <AlarmAdd ref="AlarmAddRef" @submitted="reloadList" />
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add ep-comp/skills/crud-page/examples/index.vue
git commit -m "docs: 更新 examples/index.vue 为完整 CRUD 页面"
```

---

### Task 6: 更新 SKILL.md — 核心规则扩展

这是最大的改动。需要在现有 SKILL.md 上进行多处精确修改。

**Files:**

- Modify: `ep-comp/skills/crud-page/SKILL.md`

- [ ] **Step 1: 更新 frontmatter description**

将第 3 行 description 中的 `pagination list page` 改为 `CRUD page`：

```markdown
description: Generate ep-comp CRUD page scaffolds from Swagger, Knife4j, OpenAPI JSON, or request/response examples. Use this whenever the user wants to turn API docs into `generateTableColumns`, `generateFormItems`, `useTablePage`, `GXForm`, `GXPaginationTable`, and CRUD dialog components based pages, even if they only say "根据 Swagger 生成列表页". If the context clearly points to an `@gx-web/ep-comp` page, use this skill proactively.
```

- [ ] **Step 2: 更新 Overview**

将第 10-20 行替换为：

```markdown
这个 skill 用于把 Swagger / Knife4j / OpenAPI 文档，或用户直接提供的请求/响应示例，转成基于 `@gx-web/ep-comp` 的 **完整 CRUD 页面**接入代码。

目标不是解释单个组件 API，而是生成 CRUD 页面主链路：

- `generateTableColumns`
- `generateFormItems`
- `useTablePage`
- `GXForm`
- `GXPaginationTable`
- 新增/编辑弹窗组件（`ElDialog` + 表单验证 + `defineExpose`）
- 完整 CRUD API（查询/新增/编辑/删除）

默认生成**完整 CRUD 页面**，包含分页查询、新增/编辑弹窗、操作列（编辑/删除）。
```

- [ ] **Step 3: 更新 When NOT to Use**

将第 43 行删除（移除"用户要做的是新增页、详情页、弹窗页，而不是分页列表页"限制）：

替换第 40-45 行为：

```markdown
- 用户只问 `generateTableColumns` 的单独用法
- 用户只问 `GXForm` 或 `GXPaginationTable` 的 props
- 用户给的是接口文档，但目标不是 `ep-comp` 体系
- 用户仅想阅读 Swagger 文档，不需要生成页面骨架
- 用户要做的是纯详情页（无 CRUD 操作），而非列表 CRUD 页面
```

- [ ] **Step 4: 更新 Output Format**

将第 113-119 行（五段式）替换为：

```markdown
输出固定为以下八段，顺序不要变：

1. `Model`
2. `API`
3. `查询表单`
4. `表格分页 + 操作列`
5. `弹窗组件`
6. `主页面集成`
7. `类型导出`
8. `待确认项`
```

- [ ] **Step 5: 扩展 Model 段落（第 125-142 行）**

将 `## 1. Model` 段落替换为：

```markdown
## 1. Model

至少生成：

- `XxxQueryModel` — 查询参数
- `XxxListItemModel` — 列表展示字段
- `XxxFormModel` — 新增/编辑表单字段

命名规则：

- 默认统一使用 `Model` 结尾
- 如果用户已显式给出命名，遵循用户命名
- 不默认切换到 `VO`

字段处理原则：

- 优先保留文档中能确认的字段
- 字段中文语义清楚时，可用 `@FieldName(...)`
- **所有字段必须添加 `/** ... */` 块注释**，确保 IDE 悬停可见
- **类本身也必须添加块注释**
- 块注释内容与 `@FieldName` 保持一致
- 类型或含义不明确时，不要强猜，统一放到"待确认项"里，并明确写出"需人工确认"

`XxxFormModel` 规则：

- 仅包含可编辑字段，不包含纯展示字段（如 `createdTime`、`updatedTime`）
- `id` 字段必须包含，用于区分新增/编辑模式
- 字段应与 API 文档中的新增/编辑请求体对应
```

- [ ] **Step 6: 扩展 API 段落（第 144-304 行区域）**

在 `## 2. API` 段落的"至少生成"部分（第 146-151 行），替换为：

```markdown
至少生成：

- 分页接口函数（`loadPage`）
- 新增接口函数（`add`）
- 更新接口函数（`update`）
- 删除接口函数（`removeById`）
- 请求参数类型
- 响应类型
- 与 `useTablePage` 对接的返回映射
```

在 API 段落的"约束"部分（第 153-158 行），追加一条：

```markdown
- `add` 和 `update` 使用 `XxxFormModel` 作为参数类型
- `removeById` 接受 `id: string`
- 所有 API 函数添加块注释说明用途
```

- [ ] **Step 7: 扩展表格分页段落（第 316-331 行）**

将 `## 4. 表格分页` 替换为：

```markdown
## 4. 表格分页 + 操作列

至少生成：

- `generateTableColumns(...)` — 只配置数据列，不包含操作列
- `useTablePage(...)`
- `GXPaginationTable` 示例
- `loading`、`page`、`total`、`onChange` 的联动方式
- 操作列（编辑/删除按钮）

这里必须遵循当前推荐链路：

- 使用 `generateTableColumns`
- 使用 `generateFormItems`
- 使用 `useTablePage`
- 使用 `GXForm`
- 使用 `GXPaginationTable`
- 不回退到已移除的 `getEPTableColumns`

操作列规则：

- **统一通过 `GXPaginationTable` 的 `#action` slot 渲染**，不在 `generateTableColumns` 中使用 render 配置
- 编辑按钮：`<ElButton link type="primary">`，调用弹窗组件的 `initEdit(row)` 方法
- 删除按钮：使用 `<ElPopconfirm title="是否删除?" placement="left">` 二次确认
- 删除操作使用 try/catch 错误处理

操作列 slot 模板：

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
```

- [ ] **Step 8: 在"查询表单"和"表格分页"之间新增两个段落**

在现有的 `## 3. 查询表单` 之后、新的 `## 4. 表格分页 + 操作列` 之后，插入两个新段落：

```markdown
## 5. 弹窗组件

生成独立文件 `components/xxx-add.vue`，使用 `ElDialog`。

核心模式：

- `defineOptions({ name: 'XxxAdd' })` 设置组件名称
- `useToggle` 管理显隐，额外维护 `loading` 状态
- `useStateRef` 管理表单数据（支持 reset）
- `computed` 判断 `isEdit`（基于 `form.value.id` 是否存在）
- `defineExpose({ init, initEdit })` 暴露方法给父组件
- 提交成功后 `emit('submitted')` 通知父组件刷新
- `@closed` 事件中重置表单
- CRUD 操作使用 try/catch/finally 错误处理，finally 中关闭 loading

表单生成策略（混合模式）：

1. 简单字段（input、select、textarea）：使用 `generateFormItems` + `GXForm` 自动生成
2. 复杂字段（树选择器、上传、自定义组件）：手动 `ElFormItem`
3. 在输出中明确标注哪些是自动生成、哪些需要手动补充

弹窗表单规范：

- `ElForm` 设置 `label-width="120px"`
- 表单验证使用 `reactive<FormRules>`
- 表单区域添加 `v-loading="loading"`
- 取消和确定按钮都添加 `:loading="loading"`

## 6. 主页面集成

生成完整 `index.vue`，集成搜索、表格、操作列和弹窗组件。

关键规范：

- `defineOptions({ name: 'XxxManage' })` 设置组件名称
- `defineAsyncComponent` 异步加载弹窗组件
- 模板根节点为 `<div class="模块名-kebab-case">`
- `GXSearch` 使用 `v-model="search"` 绑定
- 操作列通过 `#action` slot 渲染（见段落 4）
- 新增按钮通过 `#action-bar` slot 渲染
- 弹窗组件使用 `useCompRef` 获取引用
- 弹窗的 `@submitted` 事件触发 `reloadList()`
```

- [ ] **Step 9: 更新待确认项段落**

将 `## 5. 待确认项` 改为 `## 8. 待确认项`（因为前面插入了新段落 5-7）。

在"可后补"列表中追加：

```markdown
- 弹窗表单字段是否与列表展示字段一致
- 是否有复杂字段需要手动覆盖（树选择器、上传等）
- 操作列按钮权限控制
- 是否需要详情页
- 弹窗宽度是否合适
```

- [ ] **Step 10: 更新 Directory Contract**

将"必生成"部分替换为：

```markdown
### 必生成

- `api/index.ts`
- `model/index.ts`
- `index.vue`
- `components/xxx-add.vue`
```

- [ ] **Step 11: 更新 Default Behavioral Constraints**

将第 551-557 行替换为：

```markdown
- 默认生成完整 CRUD 页面（查询 + 新增/编辑弹窗 + 操作列）
- 默认不做额外抽象
- 优先给最小可用 CRUD 主链路
- 用户一旦提供目录结构，再切换到落地代码模式
```

- [ ] **Step 12: 更新 Example Framing**

将第 565 行中的 `五段结构` 改为 `八段结构`。

- [ ] **Step 13: 更新 Success Criteria**

将第 575-581 行替换为：

```markdown
一次成功输出至少应满足：

- 正确识别分页接口的请求参数与返回结构
- 输出 `Model`、`API`、`查询表单`、`表格分页 + 操作列`、`弹窗组件`、`主页面集成`、`类型导出`、`待确认项` 八段结构
- Model 包含 QueryModel、ListItemModel、FormModel 三个模型，所有字段含块注释
- API 包含 loadPage、add、update、removeById 四个接口
- 弹窗组件使用 ElDialog + try/catch/finally + loading 状态
- 主页面模板单根节点 `<div class="模块名">`，defineAsyncComponent 加载弹窗
- 推断项明确标注"需人工确认"
- 用户补充模块名或目录结构后，可继续生成落地代码
```

- [ ] **Step 14: 更新 API Reference 总览**

将第 587-593 行替换为：

```markdown
reference.md 包含以下内容：

- `@gx-web/core`：`@FieldName`、`getModelFromJson`、`getModelFieldName`
- `@gx-web/tool`：`useTablePage`、`useStateRef`、`useCompRef`、`useToggle`
- `@gx-web/ep-comp`：`generateTableColumns`、`generateFormItems`、`GXPaginationTable`、`GXForm`、`GXSearch`、`useComponentMap`
- 所有类型定义：`EPTableColumnConfigType`、`EPFormItemConfigType`、`GXFormProps`、`GXPaginationTableProps`
- 完整 CRUD 页面模板（index.vue + model + api + dialog component）
```

- [ ] **Step 15: Commit**

```bash
git add ep-comp/skills/crud-page/SKILL.md
git commit -m "docs: 扩展 SKILL.md 为完整 CRUD 八段式生成规则"
```

---

### Task 7: 更新 CLAUDE.md 目录结构说明

**Files:**

- Modify: `.claude-plugin/marketplace.json`（无变更，仅确认）

无变更。确认 `ep-comp` 插件已正确注册。

- [ ] **Step 1: 验证文件完整性**

确认以下文件均存在且内容正确：

- `ep-comp/skills/crud-page/SKILL.md`
- `ep-comp/skills/crud-page/reference.md`
- `ep-comp/skills/crud-page/examples/model/index.ts`
- `ep-comp/skills/crud-page/examples/api/index.ts`
- `ep-comp/skills/crud-page/examples/components/alarm-add.vue`
- `ep-comp/skills/crud-page/examples/index.vue`

- [ ] **Step 2: 最终 Commit（如有遗漏修正）**

```bash
git add -A
git commit -m "docs: crud-page skill 完整 CRUD 扩展完成"
```
