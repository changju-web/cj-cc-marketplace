# ep-comp Skill 拆分 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `ep-comp/skills/crud-page` 拆分为 `table-page`、`form-dialog`、`detail-dialog` 三个 skill，并把 `crud-page` 收敛为兼容入口与调度说明。

**Architecture:** 以现有 `crud-page` 的规则、示例和 reference 为基础，抽出“列表页底座”“表单弹窗增量注入”“详情弹窗增量注入”三类单一职责 skill。`crud-page` 不再继续承担完整页面直接生成的唯一入口，而是保留为兼容入口：说明默认推荐链路、转发到新 skill，并保留必要的历史约束说明，避免已有用户心智断裂。

**Tech Stack:** Markdown skill spec、Vue 3、TypeScript、`@gx-web/ep-comp`、Element Plus、示例文件、Git

---

## File Structure

| 操作 | 文件路径 | 职责 |
|---|---|---|
| Modify | `ep-comp/skills/crud-page/SKILL.md` | 把旧的“完整 CRUD 页面生成”改为兼容入口与调度说明 |
| Modify | `ep-comp/skills/crud-page/reference.md` | 提炼共享 reference，删除与旧默认行为冲突的描述 |
| Modify | `ep-comp/skills/crud-page/examples/index.vue` | 把示例改成直接 `import` 组件，去掉 `defineAsyncComponent` |
| Modify | `ep-comp/skills/crud-page/examples/components/alarm-add.vue` | 保留为表单弹窗自动模式示例，修正为可直接作为 `form-dialog` 参考 |
| Modify | `ep-comp/skills/crud-page/examples/api/index.ts` | 保留 CRUD API 示例，作为兼容入口 reference 的共享示例 |
| Modify | `ep-comp/skills/crud-page/examples/model/index.ts` | 保留 Query/List/Form 模型示例，供三个新 skill 共用命名约定 |
| Create | `ep-comp/skills/table-page/SKILL.md` | 新的表格页 skill 主说明 |
| Create | `ep-comp/skills/table-page/reference.md` | 仅面向 table-page 的 reference 和模板 |
| Create | `ep-comp/skills/table-page/examples/index.vue` | 纯列表页示例 |
| Create | `ep-comp/skills/table-page/examples/api/index.ts` | 仅 `loadPage` 示例 |
| Create | `ep-comp/skills/table-page/examples/model/index.ts` | QueryModel + ListItemModel 示例 |
| Create | `ep-comp/skills/form-dialog/SKILL.md` | 新的表单弹窗 skill 主说明 |
| Create | `ep-comp/skills/form-dialog/reference.md` | 自动模式 / 原生模式 / 注入规则 reference |
| Create | `ep-comp/skills/form-dialog/examples/index.vue` | 已存在 table-page 的集成示例 |
| Create | `ep-comp/skills/form-dialog/examples/components/alarm-add.vue` | 自动模式表单弹窗示例 |
| Create | `ep-comp/skills/form-dialog/examples/components/alarm-audit.vue` | 原生模式审批弹窗示例 |
| Create | `ep-comp/skills/form-dialog/examples/api/index.ts` | `add` / `update` / `audit` 示例 |
| Create | `ep-comp/skills/form-dialog/examples/model/index.ts` | Form/Audit 模型示例 |
| Create | `ep-comp/skills/detail-dialog/SKILL.md` | 新的详情弹窗 skill 主说明 |
| Create | `ep-comp/skills/detail-dialog/reference.md` | 详情只读展示与注入规则 reference |
| Create | `ep-comp/skills/detail-dialog/examples/index.vue` | 已存在 table-page 的详情集成示例 |
| Create | `ep-comp/skills/detail-dialog/examples/components/detail.vue` | 详情弹窗示例 |
| Create | `ep-comp/skills/detail-dialog/examples/api/index.ts` | `loadDetail` 示例 |
| Create | `ep-comp/skills/detail-dialog/examples/model/index.ts` | DetailModel 示例 |

---

### Task 1: 重写 `crud-page` 为兼容入口

**Files:**
- Modify: `ep-comp/skills/crud-page/SKILL.md`
- Modify: `ep-comp/skills/crud-page/reference.md`

- [ ] **Step 1: 先阅读旧入口文案，标记必须保留的兼容信息**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" diff -- ep-comp/skills/crud-page/SKILL.md ep-comp/skills/crud-page/reference.md
```

Expected: 当前这两个文件没有本地未提交改动，便于直接重写兼容入口文案。

- [ ] **Step 2: 把 `ep-comp/skills/crud-page/SKILL.md` 的 frontmatter 和 Overview 改成兼容入口描述**

将文件开头改成以下结构：

```md
---
name: crud-page
description: Compatibility entry for ep-comp page generation. Route the user to `table-page`, `form-dialog`, and `detail-dialog`, while preserving legacy CRUD guidance for existing users.
---

