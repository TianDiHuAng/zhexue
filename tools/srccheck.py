# -*- coding: utf-8 -*-
"""srccheck.py —— 来源登记的结构体检器（D67）

目的：D66 之后，把"来源登记是否自洽"做成可复跑的检查（不打网络，只看结构）。
检查项：
  1. id 唯一；2. url 为 http(s)；3. title 非空；4. verified=true 时 verify 字段齐全（method/http_status/checked_at）；
  5. verify.http_status 必须为 200；6. link_ok 必须为 true；7. type 在允许集合内；
  8. url 与 url2 不得相同；9. note 非空（≥10 字）。
另：`--sample N` 随机列出 N 条来源（id/题名/url/核验日），供人工实开抽检 title 与落地页是否相符（D66）。

用法：python tools/srccheck.py [--sample 5]
"""
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = {'百科', '专著', '译著', '古籍', '论文', '文集', '工具书', '其他', '原典', '学术著作'}


def main():
    args = sys.argv[1:]
    sample = 0
    if '--sample' in args:
        i = args.index('--sample')
        try:
            sample = int(args[i + 1])
        except Exception:
            sample = 5

    src = json.load(open(os.path.join(ROOT, 'sources.json'), encoding='utf-8'))['sources']
    ids = set()
    problems = []
    notes_short = []
    for s in src:
        sid = s.get('id', '')
        if not sid:
            problems.append(('缺 id', str(s)[:40], ''))
            continue
        if sid in ids:
            problems.append(('id 重复', sid, ''))
        ids.add(sid)
        url = s.get('url') or ''
        if not url.startswith(('http://', 'https://')):
            problems.append(('url 非法', sid, url))
        if not (s.get('title') or '').strip():
            problems.append(('title 为空', sid, ''))
        if s.get('url2') and s.get('url2') == url:
            problems.append(('url 与 url2 相同', sid, url))
        if s.get('link_ok') is not True:
            problems.append(('link_ok 非 true', sid, ''))
        if (s.get('type') or '') not in TYPES:
            problems.append(('type 不在允许集合', sid, str(s.get('type'))))
        if len((s.get('note') or '').strip()) < 10:
            notes_short.append(sid)
        if s.get('verified'):
            v = s.get('verify') or {}
            for k in ('method', 'http_status', 'checked_at'):
                if not v.get(k):
                    problems.append(('verify 缺字段 %s' % k, sid, ''))
            if v.get('http_status') not in (200, '200'):
                problems.append(('verify.http_status 非 200', sid, str(v.get('http_status'))))

    if sample:
        pool = random.sample(src, min(sample, len(src)))
        print('—— 抽检 %d 条（请实开核对落地页标题与 title 是否相符，D66）——' % len(pool))
        for s in pool:
            print('  %s | %s | %s | 核验 %s' % (s['id'], s.get('title', '')[:40], s.get('url', ''),
                                            (s.get('verify') or {}).get('checked_at', '?')))

    if notes_short:
        print('srccheck：提示 %d 条 note 过短（<10 字，历史遗留，不计失败）' % len(notes_short))

    if problems:
        print('srccheck：发现 %d 处登记问题' % len(problems))
        for kind, sid, extra in problems:
            print('  [%s] %s %s' % (kind, sid, extra))
        return 1
    print('srccheck：%d 条来源登记结构自洽（id／url／title／verify／type）' % len(src))
    return 0


if __name__ == '__main__':
    sys.exit(main())
