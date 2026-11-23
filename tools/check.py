#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段 2：内容校验器 —— 全项目质量守门员。

用法：
    python tools/check.py                 # 校验全部单元 + 流派
    python tools/check.py --file data/china/cn-xianqin.json
    python tools/check.py --quiet         # 只打印汇总

规则（与 DECISIONS.md 对应）：
  R1  必填字段非空                      R11 内部链接目标存在（图/概念/争论的 id）
  R2  年份合法（含公元前、生卒顺序）      R12 双源规则（≥2 且 verified）
  R3  来源 id 必须存在于 sources.json     R13 流派页结构
  R4  引文必须有原典出处 + 长度上限       R14 概念用法差异（≥2 位，且说法不同）
  R5  重复检测（单元内同名 / 全局 id）    R15 争论结构（≥2 方 + 焦点 + 定论说明）
  R6  SVG 合法性（XML/白名单/越界）       R16 id 字符集 a-z0-9-
  R7  计数限制（哲学家 4-8 / 概念 6-10 / 争论 2-3）
  R8  year_display 与 year 一致
  R9  全局 id 唯一
  R10 needs_verification 与 pending_notes 联动
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SOURCES = os.path.join(ROOT, "sources.json")
SCHOOLS = os.path.join(DATA, "schools.json")
WORKS = os.path.join(DATA, "works.json")
COMPARATIVE = os.path.join(DATA, "comparative.json")

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
KINDS = {"原文", "后人解读"}
SVG_ALLOWED = {"svg", "g", "text", "tspan", "rect", "line", "path", "circle",
               "ellipse", "polygon", "polyline", "defs", "marker", "title", "desc"}
NUM = re.compile(r"-?\d+(?:\.\d+)?")

errors = []
warnings = []


def err(where, rule, msg):
    errors.append("%s [%s] %s" % (where, rule, msg))


def warn(where, rule, msg):
    warnings.append("%s [%s] %s" % (where, rule, msg))


# ------------------------------------------------------------------ 基础工具
def load_sources():
    with open(SOURCES, encoding="utf-8") as f:
        data = json.load(f)
    return {s["id"]: s for s in data["sources"]}


def nonempty(v):
    if v is None:
        return False
    if isinstance(v, str):
        return len(v.strip()) > 0
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return True


def need(where, rule, obj, fields, mins=None):
    """R1：必填字段。mins = {field: 最小字数}"""
    for f in fields:
        if not nonempty(obj.get(f)):
            err(where, rule, "缺必填字段 %s" % f)
    if mins:
        for f, n in mins.items():
            v = obj.get(f)
            if isinstance(v, str) and len(v.strip()) < n:
                err(where, "R10", "字段 %s 过短（%d 字，要求 ≥%d）" % (f, len(v.strip()), n))


def check_id(where, obj):
    i = obj.get("id", "")
    if not ID_RE.match(i or ""):
        err(where, "R16", "id 非法：%r（只允许 a-z 0-9 -）" % i)


def check_sources(where, obj, src, rule="R3", need_n=2):
    ids = obj.get("sources") or []
    if not isinstance(ids, list):
        err(where, rule, "sources 必须是数组")
        return
    for sid in ids:
        if sid not in src:
            err(where, rule, "来源 id 未定义：%s" % sid)
        elif not src[sid].get("verified"):
            err(where, rule, "来源未通过核验（verified=false）：%s" % sid)
    uniq = len(set(ids))
    if uniq < need_n:
        if not (obj.get("needs_verification") and nonempty(obj.get("pending_notes"))):
            err(where, "R12", "双源规则：sources 只有 %d 个不同来源，且未标 needs_verification+pending_notes" % uniq)


def check_pending(where, obj):
    """R10：needs_verification 与 pending_notes 联动"""
    nv = obj.get("needs_verification", False)
    pn = obj.get("pending_notes", "")
    if nv and not nonempty(pn):
        err(where, "R10", "needs_verification=true 但 pending_notes 为空")
    if not nv and nonempty(pn):
        warn(where, "R10", "填了 pending_notes 但 needs_verification=false（应改 true）")


def check_kind(where, obj, rule="R13", required=True):
    k = obj.get("kind")
    if required or k is not None:
        if k not in KINDS:
            err(where, rule, "kind 必须是 原文 / 后人解读，实际 %r" % k)


