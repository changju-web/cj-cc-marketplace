# 测试用例 3：站内消息通知模块（无 skill）

## 用户输入

> 我想给系统加个站内消息通知模块，用户登录后能看到未读消息，点击消息可以跳转到对应业务页面。先帮我想想怎么做比较好。

---

## 方案建议

消息通知模块可以从这几个维度来设计：

### 1. 消息获取方式

| 方式 | 优点 | 缺点 |
|------|------|------|
| WebSocket | 实时推送 | 需要后端支持，复杂度高 |
| SSE | 服务端单向推送 | 兼容性一般 |
| 短轮询 | 实现简单 | 有延迟 |

建议先用**短轮询**（15-30 秒间隔），简单可靠，后续需要实时性再升级 WebSocket。

### 2. 整体架构

```text
顶部导航栏
  └── 铃铛图标（带未读数 badge）
       └── 下拉面板（最近消息列表）
            └── "查看全部" → 消息中心页面

消息中心页面（/messages）
  ├── 全部消息列表（分页）
  ├── 未读/已读状态
  └── 点击跳转到业务页面
```

### 3. 核心实现

**消息 Store（Pinia）**

```typescript
// src/store/message.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMessageStore = defineStore('message', () => {
  const unreadCount = ref(0)
  const messages = ref<Message[]>([])

  const fetchUnreadCount = async () => {
    const res = await fetch('/api/messages/unread-count')
    unreadCount.value = res.data.count
  }

  const fetchMessages = async (page: number) => {
    const res = await fetch(`/api/messages?page=${page}&size=20`)
    messages.value = res.data.list
  }

  const markAsRead = async (id: number) => {
    await fetch(`/api/messages/${id}/read`, { method: 'PATCH' })
    unreadCount.value--
  }

  return { unreadCount, messages, fetchUnreadCount, fetchMessages, markAsRead }
})
```

**铃铛组件**

```vue
<!-- src/components/MessageBell.vue -->
<template>
  <el-popover placement="bottom" :width="360" trigger="click">
    <template #reference>
      <el-badge :value="messageStore.unreadCount" :hidden="messageStore.unreadCount === 0">
        <el-icon><Bell /></el-icon>
      </el-badge>
    </template>

    <div class="message-list">
      <div v-for="msg in recentMessages" :key="msg.id" class="message-item" @click="handleClick(msg)">
        <span :class="{ unread: !msg.read }">{{ msg.title }}</span>
      </div>
      <router-link to="/messages">查看全部</router-link>
    </div>
  </el-popover>
</template>
```

### 4. API 接口

```
GET  /api/messages/unread-count    — 获取未读数量
GET  /api/messages?page=&size=     — 获取消息列表
PATCH /api/messages/:id/read       — 标记已读
PATCH /api/messages/read-all       — 全部已读
```

### 5. 轮询机制

```typescript
// 页面可见时轮询，隐藏时暂停
setInterval(() => {
  if (document.visibilityState === 'visible') {
    messageStore.fetchUnreadCount()
  }
}, 15000)
```

### 6. 消息跳转

消息体中携带业务类型和 ID，点击时根据类型路由到对应页面：

```typescript
const handleClick = (msg: Message) => {
  messageStore.markAsRead(msg.id)
  if (msg.type === 'approval') {
    router.push(`/approval/${msg.businessId}`)
  } else if (msg.type === 'ticket') {
    router.push(`/tickets/${msg.businessId}`)
  }
}
```

需要我继续细化某个部分吗？比如消息中心页面的完整实现，或者后端接口的详细设计。