# ep-comp CRUD 兼容入口

## Overview

这个 skill 不再直接承担“默认一次性生成完整 CRUD 页面”的主路径。

当前推荐链路为：

1. `table-page` — 先生成列表页骨架
2. `form-dialog` — 再按需追加新增 / 编辑 / 审核等提交型弹窗
3. `detail-dialog` — 再按需追加详情弹窗

`crud-page` 的职责改为：

- 识别用户当前需求应该路由到哪个新 skill
- 在用户仍然按“完整 CRUD 页面”心智描述需求时，解释新的拆分方式
- 保留兼容术语与共享约束，避免老用户完全失去上下文
```

- [ ] **Step 3: 在 `crud-page` 中增加兼容路由规则，替换旧的默认输出承诺**

在 `When to Use` 和 `Default Behavioral Constraints` 一带，写入以下规则：

```md
## Routing Rules

- 用户只要列表页 / 查询页 / page 接入：转到 `table-page`
- 用户要新增、编辑、审核、启停、分配、导入等提交型弹窗：转到 `form-dialog`
- 用户要详情、只读展示、描述型弹窗：转到 `detail-dialog`
- 用户说“按原来 CRUD 一次性生成”：先解释拆分后的推荐链路，再根据明确范围调用对应新 skill

## Compatibility Notes

- 仍可复用 `crud-page` 中已有的术语：`Model`、`API`、`主页面集成`
- 但不再承诺默认一次性输出完整 CRUD 页面
- 如果用户坚持一个入口完成所有内容，也应先生成 `table-page`，再继续追加 dialog 能力，而不是重写整个页面
```

- [ ] **Step 4: 把 `crud-page/reference.md` 改成共享契约 reference，而不是旧版大一统模板**

保留并集中以下共享内容：

```md
## Shared Contracts

### 根节点 contract

```vue
<template>
  <div class="module-kebab-case">
    <GxPaginationTable ... />
    <XxxDialog ref="XxxDialogRef" @submitted="reloadList" />
  </div>
</template>
```

### 挂点 contract

- `#header`：查询区
- `#action`：行级操作
- `#action-bar`：页面级操作

### 增量注入 contract

只允许做以下五类增量修改：
1. 追加 import
2. 追加组件 ref
3. 追加 handler
4. 向 `#action` / `#action-bar` 注入按钮
5. 在根 `div` 内追加组件实例
```

- [ ] **Step 5: 验证 `crud-page` 已不再要求 `defineAsyncComponent`，并且文案明确为兼容入口**

Run:
```bash
rg -n "defineAsyncComponent|默认生成完整 CRUD 页面|一次性生成完整 CRUD" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/crud-page/SKILL.md" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/crud-page/reference.md"
```

Expected:
- 不再出现 `defineAsyncComponent`
- 可以出现“兼容入口”
- 不再把“默认一次性生成完整 CRUD 页面”写成主路径承诺

- [ ] **Step 6: 提交兼容入口重写**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ep-comp/skills/crud-page/SKILL.md ep-comp/skills/crud-page/reference.md && git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "$(cat <<'EOF'
refactor(ep-comp): 将 crud-page 调整为兼容入口
EOF
)"
```

Expected: 生成一条只包含 `crud-page` 文案与 shared contract 改动的独立提交。

---

### Task 2: 落地 `table-page` skill

**Files:**
- Create: `ep-comp/skills/table-page/SKILL.md`
- Create: `ep-comp/skills/table-page/reference.md`
- Create: `ep-comp/skills/table-page/examples/index.vue`
- Create: `ep-comp/skills/table-page/examples/api/index.ts`
- Create: `ep-comp/skills/table-page/examples/model/index.ts`

- [ ] **Step 1: 创建 `table-page` 目录与最小文件骨架**

Run:
```bash
mkdir -p "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/table-page/examples/api" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/table-page/examples/model"
```

Expected: `table-page` skill 目录和 `examples/api`、`examples/model` 目录创建完成。

- [ ] **Step 2: 编写 `table-page/SKILL.md`，只保留列表页职责**

写入以下核心结构：

```md
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
```

- [ ] **Step 3: 编写 `table-page/reference.md`，提供纯列表页模板**

写入以下最小模板：

```md
## index.vue template

```vue
<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import { useStateRef, useTablePage } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxPaginationTable, GxSearch, generateFormItems, generateTableColumns } from '@gx-web/ep-comp'
import { XxxQueryModel, XxxListItemModel } from './model'
import { loadPage } from './api'

defineOptions({
  name: 'XxxManage'
})

const [search, , resetSearch] = useStateRef(() => getModelFromJson(XxxQueryModel))

