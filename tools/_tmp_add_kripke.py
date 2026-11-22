# -*- coding: utf-8 -*-
"""临时脚本：向 data/west/gr-contemp.json 追加克里普克（gr-contemp-kripke）。"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "west", "gr-contemp.json")

SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 760 400'>"
    "<rect x='0' y='0' width='760' height='400' fill='#f0f5fa'/>"
    "<text x='380' y='30' text-anchor='middle' font-size='18' fill='#1c3a5c'>"
    "克里普克：刚性指示、后天必然与规则遵循（示意）</text>"
    "<defs><marker id='arK1' markerWidth='10' markerHeight='8' refX='9' refY='4' orient='auto'>"
    "<path d='M0,0 L10,4 L0,8 Z' fill='#4a7ba6'/></marker></defs>"
    "<rect x='40' y='58' width='210' height='52' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='145' y='80' text-anchor='middle' font-size='12' fill='#1e2d3d'>专名：同一对象</text>"
    "<text x='145' y='99' text-anchor='middle' font-size='10' fill='#1e2d3d'>在一切可能世界都指称它</text>"
    "<rect x='510' y='58' width='210' height='52' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='615' y='80' text-anchor='middle' font-size='12' fill='#1e2d3d'>描述只“固定指称”</text>"
    "<text x='615' y='99' text-anchor='middle' font-size='10' fill='#1e2d3d'>不构成名字的意义</text>"
    "<line x1='145' y1='110' x2='318' y2='146' stroke='#4a7ba6' marker-end='url(#arK1)'/>"
    "<line x1='615' y1='110' x2='442' y2='146' stroke='#4a7ba6' marker-end='url(#arK1)'/>"
    "<rect x='250' y='150' width='260' height='56' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='380' y='174' text-anchor='middle' font-size='13' fill='#1c3a5c'>刚性指示词</text>"
    "<text x='380' y='193' text-anchor='middle' font-size='10' fill='#1e2d3d'>命名与因果历史链条传递指称</text>"
    "<line x1='320' y1='206' x2='140' y2='242' stroke='#4a7ba6' marker-end='url(#arK1)'/>"
    "<line x1='380' y1='206' x2='380' y2='242' stroke='#4a7ba6' marker-end='url(#arK1)'/>"
    "<line x1='440' y1='206' x2='620' y2='242' stroke='#4a7ba6' marker-end='url(#arK1)'/>"
    "<rect x='30' y='246' width='210' height='56' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='135' y='270' text-anchor='middle' font-size='12' fill='#1e2d3d'>后天的必然</text>"
    "<text x='135' y='289' text-anchor='middle' font-size='10' fill='#1e2d3d'>水＝H₂O：经验发现，却必然</text>"
    "<rect x='275' y='246' width='210' height='56' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='380' y='270' text-anchor='middle' font-size='12' fill='#1e2d3d'>同一性陈述</text>"
    "<text x='380' y='289' text-anchor='middle' font-size='10' fill='#1e2d3d'>启明星＝长庚星</text>"
    "<rect x='520' y='246' width='210' height='56' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='625' y='270' text-anchor='middle' font-size='12' fill='#1e2d3d'>规则遵循</text>"
    "<text x='625' y='289' text-anchor='middle' font-size='10' fill='#1e2d3d'>加 vs 夸加：过去用法两可</text>"
    "<line x1='380' y1='302' x2='380' y2='330' stroke='#4a7ba6' marker-end='url(#arK1)'/>"
    "<rect x='190' y='334' width='380' height='50' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='380' y='356' text-anchor='middle' font-size='12' fill='#1c3a5c'>意义由共同体断定，私人规则不可能</text>"
    "<text x='380' y='375' text-anchor='middle' font-size='10' fill='#1e2d3d'>此为克里普克式解读，非维特根斯坦原意</text>"
    "</svg>"
)

kripke = {
    "id": "gr-contemp-kripke",
    "name": "克里普克",
    "latin": "Saul Aaron Kripke",
    "birth_year": 1940,
    "death_year": 2022,
    "birth_display": "1940年",
    "death_display": "2022年",
    "birth_note": "生于纽约州贝赛德，犹太家庭；少年时即写出完备性定理。",
    "death_note": "2022年卒于新泽西州普莱恩斯伯勒镇。",
    "era": "1960年代以后的英美分析哲学。克里普克以可能世界语义学为模态逻辑奠基，并在《命名与必然性》中以刚性指示词与“后天必然”重划指称、必然与先验的关系，使形而上学重新成为分析哲学的正题。",
    "school": "分析哲学（模态逻辑与语言哲学）",
    "core_questions": [
        "专名如何指称？其意义是否由一组描述给出？",
        "必然性与先验性、偶然性与后天性是否等价？",
        "“符合规则”由什么事实来确定：个人意图还是共同体实践？"
    ],
    "arguments": [
        {
            "claim": "刚性指示词：专名在一切可能世界中指称同一对象，故不靠描述固定其意义",
            "premises": [
                "专名（如“尼克松”“亚里士多德”）在反事实情形中仍被用来指称现实世界中的那一个人，而不随该人在那个世界中做什么而改变。",
                "若专名的意义由一组识别性描述给出，则在描述不被满足的可能世界中，该名字将无所指或改指他人，这与我们使用名字的直觉不符。"
            ],
            "inference": "既然名字在所有可能世界都锁定同一对象，其指称就不能由偶然为真的描述来承担；名字通过初始命名与因果历史链条获得指称，描述至多帮助听者确定所指，而非构成意义。",
            "conclusion": "专名是刚性指示词，其意义不等于任何描述的内容；描述论对名称意义的说明因此失败。",
            "kind": "原文",
            "citation": "见《命名与必然性》（Naming and Necessity, 1980）第一讲"
        },
        {
            "claim": "后天必然：存在既必然又只能由经验发现的真理",
            "premises": [
                "“水是 H₂O”“启明星是长庚星（金星）”这类同一性陈述，其发现依赖经验研究，因而属于后天知识。",
                "若“水”与“H₂O”、“启明星”与“长庚星”各指同一对象，则该同一性在一切可能世界都成立，不可能有反例。"
            ],
            "inference": "必然性是关于模态地位的形而上学范畴，后天性是关于我们如何认识的认识论范畴；同一性陈述因此可以同时是后天的（就认识来源而言）与必然的（就形而上学地位而言）。",
            "conclusion": "必然与先验并不等同，偶然与后天也不等同；康德式“必然即先验”的等式被打破，形而上学模态重新获得独立地位。",
            "kind": "原文",
            "citation": "见《命名与必然性》第三讲（1980）"
        },
        {
            "claim": "规则遵循的怀疑论解读：任何过去的用法都可被解释为符合新规则",
            "premises": [
                "设想“加”与“夸加”（quus）：后者在我以往算过的所有数上都与加法结果相同，只在超出以往范围的运算中给出不同答案。",
                "过去一切具体演算都与这两条规则相容，因此没有任何过去的事实能唯一确定我此前意指的是哪一条规则。"
            ],
            "inference": "若有限的使用记录无法唯一确定规则，则“符合规则”就不能由个人的内在事实（心理图像、倾向）来保证，只能由共同体的公认用法、纠正与惩罚实践来断定。",
            "conclusion": "规则的意义须由共同体断定，私人的规则遵循不可能。须注明：这是克里普克对维特根斯坦的怀疑论式解读（“克里普肯斯坦”），并非维特根斯坦本人的原意。",
            "kind": "后人解读",
            "citation": "见《维特根斯坦论规则与私人语言》（1982）第二章；解读性质见 SEP“Wittgenstein”条目"
        }
    ],
    "works": [
        {
            "title": "《命名与必然性》",
            "edition": "《命名与必然性》中译参商务印书馆／上海译文（若无则英文版 Harvard University Press, 1980）",
            "note": "Naming and Necessity, 1980；据1970年普林斯顿讲稿整理"
        },
        {
            "title": "《维特根斯坦论规则与私人语言》",
            "edition": "《规则与私人语言》中译参复旦大学出版社（若无则 Harvard University Press, 1982）",
            "note": "Wittgenstein on Rules and Private Language, 1982"
        }
    ],
    "influenced_by": [
        {
            "name": "弗雷格",
            "id": None,
            "note": "涵义与指称的区分，以及“同一性陈述如何有认知价值”这一问题的提法"
        },
        {
            "name": "罗素",
            "id": None,
            "note": "描述论与“逻辑专名”学说，构成其反描述论论证的直接靶子"
        },
        {
            "name": "维特根斯坦",
            "id": None,
            "note": "《哲学研究》第138节以下的规则遵循讨论，被其发展为怀疑论式解读"
        }
    ],
    "influenced": [
        {
            "name": "语言哲学：指称的因果历史理论",
            "id": None,
            "note": "普特南的自然种类词与唐奈兰的指称讨论沿此展开"
        },
        {
            "name": "模态形而上学",
            "id": None,
            "note": "必然与偶然、本质与可能世界重新成为分析哲学的正题"
        },
        {
            "name": "心灵哲学与二维语义论",
            "id": None,
            "note": "“克里普克语义学”与可设想性论证塑造了心身问题与查尔默斯的二维框架"
        }
    ],
    "criticisms": [
        {
            "critic": "描述论者（塞尔等）",
            "view": "专名的指称仍依赖说话者掌握的识别性描述；克里普克的反例只否证了“唯一描述”的强版本，较弱形式的描述论仍能说明交际中如何确定所指。",
            "response": "克里普克式回应：描述可以“固定指称”而不构成意义，二者区分之后，描述论无法说明名字在反事实语境中的稳定性；初始命名与因果链条才是指称传递的机制。",
            "kind": "后人解读",
            "sources": ["iep-kripke", "sep-frege"]
        },
        {
            "critic": "二维语义论者（Chalmers）",
            "view": "若区分“认识论内涵”与“形而上学内涵”，“水是 H₂O”即可被刻画为认识上偶然、形而上学必然；克里普克赖以论证的可设想性直觉本身需要额外辩护。",
            "response": "克里普克一系的回应：二维框架只是把直觉重新编码，并未说明为何“水可能是别的液体”这一设想在形而上学上不成立；模态地位不能由认识通道来定义。",
            "kind": "后人解读",
            "sources": ["iep-kripke", "sep-logic-modal"]
        },
        {
            "critic": "维特根斯坦研究者（Baker、Hacker 一系）",
            "view": "《规则与私人语言》被指为误读：维特根斯坦的文本针对的是意义的社会性与实践，而非一个可由“怀疑论式解答”消解的怀疑论悖论。",
            "response": "克里普克承认这是“克里普克式”的问题构造，但坚持其哲学价值：若不引入共同体与纠正实践，怀疑论结论无法被挡住。",
            "kind": "后人解读",
            "sources": ["sep-wittgenstein", "iep-kripke"]
        }
    ],
    "misconceptions": [
        {
            "claim": "“后天必然”自相矛盾",
            "why": "必然性属形而上学模态（在一切可能世界成立），后天性属认识论（须经验才能知道）；两个谓词修饰不同层次，故“水是 H₂O”可同时是后天的与必然的。"
        },
        {
            "claim": "克里普克证明了本质主义",
            "why": "他论证的是模态直觉与同一性陈述的地位，并未给出事物的本质清单；从“水必然是 H₂O”推到“本质即微观结构”，还需额外的本质主义前提。"
        },
        {
            "claim": "克里普克说专名只是空标签、没有意义",
            "why": "他否认的是“意义＝描述内容”，而非名字有指称与用法；刚性指称与因果历史链条本身就是对名字如何起作用的正面说明。"
        }
    ],
    "quotes": [],
    "svg": SVG,
    "svg_caption": "克里普克：刚性指示、后天必然与规则遵循的共同体（示意图）",
    "sources": ["iep-kripke", "sep-logic-modal", "sep-wittgenstein", "sep-frege"],
    "needs_verification": False,
    "pending_notes": ""
}

with io.open(PATH, encoding="utf-8") as f:
    data = json.load(f)

ids = [p["id"] for p in data["philosophers"]]
if "gr-contemp-kripke" in ids:
    data["philosophers"] = [p for p in data["philosophers"] if p["id"] != "gr-contemp-kripke"]

data["philosophers"].append(kripke)

with io.open(PATH, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("philosophers:", [p["id"] for p in data["philosophers"]])
print("count:", len(data["philosophers"]))
