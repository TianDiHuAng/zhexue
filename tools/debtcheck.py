#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""debtcheck.py —— 待核实项（欠账）的盘点工具（D72，第 295 轮新增）

用途：
  1) 统计 needs_verification=true 的条目，按单元／类型分组，输出 DEBT.md；
  2) 供"还账轮"按序消化：每轮核 3—5 条，把核过的项在 pending_notes 里记明
     （格式：「已核（第 N 轮，据 <source_id>）：<核到的内容>」），
     全部核清者把 needs_verification 置 false。

用法：
  python tools/debtcheck.py            # 只统计并写 DEBT.md
  python tools/debtcheck.py --list 20  # 另打印前 20 条清单
"""
import json, glob, sys, collections, os

def load():
    W = json.load(open('data/works.json', encoding='utf-8'))['works']
    C = json.load(open('data/comparative.json', encoding='utf-8'))['essays']
    P = []
    for f in sorted(glob.glob('data/*/*.json')):
        d = json.load(open(f, encoding='utf-8'))
        unit = d.get('unit_id') or f.replace('\\', '/').split('/')[-1][:-5]
        for p in d.get('philosophers', []):
            P.append((unit, p))
    return W, C, P

def main():
    W, C, P = load()
    debt = collections.Counter()
    rows = []
    for unit, p in P:
        if p.get('needs_verification'):
            debt['哲学家'] += 1
            rows.append(('哲学家', unit, p['id'], p.get('name', ''), (p.get('pending_notes') or '')[:60]))
    for x in W:
        if x.get('needs_verification'):
            debt['著作'] += 1
            rows.append(('著作', 'works', x['id'], x.get('title', ''), (x.get('pending_notes') or '')[:60]))
    for e in C:
        if e.get('needs_verification'):
            debt['比较篇'] += 1
            rows.append(('比较篇', 'comparative', e['id'], e.get('title', ''), (e.get('pending_notes') or '')[:60]))
    total = sum(debt.values())

    lines = ["# DEBT.md —— 待核实项（欠账）清单（D72）", "",
             "统计方式：`needs_verification=true` 的条目。",
             "还账方式：核过一项，就在 `pending_notes` 里写「已核（第 N 轮，据 <source_id>）：<内容>」；",
             "　　　　　全部核清者把 `needs_verification` 置 `false`。", "",
             "当前合计：**%d 条**（哲学家 %d ｜ 著作 %d ｜ 比较篇 %d）" % (
                 total, debt['哲学家'], debt['著作'], debt['比较篇']), ""]
    byunit = collections.Counter(r[1] for r in rows)
    lines.append("## 按单元分布")
    for u, n in byunit.most_common():
        lines.append("- %s：%d" % (u, n))
    lines.append("")
    open('DEBT.md', 'w', encoding='utf-8', newline='\n').write("\n".join(lines) + "\n")
    print("DEBT.md 已写：合计 %d 条（哲学家 %d ｜ 著作 %d ｜ 比较篇 %d）" % (
        total, debt['哲学家'], debt['著作'], debt['比较篇']))
    if '--list' in sys.argv:
        n = 20
        i = sys.argv.index('--list')
        if i + 1 < len(sys.argv) and sys.argv[i+1].isdigit():
            n = int(sys.argv[i+1])
        for r in rows[:n]:
            print("  %s ｜ %s ｜ %s ｜ %s" % r[:4])

if __name__ == '__main__':
    main()
