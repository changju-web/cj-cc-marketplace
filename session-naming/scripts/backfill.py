"""存量会话一次性回填「MMDD｜类型｜主题」。

只处理 title_source != 'custom' 的主会话；类型靠现有标题关键词就近推断，
推断不了就保留原名（符合规范 fallback）；已是规范格式的仅补置 custom 让 hook 静默。
默认 dry-run 只预览，--apply 才写库。

用法：
  python scripts/backfill.py             # 预览，不写库
  python scripts/backfill.py --apply     # 写库（请先关闭 ZCode CLI 并备份 db.sqlite）
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

DB_PATH = os.path.join(os.path.expanduser("~"), ".zcode", "cli", "db", "db.sqlite")
NAMED_RE = re.compile(r"^\d{4}｜")


def shanghai_tz():
    # Asia/Shanghai 自 1991 年起无夏令时，固定 UTC+8 与 IANA 时区等价；
    # Windows 上 Python 常缺 tzdata 包，ZoneInfo 不可用时回退固定偏移
    try:
        return ZoneInfo("Asia/Shanghai")
    except Exception:
        return timezone(timedelta(hours=8))

# 关键词按优先级排列，先命中先归类；就近归类，不扩枚举
RULES = [
    ("修复", ("修复", "fix", "bug", "报错", "崩溃", "异常", "白屏")),
    ("发布", ("发布", "提交", "推送", "push", "部署", "上线", "release", "github")),
    ("文档", ("文档", "readme", "说明", "wiki", "注释")),
    ("研究", ("研究", "调研", "对比", "评估", "选型", "调查")),
    ("优化", ("优化", "重构", "性能", "提升", "改进", "精简", "迁移", "调整")),
    ("功能", ("功能", "新增", "添加", "支持", "整合", "实现", "接入", "开发", "生成", "制作", "增加")),
    ("设计", ("设计", "方案", "讨论", "规范", "架构", "流程", "检查", "对齐", "拆分")),
    ("探索", ("探索", "尝试", "了解", "学习", "入门", "demo")),
]


def classify(title: str) -> str | None:
    low = title.lower()
    for category, keywords in RULES:
        if any(keyword in low for keyword in keywords):
            return category
    return None


def main() -> int:
    apply = "--apply" in sys.argv
    con = sqlite3.connect(DB_PATH, timeout=5)
    rows = con.execute(
        "SELECT id, title, time_created FROM session "
        "WHERE title_source != 'custom' AND task_type != 'subagent_child' "
        "ORDER BY time_created"
    ).fetchall()
    renamed = kept = marked = 0
    for sid, title, time_created in rows:
        now_ms = int(time.time() * 1000)
        if NAMED_RE.match(title):
            marked += 1
            print(f"[仅置custom] {title}")
            if apply:
                con.execute(
                    "UPDATE session SET title_source = 'custom', time_title_updated = ? WHERE id = ?",
                    (now_ms, sid),
                )
            continue
        category = classify(title)
        if category is None:
            kept += 1
            print(f"[保留原名] {title}")
            if apply:
                con.execute(
                    "UPDATE session SET title_source = 'custom', time_title_updated = ? WHERE id = ?",
                    (now_ms, sid),
                )
            continue
        mmdd = datetime.fromtimestamp(time_created / 1000, shanghai_tz()).strftime("%m%d")
        new_title = f"{mmdd}｜{category}｜{title}"
        renamed += 1
        print(f"[改名] {title}  ->  {new_title}")
        if apply:
            con.execute(
                "UPDATE session SET title = ?, title_source = 'custom', time_title_updated = ? WHERE id = ?",
                (new_title, now_ms, sid),
            )
    if apply:
        con.commit()
    con.close()
    total = len(rows)
    print(f"\n共 {total} 个待处理会话：改名 {renamed}，保留原名 {kept}，已是规范格式 {marked}")
    if not apply:
        print("dry-run 预览结束，未写库。加 --apply 执行（请先关闭 ZCode CLI 并备份 db.sqlite）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