const [list, { page, loading, loadList, reloadList, onChange }] = useTablePage<XxxListItemModel>(
  ({ current, size }) =>
    loadPage({ ...search.value, pageNum: current, pageSize: size }).then(res => ({
      records: res.data.records,
      total: res.data.total
    }))
)

const columns = generateTableColumns(XxxListItemModel, ['field1', 'field2'])
const searchItems = generateFormItems(XxxQueryModel, ['keyword'])

onMounted(loadList)
</script>

<template>
  <div class="xxx-manage">
    <GxPaginationTable
      v-model:page="page.current"
      v-model:limit="page.size"
      :columns="columns"
      :data="list"
      :loading="loading"
      :total="page.total"
      @pagination="onChange"
    >
      <template #header>
        <GxSearch v-model="search" :items="searchItems" @submit="loadList" @reset="resetSearch();reloadList()" />
      </template>

      <template #action="{ row }">
        <ElButton link type="primary">详情</ElButton>
      </template>

      <template #action-bar />
    </GxPaginationTable>
  </div>
</template>
```
```

- [ ] **Step 4: 编写 `table-page/examples` 示例文件**

`examples/model/index.ts` 写入：

```ts
import { FieldName } from '@gx-web/core'

export class AlarmQueryModel {
  @FieldName('设备SN')
  deviceSn!: string
}

export class AlarmListItemModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  @FieldName('入库时间')
  createTime!: string

  id!: string
}
```

`examples/api/index.ts` 写入：

```ts
import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmListItemModel, AlarmQueryModel } from '../model'

const request = useAxios()

export const loadPage = (params: AlarmQueryModel) => {
  return request.get<ResPage<AlarmListItemModel>>({
    url: `/zl-business/alarm/record/page`,
    params: {
      ...params,
      pageOrder: 'create_time desc'
    }
  })
}
```

`examples/index.vue` 写入：

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useStateRef, useTablePage } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxPaginationTable, GxSearch, generateFormItems, generateTableColumns } from '@gx-web/ep-comp'
import { AlarmQueryModel, AlarmListItemModel } from './model'
import { loadPage } from './api'

defineOptions({
  name: 'AlarmManage'
})

const [search, , resetSearch] = useStateRef(() => getModelFromJson(AlarmQueryModel))

const [list, { page, loading, loadList, reloadList, onChange }] = useTablePage<AlarmListItemModel>(
  ({ current, size }) =>
    loadPage({ ...search.value, pageNum: current, pageSize: size }).then(res => ({
      records: res.data.records,
      total: res.data.total
    }))
)

const columns = generateTableColumns(AlarmListItemModel, ['alarmCode', 'alarmTitle', 'createTime'])
const searchItems = generateFormItems(AlarmQueryModel, ['deviceSn'])

onMounted(loadList)
</script>

<template>
  <div class="alarm-manage">
    <GxPaginationTable
      v-model:page="page.current"
      v-model:limit="page.size"
      :columns="columns"
      :data="list"
      :loading="loading"
      :total="page.total"
      @pagination="onChange"
    >
      <template #header>
        <GxSearch v-model="search" :items="searchItems" @submit="loadList" @reset="resetSearch();reloadList()" />
      </template>

      <template #action-bar />
      <template #action="{ row }">
        <ElButton link type="primary">详情</ElButton>
      </template>
    </GxPaginationTable>
  </div>
</template>
```

- [ ] **Step 5: 验证 `table-page` 没有越权承担 dialog 责任**

Run:
```bash
rg -n "initEdit|GxDialog|loadDetail|audit\(|add\(|update\(" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/table-page"
```

Expected: 不应出现 `GxDialog`、`loadDetail`、`audit`；`add` / `update` 也不应存在于 `table-page` 目录中。

- [ ] **Step 6: 提交 `table-page` skill**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ep-comp/skills/table-page && git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "$(cat <<'EOF'
feat(ep-comp): 新增 table-page skill
EOF
)"
```

Expected: 新 skill 独立提交，便于后续 review 只看列表页底座。

---

### Task 3: 落地 `form-dialog` skill

**Files:**
- Create: `ep-comp/skills/form-dialog/SKILL.md`
- Create: `ep-comp/skills/form-dialog/reference.md`
- Create: `ep-comp/skills/form-dialog/examples/index.vue`
- Create: `ep-comp/skills/form-dialog/examples/components/alarm-add.vue`
- Create: `ep-comp/skills/form-dialog/examples/components/alarm-audit.vue`
- Create: `ep-comp/skills/form-dialog/examples/api/index.ts`
- Create: `ep-comp/skills/form-dialog/examples/model/index.ts`
- Modify: `ep-comp/skills/crud-page/examples/components/alarm-add.vue`

- [ ] **Step 1: 创建 `form-dialog` 目录与组件目录**

