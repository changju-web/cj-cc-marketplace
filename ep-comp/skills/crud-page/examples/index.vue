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
