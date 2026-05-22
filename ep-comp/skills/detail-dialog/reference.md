# detail-dialog Reference

## Expose Contract

- detail：`init(id)`

## 自动模式组件模板

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useToggle } from '@gx-web/tool'
import { generateDescriptionsItems, GxDescriptions, GxDialog } from '@gx-web/ep-comp'
import { loadDetail } from '../api'
import type { AlarmDetailModel } from '../model'

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
```

## 原生模式组件模板

适用于自定义渲染、条件显隐、复杂布局。切换前需经用户确认。

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
      </ElDescriptions>
    </div>
  </GxDialog>
</template>
```

## Shared Contracts

### 根节点 contract

```vue
<template>
  <div class="module-kebab-case">
    <GxPaginationTable ... />
    <Detail ref="DetailRef" />
  </div>
</template>
```

### 按钮注入规则

- 详情按钮只能注入 `#action`
- 详情组件实例必须放在根 `div` 内部、`GxPaginationTable` 之后
