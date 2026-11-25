# -*- coding: utf-8 -*-
"""tools/gapscan.py —— 年代空档扫描（借鉴 “History of Philosophy without any gaps” 的“不留空白”理想）。

输出 GAP_SCAN.md：
  1) 各区域按世纪分桶的人物数、概念数、著作数
  2) 该区域内“有前后两端而中间空着”的世纪（空档）
  3) 每世纪的代表人物（最多 4 位）

用法：
  python tools/gapscan.py            # 写 GAP_SCAN.md
  python tools/gapscan.py --list 20  # 只打印空档前 20 行
"""
import json
import glob
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "GAP_SCAN.md")
REGIONS = [("china", "中国"), ("west", "西方"), ("india", "印度")]


def century(y):
    """负年份按“公元前第 n 世纪”处理，统一返回可排序的世纪序号（无 0 世纪）。"""
    if y >= 0:
        return y // 100 + 1            # 0..21 → 公元第 n 世纪（0 年并入 1 世纪）
    return -((abs(y) - 1) // 100 + 1)  # -1..-60 → 公元前第 n 世纪


def century_label(c):
    if c > 0:
        return "公元%d世纪" % c
    return "公元前%d世纪" % (-c)


def load():
    people, concepts, works = [], [], []
    for f in sorted(glob.glob(os.path.join(DATA, "*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        region = d.get("region")
        unit = d.get("title")
        for p in d.get("philosophers", []):
            people.append(dict(id=p["id"], name=p["name"], region=region, unit=unit,
                               y=p.get("birth_year"), d=p.get("death_year")))
        for c in d.get("concepts", []):
            concepts.append(dict(id=c["id"], term=c["term"], region=region))
        for b in d.get("debates", []):
            pass
    wj = json.load(open(os.path.join(DATA, "works.json"), encoding="utf-8"))
    for w in wj.get("works", []):
        works.append(dict(id=w["id"], title=w["title"], tradition=w.get("tradition"),
                          y=w.get("sort_year")))
    return people, concepts, works


def scan():
    people, concepts, works = load()
    lines = ["# GAP_SCAN.md —— 年代空档扫描（工具生成，勿手改）", "",
             "借鉴 “History of Philosophy without any gaps” 的**不留空白**理想："
             "把各区域按世纪分桶，找出**两端有人、中间空着**的世纪。",
             "",
             "统计口径：人物按其**出生年**归入世纪；著作按 `sort_year`；概念不系年，只按区域汇总。"
             "负年份按“公元前第 n 世纪”处理。", ""]
    summary = []
    for region, label in REGIONS:
        ps = [p for p in people if p["region"] == region and isinstance(p["y"], int)]
        cs = [c for c in concepts if c["region"] == region]
        ws = [w for w in works if w["tradition"] == region and isinstance(w["y"], int)]
        if not ps:
            continue
        buckets = defaultdict(list)
        for p in ps:
            buckets[century(p["y"])].append(p)
        lo, hi = min(buckets), max(buckets)
        span = [c for c in range(lo, hi + 1) if c != 0]   # 0 世纪不存在
        gaps = [c for c in span if c not in buckets]
        lines.append("## %s（%d 人 / %d 概念 / %d 部有年份的著作）" % (label, len(ps), len(cs), len(ws)))
        lines.append("")
        lines.append("| 世纪 | 人数 | 代表人物 |")
        lines.append("|---|---|---|")
        for c in span:
            names = " · ".join(p["name"] for p in sorted(buckets.get(c, []), key=lambda x: x["y"])[:4])
            mark = "**（空档）**" if c not in buckets else ""
            lines.append("| %s%s | %d | %s |" % (century_label(c), mark, len(buckets.get(c, [])), names or "—"))
        lines.append("")
        if gaps:
            lines.append("**空档：%s**" % "、".join(century_label(c) for c in gaps))
        else:
            lines.append("**无空档。**")
        lines.append("")
        summary.append((label, len(ps), len(cs), len(ws), len(gaps)))
    lines.append("## 汇总")
    lines.append("")
    lines.append("| 区域 | 人物 | 概念 | 有年份著作 | 空档世纪数 |")
    lines.append("|---|---|---|---|---|")
    for label, np_, nc, nw, ng in summary:
        lines.append("| %s | %d | %d | %d | %d |" % (label, np_, nc, nw, ng))
    lines.append("")
    lines.append("> 说明：空档不等于缺漏——某世纪若本来无重要人物，空着是**如实**。"
                 "此表只供选题参考，**不得为填空档而建无来源的页面**。")
    return "\n".join(lines) + "\n"


def main():
    text = scan()
    if "--list" in sys.argv:
        n = 20
        for i, a in enumerate(sys.argv):
            if a == "--list" and i + 1 < len(sys.argv):
                try:
                    n = int(sys.argv[i + 1])
                except ValueError:
                    pass
        for line in text.splitlines()[:n]:
            print(line)
        return
    open(OUT, "w", encoding="utf-8", newline="\n").write(text)
    print("GAP_SCAN.md 已写（%d 行）" % len(text.splitlines()))


if __name__ == "__main__":
    main()
