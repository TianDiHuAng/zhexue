#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""thincheck.py —— 代表作数 ≤1 的哲学家盘点（D69），生成 THIN_WORKS.md

用法：
  python tools/thincheck.py            # 写 THIN_WORKS.md
  python tools/thincheck.py --list 20  # 另打印前 20 名
说明：与 debtcheck.py（D72，按 needs_verification 数）不同，本工具按
      `data/works.json` 中 related_people 的**计数**衡量覆盖厚薄。
"""
import json, glob, sys, collections

def main():
    W = json.load(open('data/works.json', encoding='utf-8'))['works']
    cnt = collections.Counter()
    for x in W:
        for r in (x.get('related_people') or []):
            cnt[r] += 1
    rows = []
    for f in sorted(glob.glob('data/*/*.json')):
        d = json.load(open(f, encoding='utf-8'))
        unit = d.get('unit_id') or f.replace('\\', '/').split('/')[-1][:-5]
        for p in d.get('philosophers', []):
            c = cnt.get(p['id'], 0)
            if c <= 1:
                rows.append((unit, p['name'], p['id'], c))
    zero = [r for r in rows if r[3] == 0]
    one = [r for r in rows if r[3] == 1]
    lines = ["# THIN_WORKS.md —— 代表作数 ≤1 的哲学家名单（D69）", "",
             "统计方式：`data/works.json` 中 `related_people` 的计数，取计数 ≤1 者。",
             "用途：`GAPS_WORKS` 归零后（第 287 轮）的**下一层缺口**——从「有无」转到「厚薄」。",
             "重生成：`python tools/thincheck.py`（每次改动作著关联后应重跑）。", "",
             "当前合计：**%d 人**（0 部 %d ｜ 1 部 %d）" % (len(rows), len(zero), len(one)), ""]
    if not rows:
        lines.append("**全部哲学家的代表作均 ≥2 部。**")
    else:
        by = collections.defaultdict(list)
        for u, n, i, c in rows:
            by[u].append((n, i, c))
        for u in sorted(by):
            lines.append("## " + u)
            for n, i, c in sorted(by[u]):
                lines.append("- %s（`%s`）—— %d 部" % (n, i, c))
            lines.append("")
    open('THIN_WORKS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(lines) + "\n")
    print("THIN_WORKS.md 已写：合计 %d 人（0 部 %d ｜ 1 部 %d）" % (len(rows), len(zero), len(one)))
    if '--list' in sys.argv:
        n = 20
        i = sys.argv.index('--list')
        if i + 1 < len(sys.argv) and sys.argv[i + 1].isdigit():
            n = int(sys.argv[i + 1])
        for r in rows[:n]:
            print("  %s ｜ %s ｜ %d 部" % (r[0], r[1], r[3]))

if __name__ == '__main__':
    main()