Run:
```bash
mkdir -p "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/form-dialog/examples/components" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/form-dialog/examples/api" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/form-dialog/examples/model"
```

Expected: `form-dialog` 目录与 `examples/components` 等子目录创建完成。

- [ ] **Step 2: 编写 `form-dialog/SKILL.md`，明确自动模式 / 原生模式与确认规则**

写入以下核心段落：

```md
---
name: form-dialog
description: Add form-based dialogs to an existing ep-comp table page. Supports automatic mode with `generateFormItems + GxForm` and native mode with `ElForm`, but native mode requires explicit user confirmation.
---

## Modes

### 自动模式
- 适用于标准 input/select/textarea 等字段
- 生成方式：`generateFormItems + GxForm`

### 原生模式
- 适用于审核、强联动、自定义布局、复杂业务组件
- 生成方式：`ElForm + ElFormItem + 业务组件`
- 触发条件：先解释复杂点，再经用户确认后生成
```

- [ ] **Step 3: 编写 `form-dialog/reference.md`，放入增量注入模板与幂等检查清单**

写入以下模板：

```md
## Incremental Injection Checklist

每次注入前必须检查：
- import 是否已存在
- ref 是否已存在
- handler 是否已存在
- 按钮是否已存在
- 组件实例是否已存在

## 自动模式组件模板

```vue
<script setup lang="ts">
import { computed, reactive, useTemplateRef } from 'vue'
import type { FormRules } from 'element-plus'
import { ElButton, ElMessage } from 'element-plus'
import { useStateRef, useToggle } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { generateFormItems, GxDialog, GxForm } from '@gx-web/ep-comp'
import { add, update } from '../api'
import type { AlarmListItemModel } from '../model'
import { AlarmFormModel } from '../model'

const emit = defineEmits<{ submitted: [] }>()
const [visible, setVisible] = useToggle(false)
const [loading, setLoading] = useToggle(false)
const [form, , resetForm] = useStateRef(() => getModelFromJson(AlarmFormModel))
const isEdit = computed(() => !!form.value.id)
const rules = reactive<FormRules>({
  alarmCode: [{ required: true, message: '请输入告警代码', trigger: 'blur' }]
})
const formItems = generateFormItems(AlarmFormModel, ['alarmCode', 'alarmTitle'])
const FormRef = useTemplateRef('FormRef')
</script>
```

## 原生模式组件模板

```vue
<script setup lang="ts">
import { reactive, useTemplateRef } from 'vue'
import type { FormRules } from 'element-plus'
import { ElButton, ElForm, ElFormItem, ElInput, ElMessage, ElRadio, ElRadioGroup } from 'element-plus'
import { useStateRef, useToggle } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxDialog } from '@gx-web/ep-comp'
import { audit } from '../api'
import { AlarmAuditModel } from '../model'

const emit = defineEmits<{ submitted: [] }>()
const [visible, setVisible] = useToggle(false)
const [loading, setLoading] = useToggle(false)
const [form, , resetForm] = useStateRef(() => getModelFromJson(AlarmAuditModel, { approveStatus: 1 }))
const rules = reactive<FormRules>({
  approveStatus: [{ required: true, message: '请选择审批状态', trigger: 'change' }],
  approveRemark: [{ required: true, message: '请输入审批备注', trigger: 'blur' }]
})
const FormRef = useTemplateRef('FormRef')
</script>
```
```

- [ ] **Step 4: 编写 `form-dialog/examples/model/index.ts` 和 `api/index.ts`**

`examples/model/index.ts` 写入：

```ts
import { FieldName } from '@gx-web/core'

export class AlarmListItemModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  id!: string
}

export class AlarmFormModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  @FieldName('告警详情')
  alarmDetail!: string

  id!: string
}

export class AlarmAuditModel {
  @FieldName('审批状态')
  approveStatus!: number

  @FieldName('审批备注')
  approveRemark!: string

  id!: string
}
```

`examples/api/index.ts` 写入：

```ts
import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmAuditModel, AlarmFormModel } from '../model'

const request = useAxios()

export const add = (data: AlarmFormModel) => {
  return request.post({
    url: `/zl-business/alarm/record`,
    data
  })
}

export const update = (data: AlarmFormModel) => {
  return request.put({
    url: `/zl-business/alarm/record`,
    data
  })
}

export const audit = (data: AlarmAuditModel) => {
  return request.put({
    url: `/zl-business/alarm/record/audit`,
    data
  })
}
```

- [ ] **Step 5: 编写自动模式与原生模式两个组件示例**

`examples/components/alarm-add.vue` 直接复用并修正当前 `crud-page/examples/components/alarm-add.vue` 的结构，确保关键部分如下：

