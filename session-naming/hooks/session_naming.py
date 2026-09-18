"""ZCode Stop hook：按「MMDD｜类型｜主题」规范检查当前会话命名。

守卫（全部满足才注入提醒，否则静默退出）：
- argv[1] 能取到会话 id（hooks.json 传入 ${CLAUDE_SESSION_ID}）
- 会话存在于 db.sqlite 且 task_type != 'subagent_child'
- title_source != 'custom'（custom 后内置自动标题不再覆盖，此处永不再打扰）

输出仅含一个键：{"additionalContext": "<提醒>"}，符合 hook 严格 JSON 校验。
本脚本对数据库只读；任何异常都静默退出 0，绝不阻塞会话。
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

DB_PATH = os.path.join(os.path.expanduser("~"), ".zcode", "cli", "db", "db.sqlite")


def shanghai_tz():
    # Asia/Shanghai 自 1991 年起无夏令时，固定 UTC+8 与 IANA 时区等价；
    # Windows 上 Python 常缺 tzdata 包，ZoneInfo 不可用时回退固定偏移
    try:
        return ZoneInfo("Asia/Shanghai")
    except Exception:
        return timezone(timedelta(hours=8))

REMINDER = """【会话命名】本会话尚未按「MMDD｜类型｜主题」规范命名，请在本次回复结束前用 Bash 执行命名命令后自然收尾。

正常命名：
python "{rename_py}" {session_id} "{mmdd}｜<类型>｜<主题>"

无法判断主题时不要猜，保持现名仅关掉自动命名：
python "{rename_py}" {session_id} --keep

命名规则：
1. MMDD 已按会话创建时间（Asia/Shanghai）算好：{mmdd}
2. 类型八选一：功能/设计/修复/优化/发布/探索/文档/研究；不适用时就近归类（如重构归优化）
3. 主题：从本会话内容提炼，不超过 12 字，不重复项目名，不带句末标点
4. 示例：0903｜优化｜批次文字显示；0813｜发布｜提交代码到GitHub；0901｜设计｜界面对齐检查
5. rename.py 只更新标题（title/title_source/time_title_updated），执行成功后无需向用户解释"""


def debug(msg: str) -> None:
    if os.environ.get("ZCODE_SESSION_NAMING_DEBUG") != "1":
        return
    try:
        log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.log")
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} {msg}\n")
    except OSError:
        pass


def main() -> None:
    session_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not session_id:
        debug("no session id in argv")
        return
    db_uri = f"file:{DB_PATH.replace(os.sep, '/')}?mode=ro"
    con = sqlite3.connect(db_uri, uri=True, timeout=3)
    try:
        row = con.execute(
            "SELECT title_source, time_created, task_type FROM session WHERE id = ?",
            (session_id,),
        ).fetchone()
    finally:
        con.close()
    if row is None:
        debug(f"session not found: {session_id}")
        return
    title_source, time_created, task_type = row
    if task_type == "subagent_child" or title_source == "custom":
        return
    mmdd = datetime.fromtimestamp(time_created / 1000, shanghai_tz()).strftime("%m%d")
    rename_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rename.py")
    reminder = REMINDER.format(rename_py=rename_py, session_id=session_id, mmdd=mmdd)
    # ensure_ascii：输出纯 ASCII，规避 Windows 控制台/运行器的编码差异，JSON 解析后还原为中文
    print(json.dumps({"additionalContext": reminder}, ensure_ascii=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # hook 失败绝不能影响会话
        debug(f"error: {exc!r}")
    sys.exit(0)
