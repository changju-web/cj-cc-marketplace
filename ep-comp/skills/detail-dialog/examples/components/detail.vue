<script setup lang="ts">
import { ref } from 'vue'
import { useToggle } from '@gx-web/tool'
import { generateDescriptionsItems, GxDescriptions, GxDialog } from '@gx-web/ep-comp'
import { loadDetail } from '../api'
import type { AlarmDetailModel } from '../model'

defineOptions({
  name: 'AlarmDetail'
})

const [visible, setVisible] = useToggle(false)
const [loading, setLoading] = useToggle(false)
const detail = ref<AlarmDetailModel>()

const items = generateDescriptionsItems(AlarmDetailModel, [
  'alarmCode',
  'alarmTitle',
  'alarmDetail',
  'alarmTime',
  'createTime'
])

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
    <GxDescriptions v-model="detail" :items="items" :column="2" border :loading="loading" />
  </GxDialog>
</template>