```vue
<GxDialog v-model="visible" :title="dialogTitle" width="500px" @closed="close">
  <GxForm ref="FormRef" v-model="form" :items="formItems" :rules="rules" label-width="120px" v-loading="loading" />
  <template #footer>
    <ElButton :loading="loading" @click="setVisible(false)">取消</ElButton>
    <ElButton type="primary" :loading="loading" @click="handleSubmit">确定</ElButton>
  </template>
</GxDialog>
```

`examples/components/alarm-audit.vue` 写入：

```vue
<script setup lang="ts">
import { reactive, useTemplateRef } from 'vue'
import type { FormRules } from 'element-plus'
import { ElButton, ElForm, ElFormItem, ElInput, ElMessage, ElRadio, ElRadioGroup } from 'element-plus'
import { useStateRef, useToggle } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxDialog } from '@gx-web/ep-comp'
import { audit } from '../api'
import { AlarmAuditModel } from '../model'

const emit = defineEmits<{ submitted: [] }>()
const [visible, setVisible] = useToggle(false)
const [loading, setLoading] = useToggle(false)
const [form, , resetForm] = useStateRef(() => getModelFromJson(AlarmAuditModel, { approveStatus: 1 }))
const FormRef = useTemplateRef('FormRef')

const rules = reactive<FormRules>({
  approveStatus: [{ required: true, message: '请选择审批状态', trigger: 'change' }],
  approveRemark: [{ required: true, message: '请输入审批备注', trigger: 'blur' }]
})

const init = (row: { id: string }) => {
  resetForm()
  form.value.id = row.id
  setVisible(true)
}

const close = () => {
  resetForm()
}

const handleSubmit = async () => {
  try {
    setLoading(true)
    await FormRef.value?.validate()
    const { message } = await audit(form.value)
    ElMessage.success(message)
    setVisible(false)
    emit('submitted')
  }
  finally {
    setLoading(false)
  }
}

defineExpose({ init })
</script>

<template>
  <GxDialog v-model="visible" title="审批" width="520px" @closed="close">
    <ElForm ref="FormRef" v-loading="loading" :model="form" :rules="rules" label-width="120px">
      <ElFormItem label="审批状态" prop="approveStatus">
        <ElRadioGroup v-model="form.approveStatus">
          <ElRadio :value="1">通过</ElRadio>
          <ElRadio :value="2">拒绝</ElRadio>
        </ElRadioGroup>
      </ElFormItem>
      <ElFormItem v-if="form.approveStatus === 2" label="审批备注" prop="approveRemark">
        <ElInput v-model="form.approveRemark" type="textarea" :rows="3" placeholder="请输入审批备注" />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <ElButton :loading="loading" @click="setVisible(false)">取消</ElButton>
      <ElButton type="primary" :loading="loading" @click="handleSubmit">确定</ElButton>
    </template>
  </GxDialog>
</template>
```

- [ ] **Step 6: 编写 `form-dialog/examples/index.vue`，演示对 table-page 的增量接入**

写入：

```vue
<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import { ElButton } from 'element-plus'
import { useStateRef, useTablePage } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxPaginationTable, GxSearch, generateFormItems, generateTableColumns } from '@gx-web/ep-comp'
import { AlarmQueryModel, AlarmListItemModel } from './model'
import { loadPage } from './table-api'
import AlarmAdd from './components/alarm-add.vue'
import AlarmAudit from './components/alarm-audit.vue'

defineOptions({
  name: 'AlarmManage'
})

const AlarmAddRef = useTemplateRef('AlarmAddRef')
const AlarmAuditRef = useTemplateRef('AlarmAuditRef')
const [search, , resetSearch] = useStateRef(() => getModelFromJson(AlarmQueryModel))
const [list, { page, loading, loadList, reloadList, onChange }] = useTablePage<AlarmListItemModel>(
  ({ current, size }) =>
    loadPage({ ...search.value, pageNum: current, pageSize: size }).then(res => ({
      records: res.data.records,
      total: res.data.total
    }))
)

const columns = generateTableColumns(AlarmListItemModel, ['alarmCode', 'alarmTitle'])
const searchItems = generateFormItems(AlarmQueryModel, ['deviceSn'])

const handleAdd = () => {
  AlarmAddRef.value?.init()
}

const handleEdit = (row: AlarmListItemModel) => {
  AlarmAddRef.value?.initEdit(row)
}

const handleAudit = (row: AlarmListItemModel) => {
  AlarmAuditRef.value?.init(row)
}

onMounted(loadList)
</script>

<template>
  <div class="alarm-manage">
    <GxPaginationTable
      v-model:page="page.current"
      v-model:limit="page.size"
      :columns="columns"
      :data="list"
      :loading="loading"
      :total="page.total"
      @pagination="onChange"
    >
      <template #header>
        <GxSearch v-model="search" :items="searchItems" @submit="loadList" @reset="resetSearch();reloadList()" />
      </template>

      <template #action="{ row }">
        <ElButton link type="primary" @click="handleEdit(row)">编辑</ElButton>
        <ElButton link type="warning" @click="handleAudit(row)">审批</ElButton>
      </template>

      <template #action-bar>
        <ElButton type="primary" @click="handleAdd">新增</ElButton>
      </template>
    </GxPaginationTable>

    <AlarmAdd ref="AlarmAddRef" @submitted="reloadList" />
    <AlarmAudit ref="AlarmAuditRef" @submitted="reloadList" />
  </div>
</template>
```