def check_years(where, obj):
    """R2 + R9 年份"""
    b, d = obj.get("birth_year"), obj.get("death_year")
    for k in ("birth_year", "death_year"):
        if not isinstance(obj.get(k), int):
            err(where, "R2", "%s 必须是整数（公元前用负数），实际 %r" % (k, obj.get(k)))
    for k in ("birth_display", "death_display"):
        need(where, "R1", obj, [k])
    if isinstance(b, int) and isinstance(d, int) and b > d:
        err(where, "R2", "生年 %d 晚于卒年 %d" % (b, d))
    if isinstance(b, int) and b < -3000 or isinstance(d, int) and d < -3000:
        err(where, "R2", "年份超出合理范围")
    # R8 display 一致性
    for k, yk in (("birth_display", "birth_year"), ("death_display", "death_year")):
        disp, y = obj.get(k) or "", obj.get(yk)
        m = NUM.search(disp)
        if not m or not isinstance(y, int):
            continue
        v = int(float(m.group()))
        if "前" in disp[:disp.find(m.group()) + 1] or "BCE" in disp.upper():
            v = -v
        if abs(v) != abs(y):
            err(where, "R8", "%s（%r）与 %s（%d）不一致" % (k, disp, yk, y))


def check_svg(where, svg, rule="R6"):
    if not nonempty(svg):
        return
    s = svg.replace("'/<", "'/><")
    try:
        root = ET.fromstring(s)
    except ET.ParseError as e:
        err(where, rule, "SVG XML 解析失败：%s" % e)
        return
    if "script" in s.lower() or re.search(r"\son[a-z]+\s*=", s):
        err(where, rule, "SVG 含脚本或事件属性")
    vb = root.get("viewBox")
    if not vb:
        err(where, rule, "SVG 缺 viewBox")
        return
    parts = [float(x) for x in vb.replace(",", " ").split()]
    if len(parts) != 4:
        err(where, rule, "viewBox 格式错误：%r" % vb)
        return
    W, H = parts[2], parts[3]
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in SVG_ALLOWED:
            err(where, rule, "SVG 含非白名单元素 <%s>" % tag)
    # 越界检测（容差 2px）
    def num(el, a, default=None):
        v = el.get(a, default)
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag == "rect":
            x, y, w, h = num(el, "x", 0), num(el, "y", 0), num(el, "width", 0), num(el, "height", 0)
            if None in (x, y, w, h):
                err(where, rule, "rect 坐标/尺寸不是数字")
                continue
            if x < -2 or y < -2 or x + w > W + 2 or y + h > H + 2:
                err(where, rule, "rect 越界：(x=%s y=%s w=%s h=%s) 于 %sx%s" % (x, y, w, h, W, H))
        elif tag in ("text", "tspan"):
            x, y = num(el, "x"), num(el, "y")
            if x is not None and (x < -2 or x > W + 2):
                err(where, rule, "text x 越界：%s" % x)
            if y is not None and (y < -2 or y > H + 2):
                err(where, rule, "text y 越界：%s" % y)
        elif tag == "line":
            for a, lim in (("x1", W), ("x2", W), ("y1", H), ("y2", H)):
                v = num(el, a)
                if v is not None and (v < -2 or v > lim + 2):
                    err(where, rule, "line %s 越界：%s" % (a, v))


