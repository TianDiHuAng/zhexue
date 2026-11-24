# -*- coding: utf-8 -*-
"""dupcheck.py —— 全库重复检查器（D61）

用途：在建页前后检查四类重复：
  1. id 重复（跨单元／跨实体类型）
  2. 哲学家重名（按中文名与拉丁名）
  3. 著作标题重复（去书名号与空白后比较）
  4. 概念术语重复、比较篇标题重复

用法：python tools/dupcheck.py    （有重复则退出码 1）
"""
import json
import glob
import os
import re
import sys
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm_title(t):
    t = t or ''
    t = t.replace('《', '').replace('》', '')
    t = re.sub(r'\s+', '', t)
    return t


def main():
    ids = collections.defaultdict(list)
    names = collections.defaultdict(list)
    latins = collections.defaultdict(list)
    titles = collections.defaultdict(list)
    terms = collections.defaultdict(list)

    unit_files = sorted(glob.glob(os.path.join(ROOT, 'data', '*', '*.json')))
    for f in unit_files:
        d = json.load(open(f, encoding='utf-8'))
        rel = os.path.relpath(f, ROOT)
        for p in d.get('philosophers', []):
            ids[p['id']].append(rel)
            names[p['name']].append((rel, p['id']))
            if p.get('latin'):
                latins[p['latin'].strip().lower()].append((rel, p['id']))
        for c in d.get('concepts', []):
            ids[c['id']].append(rel)
            terms[c['term']].append((rel, c['id']))
        for k in ('debates', 'schools'):
            for x in d.get(k, []):
                if isinstance(x, dict) and 'id' in x:
                    ids[x['id']].append(rel)

    for fn, key in (('works.json', 'works'), ('comparative.json', 'essays')):
        p = os.path.join(ROOT, 'data', fn)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for x in d.get(key, []):
            ids[x['id']].append('data/' + fn)
            if x.get('title'):
                titles[norm_title(x['title'])].append((fn, x['id']))

    problems = []
    for k, v in ids.items():
        if len(v) > 1:
            problems.append(('id 重复', k, v))
    for k, v in names.items():
        if len(v) > 1:
            problems.append(('人物重名', k, v))
    for k, v in latins.items():
        if len(v) > 1:
            problems.append(('人物拉丁名重复', k, v))
    for k, v in titles.items():
        if len(v) > 1:
            problems.append(('著作／比较篇标题重复', k, v))
    for k, v in terms.items():
        if len(v) > 1:
            problems.append(('概念术语重复', k, v))

    if not problems:
        print('dupcheck：未发现重复（id／人物名／拉丁名／标题／概念）')
        return 0

    print('dupcheck：发现 %d 组重复' % len(problems))
    for kind, k, v in problems:
        print('  [%s] %s -> %s' % (kind, k, v))
    return 1


if __name__ == '__main__':
    sys.exit(main())
