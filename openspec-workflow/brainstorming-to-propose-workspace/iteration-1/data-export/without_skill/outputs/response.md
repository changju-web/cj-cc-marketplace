# 测试用例 2：数据导出功能（无 skill）

## 用户输入

> 帮我加个数据导出功能，要支持导出 Excel 和 PDF。表格用的是 ep-comp 的分页列表组件，数据量大概几万条。后端已经有 /api/export 接口了，只需要前端对接。项目里已经有 openspec 了。

---

## 方案

后端已经有 `/api/export` 接口，前端主要工作是：

1. 在列表工具栏加导出按钮
2. 调用后端接口获取文件流
3. 触发浏览器下载

### 封装通用导出 hook

```typescript
// src/hooks/useExport.ts
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export function useExport(baseUrl: string) {
  const exporting = ref(false)

  const doExport = async (format: 'excel' | 'pdf', params?: Record<string, any>) => {
    if (exporting.value) return

    exporting.value = true
    try {
      const response = await fetch(baseUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format, ...params })
      })

      if (!response.ok) throw new Error('导出失败')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `数据导出.${format === 'excel' ? 'xlsx' : 'pdf'}`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      ElMessage.error('导出失败，请稍后重试')
    } finally {
      exporting.value = false
    }
  }

  return { exporting, doExport }
}
```

### 在列表页面中使用

```vue
<template>
  <div>
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button :loading="exporting" @click="handleExport('excel')">
        导出 Excel
      </el-button>
      <el-button :loading="exporting" @click="handleExport('pdf')">
        导出 PDF
      </el-button>
    </div>

    <!-- 列表 -->
    <ep-comp-table ... />
  </div>
</template>

<script setup lang="ts">
import { useExport } from '@/hooks/useExport'

const { exporting, doExport } = useExport('/api/export')

const handleExport = (format: 'excel' | 'pdf') => {
  doExport(format, { /* 当前筛选参数 */ })
}
</script>
```

### 注意事项

- 几万条数据建议后端做流式返回或分批导出
- 大文件下载可能需要加超时配置
- 文件名建议加上时间戳避免重复

需要我继续完善代码细节吗？