# ------------------------------------------------------------------ 单元校验
def check_unit(path, src, global_ids, unit_ids):
    fname = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            u = json.load(f)
    except Exception as e:  # noqa: BLE001
        err(fname, "R1", "JSON 解析失败：%s" % e)
        return

    uid = u.get("unit_id", "")
    where0 = fname
    need(where0, "R1", u, ["unit_id", "region", "title", "period", "summary", "threads",
                           "philosophers", "concepts", "debates"],
         mins={"summary": 60, "title": 2})
    if not ID_RE.match(uid or ""):
        err(where0, "R16", "unit_id 非法：%r" % uid)
    if uid in unit_ids:
        err(where0, "R9", "unit_id 重复：%s" % uid)
    unit_ids.add(uid)
    if u.get("region") not in ("china", "west"):
        err(where0, "R1", "region 必须是 china / west")
    sy, ey = u.get("start_year"), u.get("end_year")
    if not (isinstance(sy, int) and isinstance(ey, int)):
        err(where0, "R2", "start_year / end_year 必须是整数")
    elif sy >= ey:
        err(where0, "R2", "start_year(%d) 不早于 end_year(%d)" % (sy, ey))

    ph = u.get("philosophers") or []
    co = u.get("concepts") or []
    db = u.get("debates") or []
    if not 4 <= len(ph) <= 60:
        err(where0, "R7", "哲学家数量 %d，要求 4-60" % len(ph))
    if not 6 <= len(co) <= 30:
        err(where0, "R7", "概念数量 %d，要求 6-30" % len(co))
    if not 2 <= len(db) <= 12:
        err(where0, "R7", "争论数量 %d，要求 2-12" % len(db))

    # ---- 先收集全部 id（供两遍引用校验，避免"尚未出现"的假警告）
    all_ph = {p.get("id") for p in ph}
    all_co = {c.get("id") for c in co}

    # ---- 哲学家
    unit_ph_ids, unit_concept_ids, names = set(), set(), {}
    for p in ph:
        pid = p.get("id", "")
        where = "%s / %s" % (fname, pid or "?")
        check_id(where, p)
        if pid in global_ids:
            err(where, "R9", "哲学家 id 全局重复：%s" % pid)
        global_ids.add(pid)
        unit_ph_ids.add(pid)
        nm = p.get("name", "")
        if nm in names:
            err(where, "R5", "同一单元内同名人物：%s" % nm)
        names[nm] = pid
        need(where, "R1", p, ["name", "latin", "birth_year", "death_year", "birth_display",
                              "death_display", "birth_note", "death_note", "era",
                              "core_questions", "arguments", "works", "school",
                              "criticisms", "misconceptions", "svg", "sources"],
             mins={"era": 40, "birth_note": 6, "death_note": 6})
        check_years(where, p)
        if isinstance(sy, int) and isinstance(p.get("birth_year"), int):
            if p["birth_year"] < sy - 80 or p["death_year"] > ey + 60:
                err(where, "R2", "生卒（%d/%d）落在单元范围（%d—%d）之外过多"
                    % (p["birth_year"], p["death_year"], sy, ey))
        # 论点
        args = p.get("arguments") or []
        if len(args) < 2:
            err(where, "R10", "论点少于 2 条（要求前提→推理→结论的完整结构）")
        for i, a in enumerate(args, 1):
            w2 = "%s / arg%d" % (where, i)
            need(w2, "R1", a, ["claim", "premises", "inference", "conclusion", "kind"],
                 mins={"claim": 6, "inference": 10, "conclusion": 6})
            check_kind(w2, a)
            if not isinstance(a.get("premises"), list) or not a.get("premises"):
                err(w2, "R1", "premises 必须是非空数组")
        # 著作
        for w3 in p.get("works") or []:
            need("%s / work" % where, "R1", w3, ["title", "edition"],
                 mins={"edition": 8})
        # 批评
        crit = p.get("criticisms") or []
        if len(crit) < 1:
            err(where, "R10", "criticisms 至少 1 条")
        for c in crit:
            need("%s / criticism" % where, "R1", c, ["critic", "view", "response", "kind"],
                 mins={"view": 8, "response": 4})
            check_kind("%s / criticism" % where, c)
            check_sources("%s / criticism" % where, c, src, "R3", 2)
        # 误解
        for m in p.get("misconceptions") or []:
            need("%s / misconception" % where, "R1", m, ["claim", "why"],
                 mins={"why": 10})
        if len(p.get("misconceptions") or []) < 1:
            err(where, "R10", "misconceptions 至少 1 条")
        # 引文
        for q in p.get("quotes") or []:
            w4 = "%s / quote" % where
            need(w4, "R1", q, ["text", "source_id", "locator", "kind"])
            sid = q.get("source_id")
            if sid not in src:
                err(w4, "R3", "引文来源未定义：%s" % sid)
            elif src[sid].get("type") != "原典":
                err(w4, "R4", "引文来源必须是原典（type=原典），实际 %s" % src[sid].get("type"))
            elif not src[sid].get("verified"):
                err(w4, "R3", "引文来源未通过核验：%s" % sid)
            t = q.get("text") or ""
            if len(t) > 60:
                err(w4, "R4", "引文过长（%d 字 > 60），不得大段搬用译本" % len(t))
            if not nonempty(q.get("locator")):
                err(w4, "R4", "引文缺篇目定位（locator）")
            check_kind(w4, q, "R4")
            if re.search(r"[“”\"]{2}", t):
                warn(w4, "R4", "引文内含多组引号，确认是否为拼接")
        # R19：学说详述与著作详录（新层；存在时校验结构）
        doc = p.get("doctrine")
        if doc is not None:
            need(where + " / doctrine", "R19", doc, ["summary", "system", "phases", "reception"],
                 mins={"summary": 80, "reception": 40})
            if not isinstance(doc.get("system"), list) or len(doc.get("system") or []) < 2:
                err(where + " / doctrine", "R19", "system 至少 2 条")
            for x in doc.get("system") or []:
                need(where + " / doctrine.system", "R19", x, ["name", "content"], mins={"content": 20})
            for x in doc.get("phases") or []:
                need(where + " / doctrine.phases", "R19", x, ["period", "change"], mins={"change": 15})
        wd = p.get("works_detail")
        if wd is not None:
            if not isinstance(wd, list) or not wd:
                err(where + " / works_detail", "R19", "works_detail 必须是非空数组")
            for x in wd:
                need(where + " / works_detail", "R19", x,
                     ["title", "structure", "core_thesis", "editions"],
                     mins={"structure": 15, "core_thesis": 15, "editions": 8})
        check_svg(where, p.get("svg"))
        check_sources(where, p, src)
        check_pending(where, p)
        # 影响链内部引用
        for key in ("influenced", "influenced_by"):
            for r2 in p.get(key) or []:
                need("%s / %s" % (where, key), "R1", r2, ["name", "note"])
                if r2.get("id") and r2["id"] not in all_ph:
                    err("%s / %s" % (where, key), "R11", "影响链 id 不在本单元哲学家内：%s" % r2["id"])

    # ---- 概念
    terms = {}
    for c in co:
        cid = c.get("id", "")
        where = "%s / %s" % (fname, cid or "?")
        check_id(where, c)
        if cid in global_ids:
            err(where, "R9", "概念 id 全局重复：%s" % cid)
        global_ids.add(cid)
        unit_concept_ids.add(cid)
        term = c.get("term", "")
        if term in terms:
            err(where, "R5", "同一单元内概念重名：%s" % term)
        terms[term] = cid
        need(where, "R1", c, ["term", "definition", "usages", "example", "sources"],
             mins={"definition": 20})
        us = c.get("usages") or []
        if len(us) < 2:
            err(where, "R14", "概念至少有 2 位哲学家的用法，实际 %d" % len(us))
        seen_usage = []
        for u2 in us:
            need("%s / usage" % where, "R1", u2, ["name", "usage"], mins={"usage": 15})
            if u2.get("id") and u2["id"] not in unit_ph_ids:
                err("%s / usage" % where, "R11", "usage.id 不在本单元哲学家内：%s" % u2["id"])
            if not u2.get("id"):
                warn("%s / usage" % where, "R11", "用法未关联本单元哲学家 id：%s" % u2.get("name"))
            seen_usage.append((u2.get("usage") or "").strip())
        if len(us) >= 2 and len(set(seen_usage)) < len(seen_usage):
            err(where, "R14", "不同哲学家的用法说明重复（未体现差异）")
        ex = c.get("example") or {}
        need("%s / example" % where, "R1", ex, ["text", "figure"],
             mins={"text": 20})
        for r3 in c.get("related") or []:
            if r3 not in all_co:
                err("%s / related" % where, "R11", "相关概念不在本单元概念内：%s" % r3)
        check_sources(where, c, src)
        check_pending(where, c)

    # ---- 争论
    dnames = set()
    for d in db:
        did = d.get("id", "")
        where = "%s / %s" % (fname, did or "?")
        check_id(where, d)
        if did in global_ids:
            err(where, "R9", "争论 id 全局重复：%s" % did)
        global_ids.add(did)
        title = d.get("title", "")
        if title in dnames:
            err(where, "R5", "同一单元内争论重名：%s" % title)
        dnames.add(title)
        need(where, "R1", d, ["title", "question", "positions", "focus", "status", "status_note", "sources"],
             mins={"question": 8, "focus": 10, "status_note": 15})
        pos = d.get("positions") or []
        if len(pos) < 2:
            err(where, "R15", "争论至少 2 方立场，实际 %d" % len(pos))
        for p2 in pos:
            need("%s / position" % where, "R1", p2, ["holder", "stance", "reasons", "kind"],
                 mins={"stance": 2})
            check_kind("%s / position" % where, p2, "R13")
            if not isinstance(p2.get("reasons"), list) or len(p2["reasons"]) < 1:
                err("%s / position" % where, "R15", "每方立场至少 1 条理由")
            if p2.get("id") and p2["id"] not in unit_ph_ids:
                err("%s / position" % where, "R11", "position.id 不在本单元哲学家内：%s" % p2["id"])
        check_sources(where, d, src)
        check_pending(where, d)



