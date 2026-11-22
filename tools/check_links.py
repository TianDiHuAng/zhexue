#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""站内链接完整性核验：解析 site/ 下所有 HTML 的 href/src，检查目标文件是否存在。
能抓出目录层级（depth）错配这类肉眼难发现的断链（旧项目线上 404 的根因）。"""
import glob
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
ATTR = re.compile(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"')


def main():
    pages = glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)
    bad = []
    total = 0
    for p in pages:
        with open(p, encoding="utf-8") as f:
            text = f.read()
        relp = os.path.relpath(p, SITE).replace("\\", "/")
        base = os.path.dirname(p)
        for m in ATTR.finditer(text):
            raw = m.group(1).strip()
            if not raw or raw.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
                continue
            target = raw.split("?")[0]
            if not target:
                continue
            total += 1
            if target.startswith("/"):
                fp = os.path.join(SITE, target.lstrip("/"))
            else:
                fp = os.path.normpath(os.path.join(base, urllib.parse.unquote(target)))
            if os.path.isdir(fp):
                fp = os.path.join(fp, "index.html")
            if not os.path.exists(fp):
                bad.append((relp, raw))
    for relp, raw in bad[:60]:
        print("断链  %s  →  %s" % (relp, raw))
    print("\n页面 %d；内部链接 %d；断链 %d" % (len(pages), total, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
