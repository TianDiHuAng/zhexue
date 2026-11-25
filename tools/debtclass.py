# -*- coding: utf-8 -*-
"""tools/debtclass.py —— 把欠账按"为何待核"分类，判断哪些能核、哪些核不了。

用途：`待核实` 880 条不是一个整体。多数卡在「没有原典／没有专门研究」，少数卡在
「版本／篇次／生卒推定」。分类之后，每轮只挑**能核的那一小类**去核，其余如实留着。

输出：DEBT_CLASSES.md
用法：python tools/debtclass.py [--list N]
"""
import json
import glob
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "DEBT_CLASSES.md")

# 分类规则：按关键词命中，顺序即优先（先判"根本没有底本"的硬阻塞）
RULES = [
    ("A 无底本（原书已佚／仅存辑本）", ("已佚", "散佚", "辑佚", "辑本", "仅存")),
    ("B 无原典可读（未读梵本／未校原书）", ("未读", "未校", "梵本", "藏译", "希腊文本", "未及核对")),
    ("C 版本与篇次（须核校本）", ("篇次", "分卷", "篇数", "版本", "校本", "栏码", "品次", "编次", "分章",
                                  "须核", "原书", "集释", "异文", "具体例证", "具体措辞", "具体条目", "文本见")),
    ("D 生卒与年代推定", ("生卒", "生年", "卒年", "推定", "约数", "系年", "年代")),
    ("E 归属与真伪（托名／作者问题）", ("托名", "真伪", "归属", "作者问题", "作者是谁", "有争议", "争议很大")),
    ("F 解释分歧（本页只作并述）", ("解读", "解释", "不同意见", "并述", "不裁定", "学界有不同",
                                    "取通行", "本页取", "一般表述", "只作对照", "结构对照")),
    ("G 无专门研究（只有语境性引用）", ("无 SEP", "无 IEP", "语境性", "专门研究", "无专属")),
]


def classify(note):
    n = note or ""
    for name, keys in RULES:
        for k in keys:
            if k in n:
                return name
    return "Z 其他"


def load():
    items = []
    for f in sorted(glob.glob(os.path.join(DATA, "*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        unit = d.get("title")
        region = d.get("region")
        for p in d.get("philosophers", []):
            if p.get("needs_verification"):
                items.append(("哲学家", unit, region, p["id"], p.get("name", ""), p.get("pending_notes") or "", p.get("sources") or []))
        for c in d.get("concepts", []):
            if c.get("needs_verification"):
                items.append(("概念", unit, region, c["id"], c.get("term", ""), c.get("pending_notes") or "", c.get("sources") or []))
        for b in d.get("debates", []):
            if b.get("needs_verification"):
                items.append(("争论", unit, region, b["id"], b.get("title", ""), b.get("pending_notes") or "", b.get("sources") or []))
    wj = json.load(open(os.path.join(DATA, "works.json"), encoding="utf-8"))
    for w in wj.get("works", []):
        if w.get("needs_verification"):
            items.append(("著作", "（著作）", w.get("tradition"), w["id"], w.get("title", ""), w.get("pending_notes") or "", w.get("sources") or []))
    cj = json.load(open(os.path.join(DATA, "comparative.json"), encoding="utf-8"))
    for e in cj.get("essays", []):
        if e.get("needs_verification"):
            items.append(("比较篇", "（比较）", "—", e["id"], e.get("title", ""), e.get("pending_notes") or "", e.get("sources") or []))
    return items


def main():
    items = load()
    src_type = {s["id"]: s.get("type") for s in json.load(open(os.path.join(ROOT, "sources.json"), encoding="utf-8"))["sources"]}
    by_class = defaultdict(list)
    has_primary = 0
    for layer, unit, region, iid, name, note, srcs in items:
        by_class[classify(note)].append((layer, unit, iid, name, note))
        if any(src_type.get(x) == "原典" for x in srcs):
            has_primary += 1
    lines = ["# DEBT_CLASSES.md —— 欠账按「为何待核」分类（工具生成，勿手改）", "",
             "`DEBT.md` 给的是总量；本表回答**哪些能核、哪些核不了**。", "",
             "分类按 `pending_notes` 的关键词判定，规则顺序即优先级（先判硬阻塞）。", ""]
    lines.append("| 类别 | 条数 | 能否核销 |")
    lines.append("|---|---|---|")
    can = {"C 版本与篇次（须核校本）": "需**校外书**（站内无该文本时，能核者有限）",
           "D 生卒与年代推定": "**部分能**（若有专门研究）",
           "E 归属与真伪（托名／作者问题）": "**部分能**（若有研究）",
           "F 解释分歧（本页只作并述）": "**不能**（本页的写法即结论：并述不裁定）",
           "G 无专门研究（只有语境性引用）": "**不能**（须先有专门研究）",
           "A 无底本（原书已佚／仅存辑本）": "**不能**（底本已佚）",
           "B 无原典可读（未读梵本／未校原书）": "**不能**（缺原典）",
           "Z 其他": "待判"}
    for k in sorted(by_class):
        lines.append("| %s | %d | %s |" % (k, len(by_class[k]), can.get(k, "待判")))
    lines.append("| **合计** | **%d** | |" % len(items))
    lines.append("")
    lines.append("## 结论")
    lines.append("")
    blocked = sum(len(v) for k, v in by_class.items() if k.startswith(("A", "B", "F", "G")))
    lines.append("**其中 %d 条的条目已挂着「原典」类来源** —— 这些是最有望先核的一批（有底本线索）。" % has_primary)
    lines.append("")
    lines.append("**%d / %d 条属「结构性待核」**（无底本、无原典、本页即作并述、无专门研究）——"
                 "这些不是欠账，是**方法的边界**：在拿到材料之前，它们的正确写法就是「待核实」。" % (blocked, len(items)))
    lines.append("")
    lines.append("可动的只有 **版本篇次（C）** 与部分 **生卒（D）／归属（E）**。每轮只挑其中的少数去核，"
                 "并在 `VERIFIED.md` 记「已核（第 N 轮，据 source_id）：内容」。")
    lines.append("")
    for k in sorted(by_class):
        v = by_class[k]
        lines.append("## %s（%d 条）" % (k, len(v)))
        lines.append("")
        lines.append("| 层 | 单元 | id | 名称 |")
        lines.append("|---|---|---|---|")
        for layer, unit, iid, name, note in v[:12]:
            lines.append("| %s | %s | `%s` | %s |" % (layer, unit, iid, name))
        if len(v) > 12:
            lines.append("| … | | | 余 %d 条 |" % (len(v) - 12))
        lines.append("")
    text = "\n".join(lines) + "\n"
    if "--list" in sys.argv:
        for line in text.splitlines()[:40]:
            print(line)
        return
    open(OUT, "w", encoding="utf-8", newline="\n").write(text)
    print("DEBT_CLASSES.md 已写：合计 %d 条；结构性待核 %d 条" % (len(items), blocked))


if __name__ == "__main__":
    main()
