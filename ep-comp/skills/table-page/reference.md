# table-page Reference

## index.vue template

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { ElButton } from 'element-plus'
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

## API template

```ts
import useAxios from '@base-lib/hooks/core/useAxios'
import type { XxxListItemModel, XxxQueryModel } from '../model'

const request = useAxios()

export const loadPage = (params: XxxQueryModel) => {
  return request.get<ResPage<XxxListItemModel>>({
    url: '/xxx/page',
    params
  })
}
```

## Model template

```ts
import { FieldName } from '@gx-web/core'

export class XxxQueryModel {
  @FieldName('关键字')
  keyword!: string
}

export class XxxListItemModel {
  @FieldName('字段1')
  field1!: string

  @FieldName('字段2')
  field2!: string

  id!: string
}
```

## Shared Contracts

### 根节点 contract

```vue
<template>
  <div class="module-kebab-case">
    <GxPaginationTable ... />
  </div>
</template>
```

### 挂点 contract

- `#header`：查询区
- `#action`：行级操作
- `#action-bar`：页面级操作
