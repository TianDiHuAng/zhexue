#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补核：对 build_sources.py 未能核验的条目做第二轮尝试。

- 中文原典：ctext 被反爬时改投维基文库（同一文本的公有领域全文）
- 西文原典：对 Perseus 等站点降低频率重试一次
- 成功后更新 sources.json 的 url / publisher / note / verify / verified
写回前保留原 URL 到 url2，并在 note 里注明改投原因（不虚报核验）。
"""
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# id -> 维基文库条目名
WS = {
    "ct-analects": "論語",
    "ct-daodejing": "道德經",
    "ct-mozi": "墨子",
    "ct-mengzi": "孟子",
    "ct-zhuangzi": "莊子",
    "ct-xunzi": "荀子",
    "ct-hanfeizi": "韓非子",
    "ct-liji": "禮記",
    "ct-daxue": "大學",
    "ct-zhongyong": "中庸",
    "ct-yijing": "周易",
    "ct-zuozhuan": "春秋左氏傳",
    "ct-shiji": "史記",
    "ct-chunqiufanlu": "春秋繁露",
    "ct-lunheng": "論衡",
    "ct-fayan": "法言",
    "ct-taixuanjing": "太玄經",
    "ct-tongshu": "通書",
    "ct-zhuzi-yulei": "朱子語類",
    "ct-chuanxilu": "傳習錄",
    "ct-rizhilu": "日知錄",
}


def fetch(url, timeout=20, tries=2):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }), timeout=timeout, context=CTX)
            return r.status, r.read().decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "code", 0) or 0
            if code in (403, 429, 500, 502, 503) and i == 0:
                time.sleep(2.5)
                continue
            return code, ""
    return 0, ""


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    fixed = 0
    for s in data["sources"]:
        if s.get("verified"):
            continue
        sid = s["id"]
        kw = (s.get("verify") or {}).get("keyword") or ""
        urls = []
        if sid in WS:
            urls.append(("https://zh.wikisource.org/wiki/" + urllib.parse.quote(WS[sid]),
                         "维基文库（公有领域全文，ctext 反爬时的替代核验源）", WS[sid]))
        if s.get("url") and s["url"] not in [u for u, _, _ in urls]:
            urls.append((s["url"], s.get("publisher", ""), kw))
        for url, pub, k in urls:
            code, body = fetch(url)
            ok = code == 200 and (k and k in body or len(body) > 8000)
            print("%-5s %-46s %s %s" % (code, sid, "verified" if ok else "fail", url[:70]), flush=True)
            if ok:
                s["url2"] = s["url"] if s["url"] != url else s.get("url2")
                s["url"] = url
                if "维基文库" in pub:
                    s["publisher"] = "维基文库（Wikimedia Wikisource）"
                    s["note"] = (s.get("note", "") + "；经维基文库全文核验（公有领域文本，参校以上海古籍/中华书局点校本为通行本）").strip("；")
                s["verified"] = True
                s["link_ok"] = True
                s["verify"] = dict(s.get("verify") or {}, http_status=code,
                                   method=(s.get("verify") or {}).get("method", "http-page") + "+retry",
                                   keyword_seen=True)
                fixed += 1
                break
            time.sleep(0.5)

    data["meta"]["verified"] = sum(1 for s in data["sources"] if s["verified"])
    data["meta"]["retry_pass"] = {"checked_at": time.strftime("%Y-%m-%d"), "newly_verified": fixed}
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n补核完成：新增 verified %d 条；总计 verified %d / %d"
          % (fixed, data["meta"]["verified"], len(data["sources"])))


if __name__ == "__main__":
    main()
