#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""自主模式的状态文件生成器：从 data/ 与 sources.json 算出 coverage.json，
并把本轮统计追加到 METRICS.json。每次循环的 G 步运行。"""
import datetime
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
COV = os.path.join(ROOT, "coverage.json")
MET = os.path.join(ROOT, "METRICS.json")


def main():
    units = []
    for f in sorted(glob.glob(os.path.join(DATA, "*", "*.json"))):
        u = json.load(open(f, encoding="utf-8"))
        if isinstance(u, dict) and "unit_id" in u:
            units.append(u)
    works = json.load(open(os.path.join(DATA, "works.json"), encoding="utf-8"))["works"]
    essays = json.load(open(os.path.join(DATA, "comparative.json"), encoding="utf-8"))["essays"]
    schools = json.load(open(os.path.join(DATA, "schools.json"), encoding="utf-8"))["schools"]
    src = json.load(open(os.path.join(ROOT, "sources.json"), encoding="utf-8"))["sources"]
    srcmap = {s["id"]: s for s in src}

    today = datetime.date.today().isoformat()
    entries = []

    def add(kind, e, container, title=None, need_n=2):
        eid = e["id"]
        title = title or e.get("name") or e.get("title") or e.get("term") or eid
        ids = e.get("sources") or []
        ver = sum(1 for i in ids if srcmap.get(i, {}).get("verified"))
        nv = bool(e.get("needs_verification"))
        # L2 = 双源且已验证且无待核实；L1 = 有条目但来源不足或待核实
        level = "L2" if (len(set(ids)) >= need_n and ver >= need_n and not nv) else "L1"
        entries.append({"id": eid, "type": kind, "title": title, "container": container,
                        "level": level, "sources": len(set(ids)), "verified_sources": ver,
                        "needs_verification": nv, "updated": today})

    for u in units:
        for p in u["philosophers"]:
            add("philosopher", p, u["unit_id"])
        for c in u["concepts"]:
            add("concept", c, u["unit_id"])
        for d in u["debates"]:
            add("debate", d, u["unit_id"])
    for w in works:
        add("work", w, w.get("tradition", ""))
    for e in essays:
        add("comparative", e, "comparative")
    for s in schools:
        add("school", s, s.get("unit") or "")

    by_level = {}
    for e in entries:
        by_level[e["level"]] = by_level.get(e["level"], 0) + 1
    cov = {"generated": today,
           "totals": {"entries": len(entries), "by_level": by_level,
                      "needs_verification": sum(1 for e in entries if e["needs_verification"]),
                      "sources": len(src), "sources_verified": sum(1 for s in src if s["verified"])},
           "units": [{"unit_id": u["unit_id"], "title": u["title"], "region": u["region"],
                      "philosophers": len(u["philosophers"]), "concepts": len(u["concepts"]),
                      "debates": len(u["debates"]),
                      "philosophers_slot": "8 上限，余 %d" % (8 - len(u["philosophers"]))}
                     for u in units],
           "entries": entries}
    json.dump(cov, open(COV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    metrics = []
    if os.path.exists(MET):
        metrics = json.load(open(MET, encoding="utf-8"))
    metrics.append({"date": today, "entries": len(entries), "by_level": by_level,
                    "needs_verification": cov["totals"]["needs_verification"],
                    "sources": len(src), "sources_verified": cov["totals"]["sources_verified"]})
    json.dump(metrics, open(MET, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(cov["totals"], ensure_ascii=False))
    for u in cov["units"]:
        print("%-16s phil=%d conc=%d deb=%d  %s" % (u["unit_id"], u["philosophers"], u["concepts"],
                                                    u["debates"], u["philosophers_slot"]))


if __name__ == "__main__":
    main()
