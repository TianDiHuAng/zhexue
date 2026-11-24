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
import re
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


# ===== 第110轮新增（D38 落地）：著作标题的规范化查重 =====
WORKS = os.path.join(HERE, "..", "data", "works.json")
ALIASES = os.path.join(HERE, "..", "data", "aliases.json")

# 常见的书名后缀与版本括注：规范化时去掉
_SUFFIXES = ("篇", "章", "（上）", "（下）", "（一）", "（二）")
_VERSION_HINTS = ("（四庫全書本）", "（四部叢刊本）", "（四部丛刊本）", "（英文維基文庫）",
                  "（英文维基文库）", "（Project Gutenberg 英译全文）", "（英译）", "（节译本）",
                  "（拉丁原文）", "（拉丁原文选）", "（宗宝本）")


def norm_title(t):
    """把书名规范化为可比较的形式：去《》、去版本括注、去篇/章等后缀、去空白。"""
    if not t:
        return ""
    s = t.strip()
    for v in _VERSION_HINTS:
        s = s.replace(v, "")
    s = s.replace("《", "").replace("》", "").replace(" ", "").replace("　", "")
    # D47：去掉任何括注（不仅限于版本括注），如「（道德经）」「（一名 X）」
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    changed = True
    while changed:
        changed = False
        for suf in _SUFFIXES:
            if s.endswith(suf) and len(s) > len(suf):
                s = s[: -len(suf)]
                changed = True
    return s


def norm_title_loose(t):
    """更宽松的规范化：在 norm_title 之外，再去掉前缀「论」并统一语序（论X / X论 视为同）。

    第110轮新增（D39）：中文书名有「论义务」与「义务论」这类语序互换的变体，
    规范化后仍不同，故须额外比较。做法：得到一个「字集合 + 去论前缀」的键。
    """
    s = norm_title(t)
    # 去掉「论/谈/说/辨/辩」等虚词（不论在首在尾），再按字排序，故
    # 「论义务」与「义务论」得到同一个键。
    for w in ("论", "談", "谈", "說", "说", "辨", "辩", "辯"):
        s = s.replace(w, "")
    return "".join(sorted(s))


def load_work_titles():
    with open(WORKS, encoding="utf-8") as f:
        d = json.load(f)
    return [w.get("title", "") for w in d.get("works", [])]


def load_alias_map():
    """读别名表，返回 {规范化键: 组内第一个名字}（D40）。"""
    m = {}
    if not os.path.exists(ALIASES):
        return m
    with open(ALIASES, encoding="utf-8") as f:
        d = json.load(f)
    for group in d.get("work-titles", []):
        if not group:
            continue
        rep = norm_title(group[0])          # 组内第一个名字作代表
        for name in group:
            # 注意：别名键用 norm_title（去篇/版本），不能用 norm_title_loose
            # （后者按字排序，会把「斐德若」「斐德罗」排成不同的键，别名即失效）
            m[norm_title(name)] = rep
    return m


def alias_of(title):
    """返回该标题所属别名组的代表名（无则 None）。"""
    am = load_alias_map()
    return am.get(norm_title(title))


def find_work_conflicts(titles):
    """返回 {拟用标题: 已存在标题} 的冲突表（规范化后相同即视为冲突）。"""
    existing = load_work_titles()
    norm_map = {}
    loose_map = {}
    for t in existing:
        norm_map.setdefault(norm_title(t), []).append(t)
        loose_map.setdefault(norm_title_loose(t), []).append(t)
    conflicts = {}
    for t in titles:
        k = norm_title(t)
        k2 = norm_title_loose(t)
        if k in norm_map:
            conflicts[t] = norm_map[k][0]
        elif len(k2) >= 3 and k2 in loose_map:   # D46：短标题（≤2字）不做宽松匹配，避免「中论」撞「中说」
            conflicts[t] = loose_map[k2][0] + "（宽松匹配：语序/虚词变体）"
        else:
            al = alias_of(t)
            if al:
                for t2 in existing:
                    if alias_of(t2) == al:
                        conflicts[t] = t2 + "（别名表匹配：译名变体）"
                        break
    return conflicts


