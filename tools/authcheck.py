# -*- coding: utf-8 -*-
"""tools/authcheck.py —— 「著作页有没有挂上作者本人」检查（D84）。

动机：第 405—406 轮发现《史记》没挂司马迁、《神灭论》没挂范缜、《明句论》没挂月称……
一部书连作者都不在 `related_people` 里，却挂着三个"相关人物"——这是关系的错位，
而 `check.py`、`dupcheck.py`、`relcheck.py` 都抓不到。

做法：取每位哲学家 `works` 字段里提到的《…》书名，去比对著作页的 `related_people`，
若该作者不在其中，即列为 **CANDIDATE**。

**关键：CANDIDATE 不等于错误。** 大量候选是"同名异书"（徐幹《中论》vs 龙树《中论》），
所以本工具只列清单，**判断仍须人工**，判断结果记入 `AUTHCHECK.md` 的"已判定"栏。

输出：`AUTHCHECK.md`。用法：python tools/authcheck.py
"""
import json
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 已人工判定为「同名异书，不是漏挂」的条目（(person_id, work_id)）
KNOWN_HOMONYM = {
    ("cn-lianghan-zheng-xuan", "work-zhouyi-zhu-wangbi"),
    ("cn-lianghan-xu-gan", "work-madhyamaka-karika"),
    ("cn-songming-wang-anshi", "work-laozi-zhu-wangbi"),
    ("cn-nanbei-hu-anguo", "work-shangcai-yulu"),
    ("gr-ancient-thales", "work-metaphysics"),
    ("gr-19c-spencer", "work-principia-ethica"),
    ("gr-20c-moore", "work-investigations"),
    ("gr-ancient-theophrastus", "work-metaphysics"),
    ("gr-ancient-theophrastus", "work-renwuzhi"),
    ("gr-hellenistic-iamblichus", "work-theologia-scholastica"),
    ("gr-medieval-buridan", "work-de-anima"),
    ("gr-medieval-buridan", "work-summa-logicae-ockham"),
    ("gr-medieval-albert", "work-summa"),
    ("gr-medieval-al-ghazali", "work-guide-perplexed"),
    ("in-india-ramanuja", "work-brahma-sutra-bhasya"),
    ("in-india-philoponus", "work-de-anima"),
    ("gr-hellenistic-philoponus", "work-de-anima"),
    ("gr-medieval-philoponus", "work-de-anima"),
    ("gr-modern-erasmus", "work-de-libero-arbitrio"),
    ("gr-modern-newton", "work-epistola-tolerentia"),
    ("gr-medieval-avicenna", "work-de-anima"),
    ("gr-modern-more", "work-utopia" ),
}


def main():
    works = json.load(open(os.path.join(ROOT, "data", "works.json"), encoding="utf-8"))["works"]
    by_title = {}
    for w in works:
        by_title.setdefault(w["title"], []).append(w)
    people = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for p in d.get("philosophers", []):
            people[p["id"]] = p

    cand, homonym, fixed = [], [], 0
    for pid, p in people.items():
        for it in p.get("works") or []:
            title = it if isinstance(it, str) else it.get("title", "")
            for m in re.findall(r"《[^》]+》", title):
                for w in by_title.get(m, []):
                    if pid in (w.get("related_people") or []):
                        continue
                    if (pid, w["id"]) in KNOWN_HOMONYM:
                        homonym.append((pid, p["name"], m, w["id"]))
                    else:
                        cand.append((pid, p["name"], m, w["id"]))
    lines = ["# AUTHCHECK.md —— 「著作页有没有挂上作者本人」检查（工具生成，勿手改）", "",
             "规则（D84）：取人物 `works` 里的书名，比对著作页 `related_people`；作者不在其中即列为 **CANDIDATE**。",
             "**CANDIDATE ≠ 错误**：需人工判断是否为同名异书。第 405—406 轮已修 21 处真漏挂。", "",
             "| 项 | 数 |", "|---|---|",
             "| 著作 | %d |" % len(works),
             "| 哲学家人数 | %d |" % len(people),
             "| **CANDIDATE（待人工判断）** | **%d** |" % len(cand),
             "| 已判定为同名异书 | %d |" % len(homonym), ""]
    if cand:
        lines += ["## CANDIDATE 明细（须人工判断）", "", "| 人物 | 书名 | 著作页 id |", "|---|---|---|"]
        for pid, name, t, wid in cand:
            lines.append("| %s（`%s`） | %s | `%s` |" % (name, pid, t, wid))
    else:
        lines += ["## CANDIDATE 明细", "", "（无）"]
    open(os.path.join(ROOT, "AUTHCHECK.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("AUTHCHECK.md 已写：著作 %d；CANDIDATE %d；已判同名异书 %d" % (len(works), len(cand), len(homonym)))


if __name__ == "__main__":
    main()
