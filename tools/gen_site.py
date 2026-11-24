#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段 4：静态站点生成器 —— JSON 数据 → site/ 纯 HTML（零 JS、可离线）。

页面类型：
  首页 / 区域概览×2 / 单元页×N / 哲学家页×N / 概念页×N / 争论页×N / 流派页×N
  中国时间线 / 西方时间线 / 哲学家索引 / 概念索引 / 争论索引 / 流派索引
  思想谱系总图（纯 SVG）/ 来源列表 / 方法与体例
"""
import glob
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "sources.json")
SCHOOLS = os.path.join(DATA, "schools.json")
WORKS = os.path.join(DATA, "works.json")
COMPARATIVE = os.path.join(DATA, "comparative.json")

WORKS_CACHE = []
BRAND = "镜花水月"
SUBBRAND = "中外哲学思想脉络库"
VERSION = "v1.0"


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def rel(depth):
    return "../" * depth


NAV = [
    ("首页", ""), ("中国", "china/"), ("西方", "west/"),
    ("中国时间线", "timeline/china.html"), ("西方时间线", "timeline/west.html"),
    ("哲学家", "people/"), ("概念索引", "concepts/"), ("争论", "debates/"),
    ("流派", "schools/"), ("著作", "works/"), ("比较视野", "comparative.html"), ("误读索引", "misreadings.html"),
    ("谱系总图", "graph.html"), ("来源", "sources/"),
    ("体例", "about.html"),
]


def head(title, depth, extra=""):
    p = rel(depth)
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta name=\"color-scheme\" content=\"light dark\">\n"
        "<meta name=\"theme-color\" content=\"#1a2f45\">\n"
        "<title>%s · %s</title>\n"
        "<link rel=\"stylesheet\" href=\"%sassets/style.css\">\n%s</head>\n<body>\n"
        % (esc(title), BRAND, p, extra)
    )


def header(depth, current=""):
    p = rel(depth)
    links = []
    for name, path in NAV:
        cls = " class=\"on\"" if name == current else ""
        links.append("<a href=\"%s%s\"%s>%s</a>" % (p, path, cls, name))
    return (
        "<header class=\"site\"><span class=\"brand\"><a href=\"%s\">%s"
        "<span class=\"brand-sub\">%s</span></a></span>\n<nav>%s</nav></header>\n"
        % (p, BRAND, SUBBRAND, " · ".join(links))
    )


def footer(depth):
    return (
        "<footer class=\"site\"><span class=\"footer-brand\">%s</span> · %s %s · "
        "静态资料库，供学习参考，不构成学术结论；引用请核对原始文献与版本页码。</footer>\n"
        "</body>\n</html>\n" % (BRAND, SUBBRAND, VERSION)
    )


def page(title, depth, current, body, extra_head=""):
    return head(title, depth, extra_head) + header(depth, current) + "<main>\n" + body + "\n</main>\n" + footer(depth)


def src_line(s):
    """来源单行：作者《标题》，出版者 年份 · 类型 · 核验状态"""
    bits = []
    if s.get("author"):
        bits.append(esc(s["author"]))
    bits.append("《%s》" % esc(s["title"]) if not str(s["title"]).startswith(("《", "Plato", "Aristotle")) else esc(s["title"]))
    if s.get("publisher"):
        bits.append(esc(s["publisher"]))
    if s.get("year") is not None:
        bits.append(("%d" % s["year"]) if s["year"] > 0 else ("前%d" % -s["year"]))
    return "，".join(bits)


def link_state(s):
    if s.get("url") is None:
        return '<span class="blk">离线文献</span>'
    v = s.get("verify") or {}
    if s.get("verified"):
        return '<span class="ok">已打开核对（HTTP %s）</span>' % v.get("http_status", "200")
    if s.get("link_ok") == "blocked":
        return '<span class="blk">链接可达但反爬拦截（未作已验证来源）</span>'
    return '<span class="bad">未通过核验</span>'


def kind_tag(kind):
    if kind == "原文":
        return '<span class="tag yuanwen">原文</span>'
    if kind == "后人解读":
        return '<span class="tag houshu">后人解读</span>'
    return ""


def pending_box(obj):
    if obj.get("needs_verification"):
        return ('<div class="pending"><p><b>待核实</b>　本页含尚需进一步核对的内容，'
                '相关判断请以原典与专业研究为准。</p><p>%s</p></div>' % esc(obj.get("pending_notes", "")))
    return '<div class="pending"><p>无特别待核实事项（关键事实已由两个独立来源互相印证）。</p></div>'


def src_block(ids, sources, note=""):
    out = []
    for i in ids or []:
        s = sources.get(i)
        if not s:
            continue
        link = ""
        if s.get("url"):
            link = '　<a href="%s" rel="noopener">原文/页面</a>' % esc(s["url"])
        out.append("<li>%s　<span class=\"tag\">%s</span>%s<br><span class=\"meta\">%s</span></li>"
                   % (src_line(s), esc(s.get("type", "")), link, esc(s.get("note", ""))))
    if not out:
        return ""
    return '<ul class="src-list">%s</ul>' % "".join(out)


# ------------------------------------------------------------------ 载入
def load_all():
    units = []
    for region in ("china", "west"):
        for p in sorted(glob.glob(os.path.join(DATA, region, "*.json"))):
            with open(p, encoding="utf-8") as f:
                u = json.load(f)
            u["_path"] = p
            units.append(u)
    units.sort(key=lambda u: (0 if u["region"] == "china" else 1, u["start_year"]))
    with open(SRC, encoding="utf-8") as f:
        sources = {s["id"]: s for s in json.load(f)["sources"]}
    works = []
    if os.path.exists(WORKS):
        with open(WORKS, encoding="utf-8") as f:
            works = json.load(f).get("works", [])
    essays = []
    if os.path.exists(COMPARATIVE):
        with open(COMPARATIVE, encoding="utf-8") as f:
            essays = json.load(f).get("essays", [])
    schools = []
    if os.path.exists(SCHOOLS):
        with open(SCHOOLS, encoding="utf-8") as f:
            schools = json.load(f).get("schools", [])
    return units, sources, schools, works, essays


def index_units(units):
    people, concepts, debates = {}, {}, {}
    for u in units:
        for p in u.get("philosophers", []):
            p["_unit"] = u["unit_id"]
            p["_unit_title"] = u["title"]
            p["_region"] = u["region"]
            people[p["id"]] = p
        for c in u.get("concepts", []):
            c["_unit"] = u["unit_id"]
            c["_unit_title"] = u["title"]
            c["_region"] = u["region"]
            concepts[c["id"]] = c
        for d in u.get("debates", []):
            d["_unit"] = u["unit_id"]
            d["_unit_title"] = u["title"]
            d["_region"] = u["region"]
            debates[d["id"]] = d
    return people, concepts, debates


# ------------------------------------------------------------------ 哲学家页
def render_person(p, sources, people, concepts, debates, schools):
    d = 1
    pth = rel(d)
    u = p["_unit"]
    body = []
    body.append("<h1>%s <span class=\"meta\">%s</span></h1>" % (esc(p["name"]), esc(p.get("latin", ""))))
    body.append('<p class="crumb"><a href="%s">首页</a> / <a href="%s%s/">%s</a> / '
                '<a href="%s%s/%s/">%s</a> / 哲学家</p>'
                % (pth, pth, "china" if p["_region"] == "china" else "west",
                   "中国" if p["_region"] == "china" else "西方",
                   pth, "china" if p["_region"] == "china" else "west", u, esc(p["_unit_title"])))

    # 一
    body.append("<h2>一、生卒年与时代背景</h2>")
    sch = next((s for s in schools if s["name"] == p.get("school")), None)
    schl = ('<a href="%sschools/%s.html">%s</a>' % (pth, sch["id"], esc(sch["name"]))
            if sch else esc(p.get("school", "")))
    body.append('<table><tr><th style="width:110px">生年</th><td>%s<span class="meta">（%s）</span></td></tr>'
                '<tr><th>卒年</th><td>%s<span class="meta">（%s）</span></td></tr>'
                '<tr><th>所属流派</th><td>%s</td></tr>'
                '<tr><th>所在时期</th><td><a href="%s%s/%s/">%s</a></td></tr></table>'
                % (esc(p["birth_display"]), esc(p.get("birth_note", "")),
                   esc(p["death_display"]), esc(p.get("death_note", "")),
                   schl, pth, "china" if p["_region"] == "china" else "west", u, esc(p["_unit_title"])))
    body.append("<p>%s</p>" % esc(p.get("era", "")))

    # 二
    body.append("<h2>二、他要回答的核心问题</h2>")
    body.append("<ol class=\"tight\">%s</ol>" % "".join(
        "<li>%s</li>" % esc(q) for q in p.get("core_questions", [])))

    # 三
    body.append("<h2>三、主要论点（前提→推理→结论）</h2>")
    body.append('<p class="meta">每条论点按“前提→推理→结论”展开；右上角标签标明该表述属于<b>原文明确说了什么</b>'
                '还是<b>后人如何解读</b>。</p>')
    for i, a in enumerate(p.get("arguments", []), 1):
        body.append('<div class="arg"><h3>%d. %s %s</h3>' % (i, esc(a["claim"]), kind_tag(a.get("kind"))))
        body.append("<p><span class=\"step\">前提</span></p><ul class=\"tight\">%s</ul>"
                    % "".join("<li>%s</li>" % esc(x) for x in a.get("premises", [])))
        body.append("<p><span class=\"step\">推理</span>　%s</p>" % esc(a.get("inference", "")))
        body.append("<p><span class=\"step\">结论</span>　%s</p></div>" % esc(a.get("conclusion", "")))

    # 三之二：学说体系详述
    doc = p.get("doctrine")
    if doc:
        body.append('<h2>三之二、学说体系详述</h2>')
        if doc.get("auto"):
            body.append('<p class="meta">（本节由本页论点、著作与批评条目汇编而成，便于通读；'
                        '每一论点的前提与推理见第三节。）</p>')
        if doc.get("summary"):
            body.append("<p>%s</p>" % esc(doc["summary"]))
        if doc.get("system"):
            body.append("<h3>学说的几个支柱</h3><ul class=\"tight\">%s</ul>" % "".join(
                "<li><b>%s</b>：%s</li>" % (esc(x.get("name", "")), esc(x.get("content", "")))
                for x in doc["system"]))
        if doc.get("phases"):
            body.append("<h3>思想分期与转变</h3><ul class=\"tight\">%s</ul>" % "".join(
                "<li><b>%s</b>　%s</li>" % (esc(x.get("period", "")), esc(x.get("change", "")))
                for x in doc["phases"]))
        if doc.get("reception"):
            body.append('<h3>接受史与评价</h3><p>%s</p>' % esc(doc["reception"]))

    # 四
    body.append("<h2>四、代表著作及推荐阅读版本</h2>")
    rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                   % (esc(w["title"]), esc(w["edition"]), esc(w.get("note", "")))
                   for w in p.get("works", []))
    body.append('<table><tr><th>著作</th><th>推荐版本</th><th>说明</th></tr>%s</table>' % rows)
    wd = p.get("works_detail")
    if wd:
        body.append('<h3>著作详录</h3>')
        for x in wd:
            body.append('<div class="card"><p><b>%s</b>%s</p>'
                        '<p><b>成书/出版：</b>%s</p>'
                        '<p><b>结构：</b>%s</p>'
                        '<p><b>核心论旨：</b>%s</p>'
                        '<p><b>推荐版本：</b>%s</p>%s</div>'
                        % (esc(x.get("title", "")),
                           ('　<span class="meta">%s</span>' % esc(x.get("year", ""))) if x.get("year") else "",
                           esc(x.get("date", "")), esc(x.get("structure", "")),
                           esc(x.get("core_thesis", "")), esc(x.get("editions", "")),
                           ('<p class="meta">%s</p>' % esc(x["note"])) if x.get("note") else ""))
    mine = [w for w in WORKS_CACHE if p["id"] in (w.get("related_people") or [])]
    if mine:
        body.append('<p class="meta">本站著作页：%s</p>' % " · ".join(
            '<a href="%sworks/%s.html">%s</a>' % (pth, w["id"], esc(w["title"])) for w in mine))

    # 五
    body.append("<h2>五、受谁影响、影响了谁</h2>")
    def reflist(items, empty):
        if not items:
            return '<p class="meta">%s</p>' % empty
        out = []
        for r in items:
            nm = esc(r["name"])
            if r.get("id") and r["id"] in people:
                nm = '<a href="%speople/%s.html">%s</a>' % (pth, r["id"], esc(r["name"]))
            out.append("<li>%s　<span class=\"meta\">%s</span></li>" % (nm, esc(r.get("note", ""))))
        return '<ul class="tight">%s</ul>' % "".join(out)
    body.append('<div class="grid"><div class="card"><h3>受谁影响</h3>%s</div>'
                '<div class="card"><h3>影响了谁</h3>%s</div></div>'
                % (reflist(p.get("influenced_by"), "无明确可考的师承（或史料不足）。"),
                   reflist(p.get("influenced"), "无明确可考的直接传人。")))

    # 六
    body.append("<h2>六、主要批评与回应</h2>")
    for c in p.get("criticisms", []):
        body.append('<div class="card"><p><b>批评者：%s</b> %s</p><p><b>批评：</b>%s</p>'
                    '<p><b>（被批评方的）回应：</b>%s</p>%s</div>'
                    % (esc(c["critic"]), kind_tag(c.get("kind")), esc(c["view"]),
                       esc(c["response"]), src_block(c.get("sources"), sources)))

    # 七
    body.append("<h2>七、常见误解</h2>")
    for m in p.get("misconceptions", []):
        body.append('<div class="card"><p><b>常见说法：</b>%s</p><p><b>为什么容易误解：</b>%s</p></div>'
                    % (esc(m["claim"]), esc(m["why"])))

    # 八
    body.append("<h2>八、一图：论证结构 / 思想谱系</h2>")
    body.append('<figure>%s<figcaption>%s</figcaption></figure>'
                % (p.get("svg", ""), esc(p.get("svg_caption", "%s 的论证结构与思想谱系（示意图）" % p["name"]))))

    # 九
    body.append("<h2>九、待核实</h2>")
    body.append(pending_box(p))

    # 引文
    if p.get("quotes"):
        body.append("<h2>附：原文引文与出处</h2>")
        for q in p["quotes"]:
            body.append('<blockquote>%s<cite>—— %s，%s %s</cite></blockquote>'
                        % (esc(q["text"]), esc(q["locator"]),
                           esc(sources.get(q["source_id"], {}).get("title", "")), kind_tag(q.get("kind"))))

    body.append("<h2>参考来源</h2>")
    body.append(src_block(p.get("sources"), sources))

    # 相关概念 / 争论
    rel_c = [c for c in concepts.values() if p["id"] in
             [u2.get("id") for u2 in c.get("usages", [])]]
    if rel_c:
        body.append('<p class="meta">涉及概念：%s</p>' % " · ".join(
            '<a href="%sconcepts/%s.html">%s</a>' % (pth, c["id"], esc(c["term"])) for c in rel_c[:14]))
    rel_d = [x for x in debates.values() if p["id"] in
             [y.get("id") for y in x.get("positions", [])]]
    if rel_d:
        body.append('<p class="meta">参与争论：%s</p>' % " · ".join(
            '<a href="%sdebates/%s.html">%s</a>' % (pth, x["id"], esc(x["title"])) for x in rel_d))
    return page(p["name"], d, "", "\n".join(body))


# ------------------------------------------------------------------ 概念页
def render_concept(c, sources, people, concepts):
    d = 1
    pth = rel(d)
    body = ["<h1>%s <span class=\"meta\">%s</span></h1>" % (esc(c["term"]), esc(c.get("term_latin", "")))]
    body.append('<p class="crumb"><a href="%s">首页</a> / <a href="%s%s/">%s</a> / '
                '<a href="%s%s/%s/">%s</a> / 概念</p>'
                % (pth, pth, "china" if c["_region"] == "china" else "west",
                   "中国" if c["_region"] == "china" else "西方",
                   pth, "china" if c["_region"] == "china" else "west",
                   c["_unit"], esc(c["_unit_title"])))
    body.append("<h2>一、定义</h2><p>%s</p>" % esc(c["definition"]))
    body.append('<h2>二、在不同哲学家那里的用法差异</h2>')
    rows = []
    for u2 in c.get("usages", []):
        nm = esc(u2["name"])
        if u2.get("id") and u2["id"] in people:
            nm = '<a href="%speople/%s.html">%s</a>' % (pth, u2["id"], esc(u2["name"]))
        rows.append("<tr><td>%s</td><td>%s</td></tr>" % (nm, esc(u2["usage"])))
    body.append("<table><tr><th style=\"width:26%%\">哲学家</th><th>这里的用法</th></tr>%s</table>" % "".join(rows))
    body.append("<h2>三、一个具体例子</h2>")
    ex = c.get("example", {})
    body.append('<blockquote>%s<cite>—— %s</cite></blockquote>' % (esc(ex.get("text", "")), esc(ex.get("figure", ""))))
    if ex.get("locator"):
        body.append('<p class="meta">出处/语境：%s</p>' % esc(ex["locator"]))
    body.append("<h2>四、相关概念</h2>")
    rel_ids = c.get("related") or []
    if rel_ids:
        links = []
        for r in rel_ids:
            tgt = concepts.get(r)
            label = tgt["term"] if tgt else r
            links.append('<a href="%sconcepts/%s.html">%s</a>' % (pth, r, esc(label)))
        body.append('<p>%s</p>' % " · ".join(links))
    else:
        body.append('<p class="meta">暂无。</p>')
    body.append("<h2>待核实</h2>" + pending_box(c))
    body.append("<h2>参考来源</h2>" + src_block(c.get("sources"), sources))
    return page(c["term"], d, "概念索引", "\n".join(body))


# ------------------------------------------------------------------ 争论页
def render_debate(x, sources, people):
    d = 1
    pth = rel(d)
    body = ["<h1>%s</h1>" % esc(x["title"])]
    body.append('<p class="crumb"><a href="%s">首页</a> / <a href="%s%s/">%s</a> / '
                '<a href="%s%s/%s/">%s</a> / 争论</p>'
                % (pth, pth, "china" if x["_region"] == "china" else "west",
                   "中国" if x["_region"] == "china" else "西方",
                   pth, "china" if x["_region"] == "china" else "west",
                   x["_unit"], esc(x["_unit_title"])))
    body.append("<h2>一、问题是什么</h2><p>%s</p>" % esc(x["question"]))
    body.append("<h2>二、各方立场及理由</h2>")
    for p2 in x.get("positions", []):
        nm = esc(p2["holder"])
        if p2.get("id") and p2["id"] in people:
            nm = '<a href="%speople/%s.html">%s</a>' % (pth, p2["id"], esc(p2["holder"]))
        body.append('<div class="card"><p><b>%s</b>　立场：%s %s</p><ul class="tight">%s</ul></div>'
                    % (nm, esc(p2["stance"]), kind_tag(p2.get("kind")),
                       "".join("<li>%s</li>" % esc(r) for r in p2.get("reasons", []))))
    body.append("<h2>三、争论的焦点</h2><p>%s</p>" % esc(x["focus"]))
    body.append("<h2>四、至今是否有定论</h2>")
    body.append('<p><b>%s</b>　%s</p>' % (esc(x["status"]), esc(x["status_note"])))
    body.append("<h2>待核实</h2>" + pending_box(x))
    body.append("<h2>参考来源</h2>" + src_block(x.get("sources"), sources))
    return page(x["title"], d, "争论", "\n".join(body))


# ------------------------------------------------------------------ 流派页
def render_school(s, sources, people):
    d = 1
    pth = rel(d)
    body = ["<h1>%s</h1>" % esc(s["name"])]
    body.append('<p class="crumb"><a href="%s">首页</a> / <a href="%s%s/">%s</a> / 流派</p>'
                % (pth, pth, "china" if s["region"] == "china" else "west",
                   "中国" if s["region"] == "china" else "西方"))
    body.append('<p class="meta">%s · %s</p>' % (esc(s["era"]), esc(s.get("region_label", ""))))
    body.append("<h2>一、核心主张</h2><ul class=\"tight\">%s</ul>"
                % "".join("<li>%s</li>" % esc(c) for c in s["core_claims"]))
    body.append("<h2>二、代表人物</h2>")
    reps = []
    for r in s["representatives"]:
        nm = esc(r["name"])
        if r.get("id") and r["id"] in people:
            nm = '<a href="%speople/%s.html">%s</a>' % (pth, r["id"], esc(r["name"]))
        reps.append("<tr><td>%s</td><td>%s</td></tr>" % (nm, esc(r.get("note", ""))))
    body.append("<table><tr><th style=\"width:26%%\">人物</th><th>说明</th></tr>%s</table>" % "".join(reps))
    body.append("<h2>三、兴起与衰落的原因</h2><p><b>兴起：</b>%s</p><p><b>衰落/转型：</b>%s</p>"
                % (esc(s["rise"]), esc(s["decline"])))
    body.append("<h2>四、常见误解</h2>")
    for m in s.get("misconceptions", []):
        body.append('<div class="card"><p><b>常见说法：</b>%s</p><p><b>纠正：</b>%s</p></div>'
                    % (esc(m["claim"]), esc(m["why"])))
    if not s.get("misconceptions"):
        body.append('<p class="meta">暂无。</p>')
    body.append("<h2>待核实</h2>" + pending_box(s))
    body.append("<h2>参考来源</h2>" + src_block(s.get("sources"), sources))
    return page(s["name"], d, "流派", "\n".join(body))


# ------------------------------------------------------------------ 单元页
def render_unit(u, sources, schools, prev, nxt):
    d = 2
    pth = rel(d)
    reg = "china" if u["region"] == "china" else "west"
    body = ["<h1>%s</h1>" % esc(u["title"]),
            '<p class="meta">%s · %s 位哲学家 · %s 个概念 · %s 场争论</p>'
            % (esc(u["period"]), len(u["philosophers"]), len(u["concepts"]), len(u["debates"]))]
    body.append('<p class="crumb"><a href="%s">首页</a> / <a href="%s%s/">%s</a> / %s</p>'
                % (pth, pth, reg, "中国" if reg == "china" else "西方", esc(u["title"])))
    body.append("<h2>一、线索</h2><p>%s</p>" % esc(u["summary"]))
    body.append("<ul class=\"tight\">%s</ul>" % "".join("<li>%s</li>" % esc(t) for t in u["threads"]))

    body.append("<h2>二、关键哲学家</h2>")
    rows = []
    for p in u["philosophers"]:
        rows.append('<tr><td class="year">%s—%s</td><td><a href="%speople/%s.html"><b>%s</b></a>'
                    '<span class="tag">%s</span></td><td>%s</td></tr>'
                    % (esc(p["birth_display"]), esc(p["death_display"]), pth, p["id"],
                       esc(p["name"]), esc(p.get("school", "")),
                       esc((p.get("core_questions") or [""])[0])))
    body.append('<table><tr><th class="year">生卒</th><th>人物</th>'
                '<th>核心问题</th></tr>%s</table>' % "".join(rows))

    body.append("<h2>三、核心概念</h2><div class=\"grid\">")
    for c in u["concepts"]:
        body.append('<div class="card"><h3><a href="%sconcepts/%s.html">%s</a></h3><p class="meta">%s</p></div>'
                    % (pth, c["id"], esc(c["term"]), esc(c["definition"][:70] + ("…" if len(c["definition"]) > 70 else ""))))
    body.append("</div>")

    body.append("<h2>四、重要争论</h2>")
    for x in u["debates"]:
        body.append('<div class="card"><h3><a href="%sdebates/%s.html">%s</a></h3>'
                    '<p>%s</p><p class="meta">%s</p></div>'
                    % (pth, x["id"], esc(x["title"]), esc(x["question"]), esc(x["status"])))

    rel_s = [s for s in schools if s.get("unit") == u["unit_id"]]
    if rel_s:
        body.append('<h2>五、相关流派</h2><p>%s</p>' % " · ".join(
            '<a href="%sschools/%s.html">%s</a>' % (pth, s["id"], esc(s["name"])) for s in rel_s))

    nav = []
    if prev:
        nav.append('<a href="%s%s/%s/">← %s</a>' % (pth, reg, prev["unit_id"], esc(prev["title"])))
    if nxt:
        nav.append('<a href="%s%s/%s/">%s →</a>' % (pth, reg, nxt["unit_id"], esc(nxt["title"])))
    if nav:
        body.append('<p class="meta" style="margin-top:34px">%s</p>' % "　·　".join(nav))
    return page(u["title"], d, "中国" if reg == "china" else "西方", "\n".join(body))


# ------------------------------------------------------------------ 著作页
def render_work(w, sources, people):
    d = 1
    pth = rel(d)
    body = ["<h1>%s</h1>" % esc(w["title"]),
            '<p class="meta">%s · %s</p>' % (esc(w["title_original"]), esc(w["date_display"]))]
    body.append('<p class="crumb"><a href="%s">首页</a> / <a href="%sworks/">著作</a> / %s</p>'
                % (pth, pth, esc(w["title"])))
    body.append("<h2>一、文本结构</h2><p>%s</p>" % esc(w["structure"]))
    body.append("<h2>二、核心论证</h2><ol class=\"tight\">%s</ol>"
                % "".join("<li>%s</li>" % esc(a) for a in w["core_arguments"]))
    body.append("<h2>三、关键段落</h2><table><tr><th>位置</th><th>要点</th></tr>%s</table>"
                % "".join("<tr><td class=\"year\">%s</td><td>%s</td></tr>"
                          % (esc(k["locator"]), esc(k["point"])) for k in w["key_points"]))
    body.append("<h2>四、版本与推荐阅读</h2><ul class=\"tight\">%s</ul>"
                % "".join("<li>%s</li>" % esc(e) for e in w["editions"]))
    body.append("<h2>五、相关人物</h2><p>%s</p>" % " · ".join(
        ('<a href="%speople/%s.html">%s</a>' % (pth, pid, esc(people[pid]["name"]))
         if pid in people else esc(pid)) for pid in w["related_people"]))
    body.append("<h2>六、常见误读</h2>")
    for m in w["misreadings"]:
        body.append('<div class="card"><p><b>常见说法：</b>%s</p><p><b>纠正：</b>%s</p></div>'
                    % (esc(m["claim"]), esc(m["why"])))
    body.append("<h2>待核实</h2>" + pending_box(w))
    body.append("<h2>参考来源</h2>" + src_block(w.get("sources"), sources))
    return page(w["title"], d, "著作", "\n".join(body))


def render_works_index(works):
    d = 1
    pth = rel(d)
    body = ["<h1>经典著作</h1>",
            '<p class="meta"><a href="timeline.html">→ 按年代浏览（著作年表）</a>　共 %d 部。每页给出文本结构、核心论证、关键段落、版本与常见误读；'
            '文本的分篇与作者问题在“待核实”中说明。</p>' % len(works)]
    for trad, label in (("china", "中国"), ("west", "西方")):
        body.append("<h2>%s</h2><div class=\"grid\">" % label)
        for w in [x for x in works if x["tradition"] == trad]:
            body.append('<div class="card"><h3><a href="%sworks/%s.html">%s</a></h3>'
                        '<p class="meta">%s</p><p>%s</p></div>'
                        % (pth, w["id"], esc(w["title"]), esc(w["date_display"]),
                           esc(w["structure"][:70] + ("…" if len(w["structure"]) > 70 else ""))))
        body.append("</div>")
    return page("经典著作", d, "著作", "\n".join(body))




# ------------------------------------------------------------------ 误读索引
def render_misreadings_index(people, works_list):
    d = 0
    pth = rel(d)
    rows = []
    n = 0
    for region, label in (("china", "中国"), ("west", "西方")):
        ps = [p for p in people.values() if p["_region"] == region]
        ws = [w for w in works_list if w["tradition"] == region]
        body_p = []
        for p in sorted(ps, key=lambda x: x["birth_year"]):
            for m in p.get("misconceptions", []) or []:
                n += 1
                body_p.append('<tr><td><a href="%speople/%s.html">%s</a></td><td>%s</td><td>%s</td></tr>'
                              % (pth, p["id"], esc(p["name"]), esc(m.get("claim", "")), esc(m.get("why", ""))))
        body_w = []
        for w in sorted(ws, key=lambda x: x.get("sort_year") or 0):
            for m in w.get("misreadings", []) or []:
                n += 1
                body_w.append('<tr><td><a href="%sworks/%s.html">%s</a></td><td>%s</td><td>%s</td></tr>'
                              % (pth, w["id"], esc(w["title"]), esc(m.get("claim", "")), esc(m.get("why", ""))))
        rows.append('<h2>%s · 人物</h2><table><tr><th class="year">人物</th><th>常被误认为</th><th>为什么不是</th></tr>%s</table>'
                    % (label, "".join(body_p)))
        rows.append('<h2>%s · 著作</h2><table><tr><th class="year">著作</th><th>常被误认为</th><th>为什么不是</th></tr>%s</table>'
                    % (label, "".join(body_w)))
    body = ["<h1>误读索引</h1>",
            '<p class="meta">共 %d 条。本站的招牌是“把常被说错的地方说清楚”：每一条都指明**什么说法不对**，'
            '以及**为什么不对**（原文如何、后人如何改写、语境如何被抽掉）。<br>'
            '收录范围：人物页的“常见误解”与著作页的“常见误读”。与“待核实”不同——'
            '这些是有把握的判断，不是存疑的推测。</p>' % n,
            "".join(rows)]
    return page("误读索引", d, "误读索引", "\n".join(body))


# ------------------------------------------------------------------ 比较视野
def render_comparative(essays, sources):
    d = 0
    pth = rel(d)
    body = ["<h1>比较视野</h1>",
            '<p class="meta">共 %d 篇。做法：并列两种提问方式与其论证结构，说明可比与不可比之处；'
            '不主张某一传统更“正确”，也不追求一个更高的统一表述。</p>' % len(essays)]
    body.append('<p class="meta">目录：%s</p>' % " · ".join(
        '<a href="#%s">%s</a>' % (e["id"], esc(e["title"])) for e in essays))
    for e in essays:
        body.append('<h2 id="%s">%s</h2>' % (e["id"], esc(e["title"])))
        body.append('<p class="kv"><b>问题：</b>%s</p>' % esc(e["question"]))
        for sec in e["sections"]:
            body.append("<h3>%s</h3><p>%s</p>" % (esc(sec["heading"]), esc(sec["text"])))
        body.append('<div class="pending"><p><b>比较的限度</b>　%s</p></div>' % esc(e["caveat"]))
        body.append("<h3>参考来源</h3>" + src_block(e.get("sources"), sources))
    return page("比较视野", d, "比较视野", "\n".join(body))


def render_works_timeline(works):
    d = 1
    pth = rel(d)
    ws = sorted(works, key=lambda w: w.get("sort_year") or 0)
    body = ["<h1>著作年表</h1>",
            '<p class="meta">按成书/出版年排序（公元前用“前”标注），共 %d 部。点书名进入著作页。</p>' % len(ws)]
    body.append('<div class="tl">')
    last = None
    for w in ws:
        y = w.get("sort_year") or 0
        era = "前" if y < 0 else ""
        yy = abs(y)
        cent = ("前%d世纪" % ((yy - 1) // 100 + 1)) if y < 0 else ("%d世纪" % (yy // 100 + 1))
        if cent != last:
            last = cent
            body.append('<p class="tl-item"><b>%s</b></p>' % cent)
        body.append('<p class="tl-item"><span class="tl-year">%s%s年</span>'
                    '<a href="%sworks/%s.html">%s</a>'
                    '<span class="meta">　%s · %s</span></p>'
                    % (era, yy, pth, w["id"], esc(w["title"]),
                       "中国" if w["tradition"] == "china" else "西方", esc(w["date_display"])))
    body.append("</div>")
    return page("著作年表", d, "著作", "\n".join(body))


# ------------------------------------------------------------------ 索引页
def render_people_index(people):
    d = 1
    pth = rel(d)
    items = sorted(people.values(), key=lambda p: (p["_region"] != "china", p["birth_year"]))
    rows = []
    for p in items:
        rows.append('<tr><td class="year">%s—%s</td><td><a href="%speople/%s.html">%s</a>'
                    '<span class="meta">　%s</span></td><td>%s</td><td>%s</td></tr>'
                    % (esc(p["birth_display"]), esc(p["death_display"]), pth, p["id"],
                       esc(p["name"]), esc(p.get("latin", "")), esc(p.get("school", "")),
                       esc(p["_unit_title"])))
    body = ["<h1>哲学家索引</h1>",
            '<p class="meta">共 %d 位，按“中国→西方”与该时期内的出生年排序。</p>' % len(items),
            '<table><tr><th class="year">生卒</th><th>姓名</th>'
            '<th>流派</th><th>时期</th></tr>%s</table>' % "".join(rows)]
    return page("哲学家索引", d, "哲学家", "\n".join(body))


def render_concept_index(concepts, units):
    d = 1
    pth = rel(d)
    body = ["<h1>概念索引</h1>",
            '<p class="meta">共 %d 个概念，按时期归组。每个概念页给出定义、不同哲学家那里的用法差异与一个具体例子。</p>'
            % len(concepts)]
    for region, label in (("china", "中国"), ("west", "西方")):
        body.append("<h2>%s</h2>" % label)
        for u in [x for x in units if x["region"] == region]:
            cs = [c for c in u["concepts"]]
            if not cs:
                continue
            body.append('<h3>%s <span class="meta">%s</span></h3>' % (esc(u["title"]), esc(u["period"])))
            body.append('<ul class="tight">%s</ul>' % "".join(
                '<li><a href="%sconcepts/%s.html">%s</a>　<span class="meta">%s</span></li>'
                % (pth, c["id"], esc(c["term"]), esc(c["definition"][:46] + ("…" if len(c["definition"]) > 46 else "")))
                for c in cs))
    return page("概念索引", d, "概念索引", "\n".join(body))


def render_debate_index(debates):
    d = 1
    pth = rel(d)
    items = sorted(debates.values(), key=lambda x: (x["_region"] != "china", x["_unit_title"]))
    rows = "".join('<tr><td><a href="%sdebates/%s.html">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>'
                   % (pth, x["id"], esc(x["title"]), esc(x["question"]), esc(x["_unit_title"]), esc(x["status"]))
                   for x in items)
    body = ["<h1>争论索引</h1>", '<p class="meta">共 %d 场争论。</p>' % len(items),
            '<table><tr><th>争论</th><th>问题</th>'
            '<th>时期</th><th>现状</th></tr>%s</table>' % rows]
    return page("争论索引", d, "争论", "\n".join(body))


def render_school_index(schools):
    d = 1
    pth = rel(d)
    body = ["<h1>流派索引</h1>", '<p class="meta">共 %d 个流派。</p>' % len(schools)]
    for region, label in (("china", "中国"), ("west", "西方")):
        body.append("<h2>%s</h2><div class=\"grid\">" % label)
        for s in [x for x in schools if x["region"] == region]:
            body.append('<div class="card"><h3><a href="%sschools/%s.html">%s</a></h3>'
                        '<p class="meta">%s</p><p>%s</p></div>'
                        % (pth, s["id"], esc(s["name"]), esc(s["era"]),
                           esc(s["core_claims"][0] if s["core_claims"] else "")))
        body.append("</div>")
    return page("流派索引", d, "流派", "\n".join(body))


def render_timeline(units, people, region, label):
    d = 1
    pth = rel(d)
    ps = sorted([p for p in people.values() if p["_region"] == region], key=lambda p: p["birth_year"])
    body = ["<h1>%s哲学时间线</h1>" % label,
            '<p class="meta">按出生年排序（公元前用“前”标注）。条目可点入哲学家页。</p>',
            '<div class="tl">']
    last_century = None
    for p in ps:
        c = int((p["birth_year"] // 100) * 100)
        if c != last_century:
            last_century = c
            body.append('<p class="tl-item"><b>%s</b></p>'
                        % (("前%d世纪" % (-c // 100 + 1)) if c < 0 else ("%d世纪" % (c // 100 + 1))))
        body.append('<p class="tl-item"><span class="tl-year">%s—%s</span>'
                    '<span class="tl-unit">%s · %s</span>'
                    '<a href="%speople/%s.html">%s</a>'
                    '<span class="meta">　%s</span></p>'
                    % (esc(p["birth_display"]), esc(p["death_display"]),
                       esc(p.get("school", "")), esc(p["_unit_title"]),
                       pth, p["id"], esc(p["name"]),
                       esc((p.get("core_questions") or [""])[0])))
    body.append("</div>")
    return page("%s哲学时间线" % label, d, "%s时间线" % label, "\n".join(body))


def render_sources(sources):
    d = 1
    body = ["<h1>来源列表</h1>",
            '<p class="meta">共 %d 条；其中已验证 %d 条。核验方式：脚本实际打开页面并要求正文含预期关键词'
            '（见 DECISIONS.md D8）。403/429 的站点记为“反爬拦截”，不作已验证来源。</p>'
            % (len(sources), sum(1 for s in sources.values() if s.get("verified")))]
    groups = {"原典": "一、原典（一手文本）", "百科": "二、权威百科",
              "学术著作": "三、学术著作", "论文": "四、论文"}
    for typ, label in groups.items():
        items = [s for s in sources.values() if s.get("type") == typ]
        if not items:
            continue
        body.append("<h2>%s（%d）</h2>" % (label, len(items)))
        rows = []
        for s in sorted(items, key=lambda x: x["id"]):
            link = ('<a href="%s" rel="noopener">%s</a>' % (esc(s["url"]), esc(s["url"][:56] + ("…" if len(s["url"]) > 56 else "")))
                    if s.get("url") else "—")
            rows.append("<tr><td class=\"year\">%s</td><td>%s<br><span class=\"meta\">%s</span></td>"
                        "<td>%s</td><td>%s</td></tr>"
                        % (("%d" % s["year"]) if s.get("year") is not None and s["year"] > 0
                           else ("前%d" % -s["year"] if s.get("year") is not None else "—"),
                           esc(s["title"]), esc(s.get("author", "")), link, link_state(s)))
        body.append('<table><tr><th class="year">年份</th><th>标题/作者</th>'
                    '<th>链接</th><th>核验</th></tr>%s</table>' % "".join(rows))
    return page("来源列表", d, "来源", "\n".join(body))


def render_about(units, people, concepts, debates, sources):
    d = 0
    body = ["<h1>方法与体例</h1>",
            "<p>本站是一个纯静态的中外哲学资料库：数据层是 JSON，页面由脚本确定性渲染，没有 JavaScript、"
            "不加载任何外部资源，可离线打开。</p>",
            "<h2>一、标注体系</h2>",
            "<p><span class=\"tag yuanwen\">原文</span> 表示这一说法在原典中有明确文本依据；"
            "<span class=\"tag houshu\">后人解读</span> 表示这是后代注疏、研究者或哲学史书写的解释框架。"
            "两者在每条论点、每条批评、每条引文上一律分开标注。</p>",
            "<h2>二、引文政策</h2>",
            "<ul class=\"tight\"><li>只使用能在原典中定位到具体篇目的引文；找不到出处的“名人名言”一概不用。</li>"
            "<li>单条引文不超过一两句，标明版本与篇目；不整段搬用有版权的现代译本。</li>"
            "<li>需要转述现代译本措辞时，写“大意是……”并标“后人解读”。</li></ul>",
            "<h2>三、双源与待核实</h2>",
            "<p>每条内容至少由两个独立来源互相印证；不足两源的条目必须标“待核实”并写明待核内容。"
            "所有来源在 <a href=\"%ssources/\">来源列表</a> 中给出核验状态。</p>" % rel(d),
            "<h2>四、争议的处理</h2>",
            "<p>对学界有实质分歧的问题（如《老子》成书年代、《坛经》作者、向秀/郭象《庄子注》著作权），"
            "页面并列各方说法及其依据，不替读者下结论，也不对任何流派作贬抑性表述。</p>",
            "<h2>五、五个入口</h2>",
            "<p><b>人</b>（哲学家页）、<b>概念</b>（概念页）、<b>争论</b>（争论页）、<b>流派</b>（流派页）、"
            "<b>文本</b>（著作页）五个入口互为索引；另有<b>比较视野</b>：并列中西两种提问方式及其论证结构，"
            "说明可比与不可比之处，不追求统一表述。</p>",
            "<h2>六、本站规模</h2>",
            "<table><tr><th>项目</th><th>数量</th></tr>"
            "<tr><td>时期单元</td><td>%d</td></tr><tr><td>哲学家</td><td>%d</td></tr>"
            "<tr><td>概念</td><td>%d</td></tr><tr><td>争论</td><td>%d</td></tr>"
            "<tr><td>来源</td><td>%d（已验证 %d）</td></tr></table>"
            % (len(units), len(people), len(concepts), len(debates), len(sources),
               sum(1 for s in sources.values() if s.get("verified"))),
            "<h2>七、免责</h2>",
            "<p>本站用于学习与索引，不构成学术结论。任何引用请回到原典与所标注的专业研究，"
            "并核对紙本版本的页码。</p>"]
    return page("方法与体例", d, "体例", "\n".join(body))


# ------------------------------------------------------------------ 谱系总图
def render_graph(units, people):
    d = 0
    W = 960
    rows = []
    legend_y = 0
    lanes = 6
    lane_h = 62
    blocks = []
    y_cursor = 70
    for region, label in (("china", "中国"), ("west", "西方")):
        ps = sorted([p for p in people.values() if p["_region"] == region], key=lambda p: p["birth_year"])
        if not ps:
            continue
        y0 = y_cursor
        H = lanes * lane_h + 40
        y_cursor += H + 40
        blocks.append((region, label, ps, y0, H))
    total_h = y_cursor + 30
    parts = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d'>" % (W, total_h),
             "<rect x='0' y='0' width='%d' height='%d' fill='#f0f5fa'/>" % (W, total_h),
             "<text x='%d' y='30' text-anchor='middle' font-size='20' fill='#1c3a5c'>"
             "思想谱系总图（按出生年排列，箭头表示影响方向）</text>" % (W // 2)]
    parts.append("<defs><marker id='ar' markerWidth='8' markerHeight='7' refX='7' refY='3.5' "
                 "orient='auto'><path d='M0,0 L8,3.5 L0,7 Z' fill='#4a7ba6'/></marker></defs>")
    for region, label, ps, y0, H in blocks:
        years = [p["birth_year"] for p in ps]
        lo, hi = min(years), max(years)
        span = max(1, hi - lo)
        left, right = 90, W - 40
        pos = {}
        for i, p in enumerate(ps):
            x = left + (p["birth_year"] - lo) / span * (right - left)
            lane = i % lanes
            y = y0 + 34 + lane * lane_h
            pos[p["id"]] = (x, y)
        parts.append("<text x='20' y='%d' font-size='15' font-weight='bold' fill='#1c3a5c'>%s</text>"
                     % (y0 + 18, label))
        parts.append("<line x1='%d' y1='%d' x2='%d' y2='%d' stroke='#c5d8e8' stroke-width='1'/>"
                     % (left, y0 + H - 14, right, y0 + H - 14))
        # 箭头（先画，压在文字下）
        for p in ps:
            for r in p.get("influenced", []) or []:
                tgt = r.get("id")
                if tgt in pos:
                    x1, y1 = pos[p["id"]]
                    x2, y2 = pos[tgt]
                    if x2 < x1:
                        x1, x2 = x2, x1
                        y1, y2 = y2, y1
                    parts.append("<line x1='%.0f' y1='%.0f' x2='%.0f' y2='%.0f' stroke='#4a7ba6' "
                                 "stroke-width='1' opacity='0.55' marker-end='url(#ar)'/>"
                                 % (x1 + 4, y1, x2 - 6, y2))
        for p in ps:
            x, y = pos[p["id"]]
            w = max(46, min(96, 15 + len(p["name"]) * 13))
            fill = "#dbe8f3" if region == "china" else "#dce8f4"
            parts.append("<rect x='%.0f' y='%.0f' width='%d' height='24' rx='4' fill='%s' "
                         "stroke='#1c3a5c' stroke-width='0.8'/>" % (x - w / 2, y - 12, w, fill))
            parts.append("<text x='%.0f' y='%.0f' text-anchor='middle' font-size='11' fill='#1e2d3d'>%s</text>"
                         % (x, y + 4, esc(p["name"])))
    parts.append("</svg>")
    body = ["<h1>思想谱系总图</h1>",
            '<p class="meta">横轴为出生年（同一区域内线性映射），纵向分道避免重叠；箭头由影响者指向被影响者，'
            '只绘制同一区域内有明确 id 关联的关系，跨区域与跨时期的间接影响见各哲学家页第五节。</p>',
            "<figure>%s<figcaption>中外哲学思想谱系总图（示意图，非精确年代刻度）</figcaption></figure>" % "".join(parts)]
    return page("思想谱系总图", d, "谱系总图", "\n".join(body))


# ------------------------------------------------------------------ 首页与区域页
def render_home(units, people, concepts, debates, schools, sources):
    d = 0
    body = ["<h1>中外哲学思想脉络库</h1>",
            "<p>按时期整理的哲学思想资料库：中国 6 个时期、西方 8 个时期；每位哲学家一页，"
            "按“生卒与时代—核心问题—论点（前提→推理→结论）—著作与版本—影响链—批评与回应—常见误解—一图—待核实”展开；"
            "另有概念页、争论页、流派页、双向时间线与思想谱系总图。</p>",
            '<div class="stat">'
            '<div class="card"><span class="n">%d</span><span class="l">时期单元</span></div>'
            '<div class="card"><span class="n">%d</span><span class="l">哲学家</span></div>'
            '<div class="card"><span class="n">%d</span><span class="l">核心概念</span></div>'
            '<div class="card"><span class="n">%d</span><span class="l">争论</span></div>'
            '<div class="card"><span class="n">%d</span><span class="l">流派</span></div>'
            '<div class="card"><span class="n">%d</span><span class="l">来源</span></div>'
            "</div>" % (len(units), len(people), len(concepts), len(debates), len(schools), len(sources))]
    for region, label, path in (("china", "中国哲学", "china/"), ("west", "西方哲学", "west/")):
        body.append('<h2>%s</h2><div class="grid">' % label)
        for u in [x for x in units if x["region"] == region]:
            body.append('<div class="card"><h3><a href="%s%s/">%s</a></h3>'
                        '<p class="meta">%s · 哲学家 %d · 概念 %d · 争论 %d</p><p>%s</p></div>'
                        % (path, u["unit_id"], esc(u["title"]), esc(u["period"]),
                           len(u["philosophers"]), len(u["concepts"]), len(u["debates"]),
                           esc(u["summary"][:88] + ("…" if len(u["summary"]) > 88 else ""))))
        body.append("</div>")
    body.append('<h2>另见</h2><p><a href="works/">经典著作</a> · <a href="comparative.html">比较视野</a> · <a href="timeline/china.html">中国哲学时间线</a> · '
                '<a href="timeline/west.html">西方哲学时间线</a> · <a href="graph.html">思想谱系总图</a> · '
                '<a href="concepts/">概念索引</a> · <a href="debates/">争论索引</a> · '
                '<a href="schools/">流派索引</a> · <a href="sources/">来源列表</a> · '
                '<a href="about.html">方法与体例</a></p>')
    body.append('<p class="meta" style="margin-top:34px">关键事实以两个独立来源互相印证为标准；未达标者在页内标注“待核实”。'
                '原文与后人解读逐条分标。</p>')
    return page("中外哲学思想脉络库", d, "首页", "\n".join(body))


def render_region(units, region, label):
    d = 1
    pth = rel(d)
    us = [u for u in units if u["region"] == region]
    body = ["<h1>%s（按时期）</h1>" % label,
            '<p class="meta">共 %d 个时期，%d 位哲学家。</p>'
            % (len(us), sum(len(u["philosophers"]) for u in us))]
    for u in us:
        body.append('<div class="card"><h3><a href="%s/">%s</a></h3>'
                    '<p class="meta">%s · 哲学家 %d · 概念 %d · 争论 %d</p><p>%s</p></div>'
                    % (u["unit_id"], esc(u["title"]), esc(u["period"]),
                       len(u["philosophers"]), len(u["concepts"]), len(u["debates"]),
                       esc(u["summary"])))
    return page(label, d, "中国" if region == "china" else "西方", "\n".join(body))


# ------------------------------------------------------------------ main
def write(relpath, content):
    path = os.path.join(SITE, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    global WORKS_CACHE
    units, sources, schools, works, essays = load_all()
    WORKS_CACHE = works
    people, concepts, debates = index_units(units)

    # 清理旧产物（保留 assets）
    for name in ("china", "west", "people", "concepts", "debates", "schools", "works", "timeline", "sources"):
        p = os.path.join(SITE, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
    for f in ("index.html", "about.html", "graph.html", "comparative.html"):
        p = os.path.join(SITE, f)
        if os.path.exists(p):
            os.remove(p)

    # GitHub Pages：禁用 Jekyll（站点是纯静态 HTML，不需要 Jekyll 处理）
    with open(os.path.join(SITE, ".nojekyll"), "w", encoding="utf-8") as fh:
        fh.write("")

    write("index.html", render_home(units, people, concepts, debates, schools, sources))
    write("about.html", render_about(units, people, concepts, debates, sources))
    write("graph.html", render_graph(units, people))

    for region, label in (("china", "中国"), ("west", "西方")):
        write("%s/index.html" % region, render_region(units, region, label))
        us = [u for u in units if u["region"] == region]
        for i, u in enumerate(us):
            prev = us[i - 1] if i > 0 else None
            nxt = us[i + 1] if i + 1 < len(us) else None
            write("%s/%s/index.html" % (region, u["unit_id"]), render_unit(u, sources, schools, prev, nxt))

    for p in people.values():
        write("people/%s.html" % p["id"], render_person(p, sources, people, concepts, debates, schools))
    for c in concepts.values():
        write("concepts/%s.html" % c["id"], render_concept(c, sources, people, concepts))
    for x in debates.values():
        write("debates/%s.html" % x["id"], render_debate(x, sources, people))
    for s in schools:
        write("schools/%s.html" % s["id"], render_school(s, sources, people))

    write("people/index.html", render_people_index(people))
    write("concepts/index.html", render_concept_index(concepts, units))
    write("debates/index.html", render_debate_index(debates))
    write("schools/index.html", render_school_index(schools))
    for w in works:
        write("works/%s.html" % w["id"], render_work(w, sources, people))
    write("works/index.html", render_works_index(works))
    write("works/timeline.html", render_works_timeline(works))
    write("comparative.html", render_comparative(essays, sources))
    write("misreadings.html", render_misreadings_index(people, works))
    write("timeline/china.html", render_timeline(units, people, "china", "中国"))
    write("timeline/west.html", render_timeline(units, people, "west", "西方"))
    write("sources/index.html", render_sources(sources))

    n = sum(1 for _ in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
    print("生成完成：%d 个 HTML 页面" % n)
    print("单元 %d / 哲学家 %d / 概念 %d / 争论 %d / 流派 %d / 来源 %d"
          % (len(units), len(people), len(concepts), len(debates), len(schools), len(sources)))


if __name__ == "__main__":
    main()
