# -*- coding: utf-8 -*-
"""来源 id 事前校验（第69轮新增，用于避免"凭记忆引用来源"）。

用法：
    python tools/precheck_src.py sep-kant iep-hume ...
退出码 0 = 全部存在；1 = 有未知 id（会列出）。
也可被临时脚本 import：
    from precheck_src import require
    require(["sep-kant", ...])
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "sources.json")


def load_ids():
    with open(SRC, encoding="utf-8") as f:
        d = json.load(f)
    return {s["id"] for s in d["sources"]}


def require(ids):
    """ids 中若有未知来源 id，抛出 AssertionError 并列出。"""
    known = load_ids()
    bad = sorted({i for i in ids if i not in known})
    if bad:
        raise AssertionError("未知来源 id（必须先查 sources.json）：%s" % ", ".join(bad))
    return True


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a]
    if not args:
        print("用法: python tools/precheck_src.py <source-id> [...]")
        sys.exit(0)
    try:
        require(args)
    except AssertionError as e:
        print("FORMAT-ERROR:", e)
        sys.exit(1)
    n = len(load_ids())
    print("OK  全部存在（库内共 %d 条来源）" % n)
