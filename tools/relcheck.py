# -*- coding: utf-8 -*-
"""tools/relcheck.py —— 著作页"关联人物"的可靠性检查（D83）。

动机：第 387 轮发现《植物志》误挂留基伯 —— 这类错挂不会被 check.py 抓到，
因为 id 存在、字段齐全。本工具做两件事：
  1) 关联人物的**区域**与著作 tradition 不符者，若其姓名在著作正文（结构/论证/要点/误读）中**一次都未出现**，
     则判为"无据挂靠"（SUSPECT）。
  2) 同一著作中，关联人物姓名在正文完全未出现者，标为"提示"（INFO，数量多，不强制）。

输出：`RELCHECK.md`。用法：python tools/relcheck.py
"""
import json
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    people = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for p in d.get("philosophers", []):
            people[p["id"]] = dict(name=p["name"], region=d.get("region"))
    wj = json.load(open(os.path.join(ROOT, "data", "works.json"), encoding="utf-8"))
    return people, wj["works"]


def text_of(w):
    parts = [w.get("structure") or "", w.get("date_display") or ""]
    parts += [str(x) for x in (w.get("core_arguments") or [])]
    parts += [str(x.get("point", "")) for x in (w.get("key_points") or [])]
    parts += [str(x.get("claim", "")) + str(x.get("why", "")) for x in (w.get("misreadings") or [])]
    parts += [str(x) for x in (w.get("editions") or [])]
    parts.append(w.get("pending_notes") or "")
    return "\n".join(parts)


def main():
    people, works = load()
    suspect, info = [], 0
    for w in works:
        t = text_of(w)
        tr = w.get("tradition")
        for pid in w.get("related_people") or []:
            p = people.get(pid)
            if not p:
                continue
            mentioned = p["name"] in t
            if not mentioned:
                info += 1
            if tr and p["region"] and p["region"] != tr and not mentioned:
                suspect.append((w["id"], w["title"], tr, pid, p["name"], p["region"]))
    lines = ["# RELCHECK.md —— 著作页「关联人物」可靠性检查（工具生成，勿手改）", "",
             "规则（D83）：关联人物的区域与著作 `tradition` 不符、且其姓名在著作正文中**一次都未出现** → 判为 **SUSPECT（无据挂靠）**。",
             "第 387 轮的《植物志》误挂留基伯即此类。", "",
             "| 项 | 数 |", "|---|---|",
             "| 著作总数 | %d |" % len(works),
             "| 跨区域且正文未提及（SUSPECT） | **%d** |" % len(suspect),
             "| 任何未提及者（INFO） | %d |" % info, ""]
    if suspect:
        lines += ["## SUSPECT 明细", "", "| 著作 | 区域 | 人物 | 人物区域 |", "|---|---|---|---|"]
        for wid, title, tr, pid, name, reg in suspect:
            lines.append("| `%s` %s | %s | %s（`%s`） | %s |" % (wid, title, tr, name, pid, reg))
    else:
        lines += ["## SUSPECT 明细", "", "（无）"]
    edges = sum(len(w.get("related_people") or []) for w in works)
    out = os.path.join(ROOT, "RELCHECK.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("RELCHECK.md 已写：著作 %d；关联边 %d；SUSPECT %d；INFO %d" % (len(works), edges, len(suspect), info))


if __name__ == "__main__":
    main()