- [ ] **Step 7: 同步修正旧 `crud-page/examples/components/alarm-add.vue` 为直接 `GxDialog + GxForm` 的规范示例**

将以下片段补齐到旧文件中：

```vue
const FormRef = useTemplateRef('FormRef')

<GxDialog v-model="visible" :title="dialogTitle" width="500px" @closed="close">
  <GxForm ref="FormRef" v-model="form" :items="formItems" :rules="rules" label-width="120px" v-loading="loading" />
  <template #footer>
    <ElButton :loading="loading" @click="setVisible(false)">取消</ElButton>
    <ElButton type="primary" :loading="loading" @click="handleSubmit">确定</ElButton>
  </template>
</GxDialog>
```

- [ ] **Step 8: 验证 `form-dialog` 的模式边界和幂等术语存在**

Run:
```bash
rg -n "自动模式|原生模式|先解释复杂点|import 是否已存在|按钮是否已存在|组件实例是否已存在" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/form-dialog"
```

Expected: `SKILL.md` 和 `reference.md` 中都能找到模式切换与幂等检查说明。

- [ ] **Step 9: 提交 `form-dialog` skill**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ep-comp/skills/form-dialog ep-comp/skills/crud-page/examples/components/alarm-add.vue && git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "$(cat <<'EOF'
feat(ep-comp): 新增 form-dialog skill
EOF
)"
```

Expected: 自动模式、原生模式与旧示例修正一起进入一条提交。

---

### Task 4: 落地 `detail-dialog` skill

**Files:**
- Create: `ep-comp/skills/detail-dialog/SKILL.md`
- Create: `ep-comp/skills/detail-dialog/reference.md`
- Create: `ep-comp/skills/detail-dialog/examples/index.vue`
- Create: `ep-comp/skills/detail-dialog/examples/components/detail.vue`
- Create: `ep-comp/skills/detail-dialog/examples/api/index.ts`
- Create: `ep-comp/skills/detail-dialog/examples/model/index.ts`

- [ ] **Step 1: 创建 `detail-dialog` 目录与示例骨架**

Run:
```bash
mkdir -p "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/detail-dialog/examples/components" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/detail-dialog/examples/api" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/detail-dialog/examples/model"
```

Expected: `detail-dialog` 目录结构创建完成。

- [ ] **Step 2: 编写 `detail-dialog/SKILL.md`，明确只读详情职责**

写入：

```md
---
name: detail-dialog
description: Add read-only detail dialogs to an existing ep-comp table page without changing the table-page skeleton.
---

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
```

- [ ] **Step 3: 编写 `detail-dialog/reference.md`，提供 `init(id)` 约定与详情模板**

写入：

```md
## Expose Contract

- detail：`init(id)`

## Detail Component Template

```vue
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElDescriptions, ElDescriptionsItem } from 'element-plus'
import { useToggle } from '@gx-web/tool'
import { GxDialog } from '@gx-web/ep-comp'
import { loadDetail } from '../api'
import type { AlarmDetailModel } from '../model'

const [visible, setVisible] = useToggle(false)
const [loading, setLoading] = useToggle(false)
const detail = ref<AlarmDetailModel>()

const init = async (id: string) => {
  setVisible(true)
  setLoading(true)
  try {
    const { data } = await loadDetail(id)
    detail.value = data
  }
  finally {
    setLoading(false)
  }
}

defineExpose({ init })
</script>
```
```

- [ ] **Step 4: 编写 `detail-dialog/examples/model/index.ts` 和 `api/index.ts`**

`examples/model/index.ts` 写入：

```ts
import { FieldName } from '@gx-web/core'

export class AlarmListItemModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  id!: string
}

export class AlarmDetailModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  @FieldName('告警详情')
  alarmDetail!: string

  @FieldName('告警时间')
  alarmTime!: string

  @FieldName('入库时间')
  createTime!: string

  id!: string
}
```

`examples/api/index.ts` 写入：

```ts
import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmDetailModel } from '../model'

const request = useAxios()