def require_work_title_new(titles):
    """拟新增的著作标题不得与既有著作同名（规范化后比较）。

    用法：
        from precheck_src import require_work_title_new
        require_work_title_new(["《会饮》", "《智者》"])
    """
    conflicts = find_work_conflicts(titles)
    if conflicts:
        msg = "；".join("%s → 已存在：%s" % (a, b) for a, b in conflicts.items())
        raise AssertionError("著作标题重复（D38 规范化查重）：%s" % msg)
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


def require_work_id_new(ids):
    """D51：id 唯一性单独核对（标题查重不保证 id 唯一）。"""
    import json, glob as _g
    have = set()
    for f in _g.glob('data/*/*.json'):
        d = json.load(open(f, encoding='utf-8'))
        if isinstance(d, dict) and 'philosophers' in d:
            for k in ('philosophers', 'concepts', 'debates'):
                for x in d.get(k, []) or []:
                    if isinstance(x, dict) and x.get('id'):
                        have.add(x['id'])
    for f in ('data/works.json', 'data/schools.json', 'data/comparative.json'):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for k in ('works', 'schools', 'essays'):
            for x in d.get(k, []) or []:
                if isinstance(x, dict) and x.get('id'):
                    have.add(x['id'])
    bad = [i for i in ids if i in have]
    if bad:
        raise AssertionError("id 已被占用（D51）：%s" % ", ".join(bad))


def require_concept_term_new(terms):
    """D54：概念 term 必须在全部单元内唯一（check.py 不跨单元查同名，只有体检的重复标题能抓）。"""
    import json, glob as _g
    seen = {}
    for f in _g.glob('data/*/*.json'):
        d = json.load(open(f, encoding='utf-8'))
        if isinstance(d, dict) and 'concepts' in d:
            for c in d['concepts']:
                seen[c.get('term')] = d.get('unit_id', f)
    bad = [(t, seen[t]) for t in terms if t in seen]
    if bad:
        raise AssertionError("概念术语已存在（D54 全局查重）：%s" % "; ".join("%s@%s" % b for b in bad))


def find_work_superset_conflicts(extra_titles=None):
    """D58：只找"书名 + 少量尾缀"的同一书嫌疑（如《政府论》vs《政府论》两篇）。
    精确规则：较长者 = 较短者 + 尾缀，尾缀属于已知可加项（两篇/和基础/第一卷/上卷…）或“和/与/及+X”。
    含有“·”的篇目（如《荀子·劝学》）不参与比较，避免与书名批次混淆。"""
    import json as _j, re as _re
    SUF = ("两篇", "三篇", "和基础", "第一卷", "第二卷", "上卷", "下卷", "上", "下", "全译本", "节译本")

    def core(t):
        t = _re.sub(r"[（(][^）)]*[）)]", "", str(t))
        t = _re.sub(r"[《》〈〉\s]", "", t)
        return t

    titles = []
    try:
        for w in _j.load(open('data/works.json', encoding='utf-8'))['works']:
            for k in ('title', 'title_original'):
                v = w.get(k)
                if v and '·' not in str(v):
                    titles.append((core(v), w.get('id')))
    except Exception:
        pass
    for t in (extra_titles or []):
        if '·' not in str(t):
            titles.append((core(t), '<new>'))

    try:
        _wl = set(tuple(sorted(p)) for p in _j.load(open('data/superset_whitelist.json', encoding='utf-8'))['pairs'])
    except Exception:
        _wl = set()

    out, seen = [], set()
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            a, b = titles[i][0], titles[j][0]
            if not a or not b or a == b:
                continue
            sh, lo = (a, b) if len(a) <= len(b) else (b, a)
            if not lo.startswith(sh):
                continue
            suf = lo[len(sh):]
            ok = (suf in SUF) or bool(_re.match(r'^(和|与|及).{1,3}$', suf))
            if not ok:
                continue
            key = (sh, lo)
            if key in seen or key in _wl:
                continue
            seen.add(key)
            out.append((sh, lo, len(suf)))
    return out


def require_work_superset_clean(extra_titles=None):
    """与 find_work_superset_conflicts 同源；预检用打印（不阻断），需要阻断时调用此函数的返回自行判断。"""
    bad = find_work_superset_conflicts(extra_titles)
    if bad:
        print('  [D58 提示] 疑似超集标题（请人工确认是否为同一书）：' +
              '；'.join('%s ⊂ %s(+%d)' % b for b in bad))
    return bad
