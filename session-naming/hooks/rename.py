"""会话标题改名执行器：只更新 title / title_source / time_title_updated 三个字段。

用法：
  python rename.py <session_id> "<MMDD>｜<类型>｜<主题>"
  python rename.py <session_id> --keep    # 标题保持不变，仅置 custom，对应规范"无法判断就保留原名"
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
import time

DB_PATH = os.path.join(os.path.expanduser("~"), ".zcode", "cli", "db", "db.sqlite")
TITLE_RE = re.compile(r"^\d{4}｜[^｜]+｜[^｜]+$")


def main() -> int:
    if len(sys.argv) < 3:
        print('用法: python rename.py <session_id> "<MMDD>｜<类型>｜<主题>" | --keep', file=sys.stderr)
        return 0
    session_id, title = sys.argv[1], sys.argv[2]
    if title != "--keep" and not TITLE_RE.match(title):
        print(f"标题不符合「MMDD｜类型｜主题」格式，未写入: {title}", file=sys.stderr)
        return 0
    con = sqlite3.connect(DB_PATH, timeout=5)
    try:
        with con:
            if title == "--keep":
                cur = con.execute(
                    "UPDATE session SET title_source = 'custom', time_title_updated = ? "
                    "WHERE id = ? AND title_source != 'custom'",
                    (int(time.time() * 1000), session_id),
                )
            else:
                cur = con.execute(
                    "UPDATE session SET title = ?, title_source = 'custom', time_title_updated = ? "
                    "WHERE id = ?",
                    (title, int(time.time() * 1000), session_id),
                )
        print(f"done ({cur.rowcount} row)")
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
