# -*- coding: utf-8 -*-
"""refcheck.py —— 全库引用有效性检查器（D62）

用途：检查所有"指向 id 的引用"是否都落在全库已有的 id 上（跨单元亦须存在）。
覆盖字段：related_people / influenced / influenced_by / usages[].id / related / sources
（R11 只检"是否在本单元"，refcheck 检"是否存在于全库"，二者互补。）

用法：python tools/refcheck.py    （失效引用则退出码 1）
"""
import json
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REF_FIELDS = ('related_people', 'related', 'sources')
REF_OBJ_FIELDS = ('influenced', 'influenced_by', 'usages')


def load():
    units = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', '*', '*.json'))):
        units[os.path.relpath(f, ROOT)] = json.load(open(f, encoding='utf-8'))
    works = json.load(open(os.path.join(ROOT, 'data', 'works.json'), encoding='utf-8'))
    comp = json.load(open(os.path.join(ROOT, 'data', 'comparative.json'), encoding='utf-8'))
    src = json.load(open(os.path.join(ROOT, 'sources.json'), encoding='utf-8'))
    return units, works, comp, src


def main():
    units, works, comp, src = load()

    people = set()
    concepts = set()
    all_ids = set()
    for rel, d in units.items():
        for p in d.get('philosophers', []):
            people.add(p['id']); all_ids.add(p['id'])
        for c in d.get('concepts', []):
            concepts.add(c['id']); all_ids.add(c['id'])
        for k in ('debates', 'schools'):
            for x in d.get(k, []) or []:
                if isinstance(x, dict) and 'id' in x:
                    all_ids.add(x['id'])
    for x in works.get('works', []):
        all_ids.add(x['id'])
    for x in comp.get('essays', []):
        all_ids.add(x['id'])
    sources = {s['id'] for s in src.get('sources', [])}

    problems = []

    def check_list(rel, owner, field, lst, valid):
        for v in lst or []:
            if isinstance(v, str):
                if v not in valid:
                    problems.append((rel, owner, field, v))
            elif isinstance(v, dict):
                vid = v.get('id')
                if vid and vid not in valid:
                    problems.append((rel, owner, field, vid))

    for rel, d in units.items():
        for p in d.get('philosophers', []):
            check_list(rel, p['id'], 'related_people', p.get('related_people'), people)
            for fld in ('influenced', 'influenced_by'):
                check_list(rel, p['id'], fld, p.get(fld), people)
        for c in d.get('concepts', []):
            check_list(rel, c['id'], 'related', c.get('related'), concepts)
            check_list(rel, c['id'], 'usages.id', c.get('usages'), people)
            check_list(rel, c['id'], 'sources', c.get('sources'), sources)
    for x in works.get('works', []):
        check_list('data/works.json', x['id'], 'related_people', x.get('related_people'), people)
        check_list('data/works.json', x['id'], 'sources', x.get('sources'), sources)
    for x in comp.get('essays', []):
        check_list('data/comparative.json', x['id'], 'sources', x.get('sources'), sources)

    if not problems:
        print('refcheck：全部引用有效（人物／概念／著作／比较篇／来源）')
        return 0

    print('refcheck：发现 %d 处失效引用' % len(problems))
    for rel, owner, field, bad in problems:
        print('  %s :: %s :: %s -> %s' % (rel, owner, field, bad))
    return 1


if __name__ == '__main__':
    sys.exit(main())
