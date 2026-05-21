# detail-dialog Reference

## Expose Contract

- detail：`init(id)`

## Detail Component Template

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
