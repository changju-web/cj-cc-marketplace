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