export const loadDetail = (id: string) => {
  return request.get<Res<AlarmDetailModel>>({
    url: `/zl-business/alarm/record/${id}`
  })
}
```

- [ ] **Step 5: 编写 `detail-dialog/examples/components/detail.vue` 与集成页**

`examples/components/detail.vue` 写入：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { ElDescriptions, ElDescriptionsItem } from 'element-plus'
import { useToggle } from '@gx-web/tool'
import { GxDialog } from '@gx-web/ep-comp'
import { loadDetail } from '../api'
import type { AlarmDetailModel } from '../model'

const [visible, setVisible] = useToggle(false)
const [loading, setLoading] = useToggle(false)
const detail = ref<AlarmDetailModel>()

const init = async (id: string) => {
  setVisible(true)
  setLoading(true)
  try {
    const { data } = await loadDetail(id)
    detail.value = data
  }
  finally {
    setLoading(false)
  }
}

defineExpose({ init })
</script>

<template>
  <GxDialog v-model="visible" title="详情" width="720px">
    <div v-loading="loading">
      <ElDescriptions :column="2" border>
        <ElDescriptionsItem label="告警代码">{{ detail?.alarmCode || '--' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="告警标题">{{ detail?.alarmTitle || '--' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="告警详情">{{ detail?.alarmDetail || '--' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="告警时间">{{ detail?.alarmTime || '--' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="入库时间">{{ detail?.createTime || '--' }}</ElDescriptionsItem>
      </ElDescriptions>
    </div>
  </GxDialog>
</template>
```

`examples/index.vue` 写入：

```vue
<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import { ElButton } from 'element-plus'
import { useStateRef, useTablePage } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxPaginationTable, GxSearch, generateFormItems, generateTableColumns } from '@gx-web/ep-comp'
import { AlarmQueryModel, AlarmListItemModel } from './model'
import { loadPage } from './table-api'
import Detail from './components/detail.vue'

const DetailRef = useTemplateRef('DetailRef')
const [search, , resetSearch] = useStateRef(() => getModelFromJson(AlarmQueryModel))
const [list, { page, loading, loadList, reloadList, onChange }] = useTablePage<AlarmListItemModel>(
  ({ current, size }) =>
    loadPage({ ...search.value, pageNum: current, pageSize: size }).then(res => ({
      records: res.data.records,
      total: res.data.total
    }))
)

const columns = generateTableColumns(AlarmListItemModel, ['alarmCode', 'alarmTitle'])
const searchItems = generateFormItems(AlarmQueryModel, ['deviceSn'])

const handleDetail = (row: AlarmListItemModel) => {
  DetailRef.value?.init(row.id)
}

onMounted(loadList)
</script>

<template>
  <div class="alarm-manage">
    <GxPaginationTable
      v-model:page="page.current"
      v-model:limit="page.size"
      :columns="columns"
      :data="list"
      :loading="loading"
      :total="page.total"
      @pagination="onChange"
    >
      <template #header>
        <GxSearch v-model="search" :items="searchItems" @submit="loadList" @reset="resetSearch();reloadList()" />
      </template>

      <template #action="{ row }">
        <ElButton link type="primary" @click="handleDetail(row)">详情</ElButton>
      </template>
    </GxPaginationTable>

    <Detail ref="DetailRef" />
  </div>
</template>
```

- [ ] **Step 6: 验证 `detail-dialog` 没有混入提交型表单责任**

Run:
```bash
rg -n "emit\('submitted'\)|handleSubmit|generateFormItems\(|add\(|update\(|audit\(" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/detail-dialog"
```

Expected: 不应出现 `handleSubmit`、`add`、`update`、`audit`；`generateFormItems` 也不应成为主模板的一部分。

