# cj-cc-marketplace

长聚科技 Claude Code 插件市场，面向团队业务场景的 skill 集合。

## 插件列表

| 插件 | 说明 |
|------|------|
| ep-comp | 基于 @gx-web/ep-comp 的业务代码生成插件 |

## 安装

### 1. 添加 Marketplace

```bash
/plugin marketplace add changju-web/cj-cc-marketplace
```

### 2. 安装插件

```bash
/plugin install ep-comp@cj-cc-marketplace
```

## 更新

插件更新后，重新安装即可获取最新版本：

```bash
/plugin install ep-comp@cj-cc-marketplace
```

## 包含的 Skill

### crud-page

从 Swagger / Knife4j / OpenAPI JSON 或请求响应示例生成基于 `@gx-web/ep-comp` 的 CRUD 页面脚手架，自动生成 `generateTableColumns`、`generateFormItems`、`useTablePage`、`GXForm`、`GXPaginationTable` 等代码。
