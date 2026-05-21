<script setup lang="ts">
import { reactive, useTemplateRef } from 'vue'
import type { FormRules } from 'element-plus'
import { ElButton, ElForm, ElFormItem, ElInput, ElMessage, ElRadio, ElRadioGroup } from 'element-plus'
import { useStateRef, useToggle } from '@gx-web/tool'
import { getModelFromJson } from '@gx-web/core'
import { GxDialog } from '@gx-web/ep-comp'
import { audit } from '../api'
import { AlarmAuditModel } from '../model'

defineOptions({
  name: 'AlarmAudit'
})

const emit = defineEmits<{
  submitted: []
}>()

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
          <ElRadio :value="1">
            通过
          </ElRadio>
          <ElRadio :value="2">
            拒绝
          </ElRadio>
        </ElRadioGroup>
      </ElFormItem>
      <ElFormItem v-if="form.approveStatus === 2" label="审批备注" prop="approveRemark">
        <ElInput v-model="form.approveRemark" type="textarea" :rows="3" placeholder="请输入审批备注" />
      </ElFormItem>
    </ElForm>
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