- [ ] **Step 7: 提交 `detail-dialog` skill**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ep-comp/skills/detail-dialog && git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "$(cat <<'EOF'
feat(ep-comp): 新增 detail-dialog skill
EOF
)"
```

Expected: 详情弹窗的示例、reference、skill 文档进入单独提交。

---

### Task 5: 清理旧示例并完成兼容验证

**Files:**
- Modify: `ep-comp/skills/crud-page/examples/index.vue`
- Modify: `ep-comp/skills/crud-page/examples/model/index.ts`
- Modify: `ep-comp/skills/crud-page/examples/api/index.ts`
- Review: `ep-comp/skills/table-page/**`
- Review: `ep-comp/skills/form-dialog/**`
- Review: `ep-comp/skills/detail-dialog/**`

- [ ] **Step 1: 把旧 `crud-page/examples/index.vue` 从 `defineAsyncComponent` 改为直接 `import`**

将以下片段：

```ts
import { defineAsyncComponent, h, onMounted, useTemplateRef } from 'vue'
...
const AlarmAdd = defineAsyncComponent(() => import('./components/alarm-add.vue'))
```

替换为：

```ts
import { h, onMounted, useTemplateRef } from 'vue'
...
import AlarmAdd from './components/alarm-add.vue'
```

- [ ] **Step 2: 让旧 `crud-page/examples/index.vue` 明确成为“拆分后组合使用”的兼容示例**

将操作区与组件挂载保留，并在文件顶部附近补上这段注释：

```ts
// 兼容示例：table-page 生成底座后，再追加 form-dialog 能力
```

同时保证模板仍然是：

```vue
<div class="alarm-manage">
  <GxPaginationTable ...>
    <template #action>...</template>
    <template #action-bar>...</template>
  </GxPaginationTable>
  <AlarmAdd ref="AlarmAddRef" @submitted="reloadList" />
</div>
```

- [ ] **Step 3: 复核旧示例 model/api 是否还能作为共享示例**

要求保留以下代码不变或等价：

```ts
export class AlarmFormModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  @FieldName('告警详情')
  alarmDetail!: string

  id!: string
}
```

```ts
export const add = (data: AlarmFormModel) => {
  return request.post({
    url: `/zl-business/alarm/record`,
    data
  })
}
```

- [ ] **Step 4: 运行全局检索，确认旧主路径术语与新 skill 都已到位**

Run:
```bash
rg -n "name: (crud-page|table-page|form-dialog|detail-dialog)|defineAsyncComponent|兼容入口|自动模式|原生模式|增量注入 contract|init\(id\)" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills"
```

Expected:
- 能查到四个 skill 名称
- 只剩历史说明时才允许出现 `defineAsyncComponent`，正常情况下应为 0 处
- `crud-page` 存在“兼容入口”
- `form-dialog` 存在“自动模式”“原生模式”
- `detail-dialog` 存在 `init(id)`

- [ ] **Step 5: 查看本次全部变更，确认没有误改缓存目录或仓库外文件**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" status --short && git -C "D:/Develop/Project/cj-cc-marketplace" diff --stat
```

Expected:
- 只出现 `D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/**` 和 `docs/superpowers/plans/**`
- 不应出现 `C:/Users/13226/.claude/plugins/cache/...` 之类的缓存目录

- [ ] **Step 6: 提交示例清理与最终兼容验证**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" add ep-comp/skills/crud-page/examples/index.vue ep-comp/skills/crud-page/examples/model/index.ts ep-comp/skills/crud-page/examples/api/index.ts && git -C "D:/Develop/Project/cj-cc-marketplace" commit -m "$(cat <<'EOF'
refactor(ep-comp): 更新 crud-page 兼容示例
EOF
)"
```

Expected: `crud-page` 示例与兼容链路收尾改动形成最后一条提交。

---

### Task 6: 最终验收与交付说明

**Files:**
- Review: `ep-comp/skills/crud-page/**`
- Review: `ep-comp/skills/table-page/**`
- Review: `ep-comp/skills/form-dialog/**`
- Review: `ep-comp/skills/detail-dialog/**`
- Review: `docs/superpowers/plans/2026-05-21-ep-comp-skill-split.md`

- [ ] **Step 1: 检查四个 skill 的职责边界是否互斥**

Run:
```bash
rg -n "不负责|只负责|Routing Rules|Compatibility Notes|自动模式|原生模式|只读详情" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills"
```

Expected: 四个 skill 的职责与非职责边界都能被文本明确检索到。

- [ ] **Step 2: 检查三个新 skill 的示例都符合根节点 contract**

Run:
```bash
rg -n "<template>|<div class=\".*-manage\">|<GxPaginationTable|ref=\".*Ref\"" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/table-page/examples" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/form-dialog/examples" "D:/Develop/Project/cj-cc-marketplace/ep-comp/skills/detail-dialog/examples"
```

Expected: 每个 `examples/index.vue` 都有单根 `<div class="*-manage">`，dialog 示例挂载在根 `div` 内。

- [ ] **Step 3: 复查计划与实现范围一致**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" diff --name-only HEAD~4..HEAD
```

Expected: 最近几次提交只涉及本计划列出的 skill 目录与示例文件。

- [ ] **Step 4: 输出交付说明，明确推荐使用链路**

交付说明应包含以下文案：

```md
推荐调用链：
1. `table-page`
2. `form-dialog`
3. `detail-dialog`

兼容入口：
- `crud-page` 继续保留
- 仅负责识别需求、解释拆分链路、承接旧术语
- 不再作为默认一次性完整 CRUD 生成器
```

- [ ] **Step 5: 提交最终验收说明**

Run:
```bash
git -C "D:/Develop/Project/cj-cc-marketplace" commit --allow-empty -m "$(cat <<'EOF'
chore(ep-comp): 完成 skill 拆分验收
EOF
)"
```

Expected: 用一条空提交标记整个拆分工作验收完成，方便回看里程碑。
