<script setup lang="ts">
import { ref } from 'vue'
import { ElDescriptions, ElDescriptionsItem } from 'element-plus'
import { useToggle } from '@gx-web/tool'
import { GxDialog } from '@gx-web/ep-comp'
import { loadDetail } from '../api'
import type { AlarmDetailModel } from '../model'

defineOptions({
  name: 'AlarmDetail'
})

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