# ------------------------------------------------------------------ 流派校验
def check_schools(src, unit_ids, global_ids):
    if not os.path.exists(SCHOOLS):
        warn("schools.json", "R13", "流派文件不存在，跳过")
        return
    try:
        with open(SCHOOLS, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:  # noqa: BLE001
        err("schools.json", "R1", "JSON 解析失败：%s" % e)
        return
    items = data.get("schools") or []
    if len(items) < 20:
        err("schools.json", "R13", "流派数量 %d 偏少（目标 ≥26）" % len(items))
    seen = set()
    for s in items:
        sid = s.get("id", "")
        where = "schools / %s" % sid
        check_id(where, s)
        if sid in seen:
            err(where, "R5", "流派 id 重复")
        seen.add(sid)
        global_ids.add(sid)
        need(where, "R1", s, ["name", "region", "era", "core_claims", "representatives",
                              "rise", "decline", "sources"],
             mins={"era": 4, "rise": 20, "decline": 20})
        if len(s.get("core_claims") or []) < 3:
            err(where, "R13", "core_claims 至少 3 条")
        if len(s.get("representatives") or []) < 2:
            err(where, "R13", "representatives 至少 2 位")
        if s.get("unit") and s["unit"] not in unit_ids:
            warn(where, "R11", "unit 指向不存在的单元：%s" % s["unit"])
        check_sources(where, s, src)
        check_pending(where, s)


# ------------------------------------------------------------------ 著作校验
def check_works(src, global_ids):
    """R17：经典著作页（新维度）"""
    if not os.path.exists(WORKS):
        return
    with open(WORKS, encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("works") or []
    if len(items) < 10:
        err("works.json", "R17", "著作条目 %d 偏少（目标 ≥10）" % len(items))
    seen = set()
    for w in items:
        wid = w.get("id", "")
        where = "works / %s" % wid
        check_id(where, w)
        if wid in seen:
            err(where, "R5", "著作 id 重复")
        seen.add(wid)
        global_ids.add(wid)
        need(where, "R17", w, ["title", "title_original", "tradition", "date_display",
                               "structure", "core_arguments", "key_points", "editions",
                               "related_people", "misreadings", "sources"],
             mins={"structure": 30, "date_display": 4})
        if w.get("tradition") not in ("china", "west"):
            err(where, "R17", "tradition 必须是 china / west")
        for k in ("core_arguments", "key_points", "editions", "related_people", "misreadings"):
            if not isinstance(w.get(k), list) or not w.get(k):
                err(where, "R17", "%s 必须是非空数组" % k)
        if len(w.get("core_arguments") or []) < 2:
            err(where, "R17", "core_arguments 至少 2 条")
        if len(w.get("key_points") or []) < 2:
            err(where, "R17", "key_points 至少 2 条")
        for kp in w.get("key_points") or []:
            need("%s / key_point" % where, "R17", kp, ["locator", "point"])
        for r in w.get("related_people") or []:
            if r not in global_ids:
                err("%s / related_people" % where, "R11", "人物 id 不存在：%s" % r)
        for m in w.get("misreadings") or []:
            need("%s / misreading" % where, "R17", m, ["claim", "why"], mins={"why": 10})
        check_sources(where, w, src)
        check_pending(where, w)

# ------------------------------------------------------------------ 比较视野
def check_comparative(src):
    """R18：中西比较文章"""
    if not os.path.exists(COMPARATIVE):
        return
    data = json.load(open(COMPARATIVE, encoding="utf-8"))
    items = data.get("essays") or []
    if len(items) < 2:
        err("comparative.json", "R18", "比较文章少于 2 篇")
    seen = set()
    for e in items:
        eid = e.get("id", "")
        where = "comparative / %s" % eid
        check_id(where, e)
        if eid in seen:
            err(where, "R5", "比较文章 id 重复")
        seen.add(eid)
        need(where, "R18", e, ["title", "question", "sections", "caveat", "sources"],
             mins={"question": 10, "caveat": 20})
        secs = e.get("sections") or []
        if len(secs) < 2:
            err(where, "R18", "sections 至少 2 节")
        for sec in secs:
            need("%s / section" % where, "R18", sec, ["heading", "text"], mins={"text": 80})
        check_sources(where, e, src)
        check_pending(where, e)

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="只校验单个单元文件")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    src = load_sources()
    if not os.path.exists(DATA):
        print("data/ 不存在")
        return 2
    files = [args.file] if args.file else sorted(
        glob.glob(os.path.join(DATA, "china", "*.json")) +
        glob.glob(os.path.join(DATA, "west", "*.json")))
    global_ids, unit_ids = set(), set()
    for p in files:
        check_unit(p, src, global_ids, unit_ids)
    if not args.file:
        check_schools(src, unit_ids, global_ids)
        check_works(src, global_ids)
        check_comparative(src)

    if not args.quiet:
        for w in warnings:
            print("WARN  " + w)
        for e in errors:
            print("ERROR " + e)

    print("\n单元文件：%d；来源：%d 条（verified %d）；错误 %d；警告 %d"
          % (len(files), len(src), sum(1 for s in src.values() if s["verified"]),
             len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
