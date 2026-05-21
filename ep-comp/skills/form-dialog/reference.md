# form-dialog Reference

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

## Shared Contracts

### 根节点 contract

```vue
<template>
  <div class="module-kebab-case">
    <GxPaginationTable ... />
    <XxxAdd ref="XxxAddRef" @submitted="reloadList" />
  </div>
</template>
```

### 按钮注入规则

- 行级按钮：只能注入 `#action`
- 页面级按钮：只能注入 `#action-bar`
