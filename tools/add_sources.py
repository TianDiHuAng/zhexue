#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补充来源：为 Perseus 被反爬（403）的希腊罗马原典另找可核验的公有领域文本站，
并为近代哲学补几个可核验的英译本 PDF。核验标准同 build_sources.py。"""
import json
import os
import ssl
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

MIT = "Internet Classics Archive（MIT）"
EMT = "Early Modern Texts（J. Bennett 改编本）"

CANDIDATES = [
    # id, title, author, year, year_note, publisher, type, url, keyword, note
    ("mit-plato-republic", "Plato, Republic（Jowett 英译）", "Plato / Benjamin Jowett 译", -380,
     "约前 380 年成书；译本为 19 世纪公有领域英译", MIT, "原典",
     "https://classics.mit.edu/Plato/republic.html", "Republic",
     "分卷网页；卷七 514a 起为洞穴之喻"),
    ("mit-plato-apology", "Plato, Apology（Jowett 英译）", "Plato / Benjamin Jowett 译", -399,
     "记述前 399 年苏格拉底受审", MIT, "原典",
     "https://classics.mit.edu/Plato/apology.html", "Apology",
     "申辩全文；38a 为“未经省察的人生”一句"),
    ("mit-plato-phaedo", "Plato, Phaedo（Jowett 英译）", "Plato / Benjamin Jowett 译", -380,
     "约前 380 年；记苏格拉底之死与灵魂不朽论证", MIT, "原典",
     "https://classics.mit.edu/Plato/phaedo.html", "Phaedo",
     "灵魂不朽与理念论的经典文本"),
    ("mit-aristotle-nicomachean", "Aristotle, Nicomachean Ethics（Ross 英译）", "Aristotle / W. D. Ross 译", -340,
     "约前 340 年；Ross 译本为公有领域", MIT, "原典",
     "https://classics.mit.edu/Aristotle/nicomachaen.html", "Nicomachean",
     "十卷；德性与中道见卷二"),
    ("mit-aristotle-metaphysics", "Aristotle, Metaphysics（Ross 英译）", "Aristotle / W. D. Ross 译", -340,
     "约前 340 年；Ross 译本", MIT, "原典",
     "https://classics.mit.edu/Aristotle/metaphysics.html", "Metaphysics",
     "十四卷；Γ 卷论矛盾律，A 卷为早期哲学史"),
    ("mit-aristotle-politics", "Aristotle, Politics（Jowett 英译）", "Aristotle / Benjamin Jowett 译", -335,
     "约前 335 年；Jowett 译本", MIT, "原典",
     "https://classics.mit.edu/Aristotle/politics.html", "Politics",
     "I.2 1253a“人天生是政治的动物”"),
    ("mit-epictetus-discourses", "Epictetus, Discourses（Long 英译）", "Epictetus / George Long 译", 108,
     "约公元 108 年记录；Long 译本公有领域", MIT, "原典",
     "https://classics.mit.edu/Epictetus/discourses.html", "Epictetus",
     "斯多亚实践哲学；区分“在我之内/不在我之内”"),
    ("mit-marcus-aurelius", "Marcus Aurelius, Meditations（Long 英译）", "Marcus Aurelius / George Long 译", 180,
     "约 170—180 年写作；Long 译本", MIT, "原典",
     "https://classics.mit.edu/Antoninus/meditations.html", "Meditations",
     "斯多亚式的自我操练笔记"),
    ("emt-locke", "John Locke, An Essay Concerning Human Understanding（节译改编本）", "John Locke / J. Bennett 改编", 1690,
     "1690 年初版；此为现代英语节译，非学术定本", EMT, "原典",
     "https://www.earlymoderntexts.com/assets/pdfs/locke1690book1.pdf", "Locke",
     "白板说与观念来源见第一卷、第二卷"),
    ("emt-berkeley", "George Berkeley, A Treatise Concerning the Principles of Human Knowledge", "George Berkeley / J. Bennett 改编", 1710,
     "1710 年初版；现代英语改编本", EMT, "原典",
     "https://www.earlymoderntexts.com/assets/pdfs/berkeley1710.pdf", "Berkeley",
     "“存在即被感知”见第 1—3 节"),
    ("emt-leibniz", "G. W. Leibniz, Monadology", "G. W. Leibniz / J. Bennett 改编", 1714,
     "1714 年写成；现代英语改编本", EMT, "原典",
     "https://www.earlymoderntexts.com/assets/pdfs/leibniz1714a.pdf", "Leibniz",
     "单子论九十节"),
    ("emt-spinoza", "Benedict de Spinoza, Ethics（节译改编本）", "Spinoza / J. Bennett 改编", 1677,
     "1677 年遗著初版；现代英语节译", EMT, "原典",
     "https://www.earlymoderntexts.com/assets/pdfs/spinoza1677.pdf", "Spinoza",
     "第一部分论神、实体与样态"),
]


def fetch(url, timeout=25, tries=2):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8"}), timeout=timeout, context=CTX)
            ctype = r.headers.get("Content-Type", "")
            body = r.read(400000)
            return r.status, ctype, body
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "code", 0) or 0
            if code in (403, 429, 500, 502, 503) and i == 0:
                time.sleep(2.0)
                continue
            return code, "", b""
    return 0, "", b""


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    have = {s["id"] for s in data["sources"]}
    added = 0
    for sid, title, author, year, ynote, pub, typ, url, kw, note in CANDIDATES:
        if sid in have:
            print("skip", sid)
            continue
        code, ctype, body = fetch(url)
        text = body.decode("utf-8", "ignore")
        ok = code == 200 and (kw.lower() in text.lower() or
                              ("pdf" in ctype.lower() and len(body) > 50000))
        rec = {
            "id": sid, "title": title, "author": author, "year": year,
            "year_note": ynote, "publisher": pub, "type": typ,
            "url": url, "url2": None, "link_ok": True if ok else ("blocked" if code in (401, 403, 429) else False),
            "verified": bool(ok), "note": note, "unit_hint": "",
            "verify": {"method": "http-page", "http_status": code,
                       "checked_at": time.strftime("%Y-%m-%d"),
                       "keyword": kw, "keyword_seen": bool(ok),
                       "content_type": ctype[:40]},
        }
        data["sources"].append(rec)
        print("%-5s %-34s %s" % (code, sid, "verified" if ok else "FAILED"), flush=True)
        added += 1
        time.sleep(0.6)

    order = {"原典": 0, "百科": 1, "学术著作": 2, "论文": 3}
    data["sources"].sort(key=lambda r: (order.get(r["type"], 9), r["id"]))
    for i, r in enumerate(data["sources"], 1):
        r["n"] = i
    data["meta"]["total"] = len(data["sources"])
    data["meta"]["verified"] = sum(1 for s in data["sources"] if s["verified"])
    data["meta"]["by_type"] = {t: sum(1 for s in data["sources"] if s["type"] == t) for t in order}
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n新增候选 %d；总计 %d，verified %d"
          % (added, data["meta"]["total"], data["meta"]["verified"]))


if __name__ == "__main__":
    main()
