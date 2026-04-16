# 测试用例 1：用户管理页面（有 skill）

## 用户输入

> 我需要做一个用户管理页面，可以查看用户列表、搜索用户、禁用/启用用户账号。项目已经用了 Vue 3 + Element Plus + TypeScript，后端接口用的是 RESTful 风格。你帮我理一下需求然后开始做吧。

---

## 阶段 1：brainstorming 需求探索

### 澄清问题

在开始之前，我需要确认几个关键点：

**1. 搜索维度的范围**

你提到"搜索用户"，具体需要支持哪些搜索条件？

- A. 仅用户名/手机号模糊搜索
- B. 用户名 + 手机号 + 状态（启用/禁用）组合筛选
- C. 还需要按角色、注册时间等更多维度筛选

**2. 禁用/启用操作的交互**

- A. 列表行内直接切换（switch 开关）
- B. 选中后批量操作
- C. 两种都要支持

**3. 是否需要其他用户管理能力**

- 是否需要新增用户？
- 是否需要编辑用户信息？
- 是否需要分配角色？
- 是否需要查看用户操作日志？

**4. 数据权限**

- 所有管理员都能看到全部用户？
- 还是需要按部门/角色做数据隔离？

---

### 假设用户回复：B、A+C、仅查看+禁用启用、全部可见

### 方案收敛

基于你的需求，推荐方案如下：

**技术方案：** 使用 ep-comp 分页列表组件 + Element Plus 表单组件

- 搜索区：`ElForm` + 多个 `ElInput` / `ElSelect` 组合筛选
- 列表区：`ep-comp` 分页列表，列包含用户名、手机号、状态、注册时间、操作
- 操作区：行内 switch 切换状态 + 选中行批量禁用/启用
- 后端对接：RESTful 接口，`GET /api/users`（列表）、`PATCH /api/users/:id/status`（状态切换）

**不做的事：**
- 不做新增/编辑用户
- 不做角色分配
- 不做操作日志查看
- 不做数据权限隔离

---

### 硬确认门

> 需求探索阶段完成，以下是结论摘要：
>
> - **目标**：为系统新增用户管理页面，支持查看、搜索、禁用/启用用户账号
> - **范围**：做 — 列表展示、组合搜索（用户名/手机号/状态）、单条状态切换、批量状态切换；不做 — 新增/编辑/角色分配/日志/数据隔离
> - **推荐方案**：ep-comp 分页列表 + ElForm 搜索区 + RESTful 接口对接
> - **核心约束**：Vue 3 + Element Plus + TypeScript 技术栈，后端已有 RESTful 接口
>
> 确认后将进入 `/opsx:propose` 创建正式提案。是否继续？

---

### 阶段 2：结构化摘要（假设用户已确认）

**change-name：** `user-management-page`

**proposal 内容：**
- Why：系统需要集中管理用户账号状态，目前缺少可视化的管理界面
- What：新增用户管理页面，包含用户列表、组合搜索、单条/批量禁用启用
- Scope：仅前端页面开发，后端接口已就绪
- Impact：管理员可直观管理用户状态，减少手动操作数据库的风险

**spec 内容：**
- 用户列表默认按注册时间倒序展示，支持分页
- 搜索条件：用户名（模糊）、手机号（模糊）、状态（精确）
- 搜索结果实时刷新列表
- 每行操作列包含状态 switch，切换需二次确认
- 选中多行后顶部出现批量操作栏
- 禁用用户后该行状态标签变红，启用后变绿
- 网络异常时 switch 回滚并提示错误
- 空数据时展示空状态插图

**design 内容：**
- 技术选型：Vue 3 Composition API + Element Plus + TypeScript
- 目录结构：`src/views/user-management/index.vue`
- 组件拆分：SearchForm（搜索区）、UserTable（列表区，基于 ep-comp）
- 接口设计：
  - `GET /api/users?page=1&size=20&username=&phone=&status=` — 用户列表
  - `PATCH /api/users/:id/status` — 单条状态切换 `{ status: 'disabled' | 'enabled' }`
  - `PATCH /api/users/batch-status` — 批量状态切换 `{ ids: number[], status: string }`

**tasks 雏形：**
1. 创建 user-management 目录和页面入口
2. 实现 SearchForm 组件（组合搜索）
3. 实现 UserTable 列表组件（基于 ep-comp）
4. 对接用户列表接口
5. 实现单条状态切换（switch + 确认弹窗）
6. 实现批量状态切换（选中行 + 批量操作栏）
7. 异常处理与空状态
8. 联调测试

---

### 阶段 3：准备进入 /opsx:propose

（此处将上述摘要作为上下文传入 `/opsx:propose`，由 propose 生成 proposal.md、spec.md、design.md、tasks.md 四件套）

本 skill 不直接写 OpenSpec 文件，到此为止。
