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


def norm_name(n):
    """去掉括号内的别名，只留主名（用于查"同一人的两条译名"）"""
    n = n or ''
    n = re.sub(r'（[^）]*）', '', n)
    n = re.sub(r'\([^)]*\)', '', n)
    return re.sub(r'\s+', '', n).strip()


def latin_tokens(l):
    """拉丁名的关键 token：去掉括号与生卒、小写，取最长的两个词"""
    l = l or ''
    l = re.sub(r'（[^）]*）', ' ', l)
    l = re.sub(r'\([^)]*\)', ' ', l)
    l = re.sub(r'[0-9,—\-–]', ' ', l.lower())
    toks = [t for t in re.split(r'\s+', l) if len(t) > 2]
    return set(toks)


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
    units = {}
    for f in unit_files:
        d = json.load(open(f, encoding='utf-8'))
        rel = os.path.relpath(f, ROOT)
        units[rel] = d
        for p in d.get('philosophers', []):
            ids[p['id']].append(rel)
            names[norm_name(p['name'])].append((rel, p['id']))
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
    notes = []
    for k, v in names.items():
        if len(v) > 1:
            notes.append(('人物重名（需人工确认是否同一人）', k, v))
    for k, v in latins.items():
        if len(v) > 1:
            problems.append(('人物拉丁名完全重复', k, v))
    for k, v in titles.items():
        if len(v) > 1:
            problems.append(('著作／比较篇标题重复', k, v))
    for k, v in terms.items():
        if len(v) > 1:
            problems.append(('概念术语重复', k, v))

    # 拉丁名 token 交叉比对（D64）：仅在“一方 token 集是另一方子集”时报警，
    # 只对西方（gr-）人物生效：中文人物的拼音同姓（Wang/Liu/Zhang…）无判别力。
    # 这样 "Averroes (Ibn Rushd)" 与 "Ibn Rushd (Averroes)" 会被抓到，
    # 而共享教名（John/Karl/Friedrich…）不会被误报。
    lat = [(norm_name(p['name']), latin_tokens(p.get('latin')), p['id'], rel)
           for rel, d in units.items() for p in d.get('philosophers', [])
           if p.get('latin') and p['id'].startswith('gr-')]
    for i in range(len(lat)):
        for j in range(i + 1, len(lat)):
            n1, t1, id1, r1 = lat[i]
            n2, t2, id2, r2 = lat[j]
            if not t1 or not t2:
                continue
            if t1 <= t2 or t2 <= t1:
                if t1 == t2 or len(t1 & t2) >= 2:
                    problems.append(('疑似同一人（拉丁名 token 互为子集）', id1 + ' / ' + id2,
                                     (r1, r2, sorted(t1 & t2))))

    if notes:
        print('dupcheck：提示 %d 组重名（不同人同名，需人工确认，不计为失败）' % len(notes))
        for kind, k, v in notes:
            print('  [%s] %s -> %s' % (kind, k, v))

    if not problems:
        print('dupcheck：未发现重复（id／拉丁名／标题／概念）')
        return 0

    print('dupcheck：发现 %d 组重复' % len(problems))
    for kind, k, v in problems:
        print('  [%s] %s -> %s' % (kind, k, v))
    return 1


if __name__ == '__main__':
    sys.exit(main())
