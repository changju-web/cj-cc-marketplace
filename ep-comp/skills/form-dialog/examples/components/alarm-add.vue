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
const dialogTitle = computed(() => `${isEdit.value ? '编辑' : '新增'}告警`)

const rules = reactive<FormRules>({
  alarmCode: [{ required: true, message: '请输入告警代码', trigger: 'blur' }],
  alarmTitle: [{ required: true, message: '请输入告警标题', trigger: 'blur' }]
})

const formItems = generateFormItems(AlarmFormModel, ['alarmCode', 'alarmTitle', 'alarmDetail'])
const FormRef = useTemplateRef('FormRef')

const init = () => {
  setVisible(true)
}

const initEdit = (row: AlarmListItemModel) => {
  resetForm()
  form.value = { ...form.value, ...row }
  setVisible(true)
}

const close = () => {
  resetForm()
}

const handleSubmit = async () => {
  try {
    setLoading(true)
    await FormRef.value?.validate()
    const { message } = await (isEdit.value ? update(form.value) : add(form.value))
    ElMessage.success(message)
    setVisible(false)
    emit('submitted')
  }
  finally {
    setLoading(false)
  }
}

defineExpose({ init, initEdit })
</script>

<template>
  <GxDialog v-model="visible" :title="dialogTitle" width="500px" @closed="close">
    <GxForm ref="FormRef" v-model="form" :items="formItems" :rules="rules" label-width="120px" v-loading="loading" />
    <template #footer>
      <ElButton :loading="loading" @click="setVisible(false)">
        取消
      </ElButton>
      <ElButton type="primary" :loading="loading" @click="handleSubmit">
        确定
      </ElButton>
    </template>
  </GxDialog>
</template>
