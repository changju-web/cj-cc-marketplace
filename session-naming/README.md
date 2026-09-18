# session-naming

ZCode 会话自动命名插件：每轮回复结束（Stop hook）检查当前会话标题，未按规范命名的注入一次性提醒，由会话内的 agent 完成改名；改完后标题标记 `title_source=custom`，内置自动标题不再覆盖，hook 从此静默。

## 命名规范（唯一权威源）

- 日期取会话创建时间 `createdAt`，按 `Asia/Shanghai` 转换；不使用 `updatedAt`。
- 格式统一为：`MMDD｜类型｜主题`（全角分隔符）。
- 类型限定为：功能、设计、修复、优化、发布、探索、文档、研究；不适用时就近归类（如重构归优化），不扩枚举。
- 主题：根据对话实际内容提炼，不超过 12 字，不重复项目名称，不带句末标点。
- 无法判断主题时不要猜：标题保持原名，仅将 `title_source` 置为 `custom`（对应"保留原名"）。
- 只修改对话标题，不修改项目名称、对话内容、项目归属、排序、置顶或归档状态。
- MMDD 不带年份，接受跨年歧义；同日同名允许重复，不追加序号。

示例：

- `0903｜优化｜批次文字显示`
- `0902｜功能｜整合快捷键提示页`
- `0813｜发布｜提交代码到GitHub`
- `0901｜设计｜界面对齐检查`

## 工作原理

- `hooks/hooks.json`：注册 Stop hook，`process` 类型走 argv 不经 shell（Windows 安全），超时 5 秒。
- `hooks/session_naming.py`：只读查询 `~/.zcode/cli/db/db.sqlite`，守卫（无会话 id / 子会话 / 已 custom 则静默退出）后输出 `{"additionalContext": 提醒}`；MMDD 已由脚本算好，agent 只需判断类型与主题。
- `hooks/rename.py`：改名执行器，仅 `UPDATE` title / title_source / time_title_updated 三个字段；`--keep` 对应"保留原名"。
- 成本：每个会话终生一次性约 300–500 token（一条提醒 + 一次改名调用），改完后为零——守卫是本地读库，不产生模型调用。

## 安装

从 cj-cc-marketplace 安装本插件即可。插件 hook 会自动启用 hook 运行器，无需在配置中设置 `hooks.enabled`。

## 存量会话回填

1. 关闭 ZCode CLI（避免写锁）。
2. 备份 `~/.zcode/cli/db/db.sqlite`（连同 `-wal` / `-shm`）。
3. 先预览，再执行：

```text
python scripts/backfill.py
python scripts/backfill.py --apply
```

类型由现有标题关键词就近推断；推断不了的保留原名（仅置 custom），不会瞎猜。

## 排障

- hook 是否触发、超时还是失败：看 ZCode 日志里的 hook 运行记录（来源、matcher、结果、耗时）。
- 设置环境变量 `ZCODE_SESSION_NAMING_DEBUG=1` 后，`hooks/debug.log` 会记录每次守卫判断。
