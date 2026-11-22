# -*- coding: utf-8 -*-
"""临时脚本：向 data/west/gr-19c.json 追加恩格斯条目。"""
import json

PATH = "data/west/gr-19c.json"

svg = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 760 400'>"
    "<rect x='0' y='0' width='760' height='400' fill='#f0f5fa'/>"
    "<text x='380' y='30' text-anchor='middle' font-size='18' fill='#1c3a5c'>恩格斯：辩证法、历史与上层建筑（示意）</text>"
    "<defs><marker id='arE1' markerWidth='10' markerHeight='8' refX='9' refY='4' orient='auto'>"
    "<path d='M0,0 L10,4 L0,8 Z' fill='#4a7ba6'/></marker></defs>"
    "<rect x='50' y='60' width='210' height='60' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='155' y='84' text-anchor='middle' font-size='12' fill='#1e2d3d'>自然界：量变→质变</text>"
    "<text x='155' y='103' text-anchor='middle' font-size='10' fill='#1e2d3d'>对立统一·否定之否定</text>"
    "<rect x='500' y='60' width='210' height='60' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='605' y='84' text-anchor='middle' font-size='12' fill='#1e2d3d'>历史：生产力与生产关系</text>"
    "<text x='605' y='103' text-anchor='middle' font-size='10' fill='#1e2d3d'>阶级与国家的起源</text>"
    "<line x1='205' y1='122' x2='300' y2='166' stroke='#4a7ba6' marker-end='url(#arE1)'/>"
    "<line x1='555' y1='122' x2='460' y2='166' stroke='#4a7ba6' marker-end='url(#arE1)'/>"
    "<rect x='230' y='170' width='300' height='62' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='380' y='194' text-anchor='middle' font-size='12' fill='#1c3a5c'>辩证法：同一套运动规律</text>"
    "<text x='380' y='213' text-anchor='middle' font-size='10' fill='#1e2d3d'>三规律是整理材料的方式，非先验公式</text>"
    "<line x1='380' y1='234' x2='380' y2='272' stroke='#4a7ba6' marker-end='url(#arE1)'/>"
    "<rect x='110' y='276' width='540' height='66' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='380' y='300' text-anchor='middle' font-size='12' fill='#1c3a5c'>经济归根到底起决定作用，但非唯一因素</text>"
    "<text x='380' y='320' text-anchor='middle' font-size='10' fill='#1e2d3d'>上层建筑有相对独立性并反作用于经济基础</text>"
    "</svg>"
)

entry = {
    "id": "gr-19c-engels",
    "name": "恩格斯",
    "latin": "Friedrich Engels",
    "birth_year": 1820,
    "death_year": 1895,
    "birth_display": "1820年",
    "death_display": "1895年",
    "birth_note": "生于普鲁士莱茵省巴门市（今伍珀塔尔），出身纺织厂主家庭。",
    "death_note": "1895年病逝于伦敦，遵遗嘱火化并撒骨灰于伊斯特本海滨。",
    "era": "工业资本主义扩张、工人运动组织化的时代。恩格斯在曼彻斯特经商期间考察英国工人状况，与马克思合作写作；晚年整理马克思遗稿，并成为第二国际的理论权威之一。",
    "school": "马克思主义（辩证唯物主义与历史唯物主义的系统表述者）",
    "core_questions": [
        "辩证法规律是否只在历史与社会中有效，还是同样适用于自然界？",
        "经济因素在历史解释中究竟起多大的作用？",
        "国家从何而来，又将向何处去？"
    ],
    "arguments": [
        {
            "claim": "辩证法规律在自然界与历史中同样有效",
            "premises": [
                "自然界与人类社会并非两类互不相干的领域，二者都由物质运动构成，因而服从同一套运动规律。",
                "黑格尔已以唯心主义方式表述了量变到质变、对立统一与否定之否定，但把规律归于概念的自我运动。"
            ],
            "inference": "若把黑格尔的辩证法“倒转”过来，即把观念中的辩证运动理解为现实物质过程的反映，则同一组规律既可用于解释自然现象，也可用于解释社会历史变迁。",
            "conclusion": "辩证法不是思辨建构，而是关于自然、社会与思维运动的一般规律；据此可以建立“自然辩证法”。不过这门学科是否成立，学界至今有长期争论。",
            "kind": "原文"
        },
        {
            "claim": "经济因素归根到底起决定作用，但不是唯一因素",
            "premises": [
                "历史唯物主义主张生产与再生产是历史的基础，但它从未主张经济是唯一起作用的原因。",
                "政治、法律、宗教、哲学等上层建筑一旦形成，便有其自身的传统与相对独立的运动逻辑。"
            ],
            "inference": "若上层建筑具有相对独立性，则它既能偏离经济基础，又能反过来作用于经济基础；因此历史是多种因素交互作用的结果，经济只在“归根到底”的意义上起决定作用。",
            "conclusion": "把历史唯物主义读成“经济决定论”是对它的曲解；经济是最终的解释性原则，而不是唯一的因果因素。",
            "kind": "原文"
        },
        {
            "claim": "国家是阶级矛盾不可调和的产物",
            "premises": [
                "在氏族制度解体的过程中，私有制与分工造成阶级分化，产生了利益彼此对立的集团。",
                "这些对立若不受控制，社会将在无休止的冲突中瓦解，而氏族制度已无力凭血缘纽带调和冲突。"
            ],
            "inference": "若社会需要一种凌驾于各阶级之上、形式上代表公共秩序的强制力量来维持秩序，则这种力量就是国家；它随阶级分裂而生，也将随阶级消亡而消亡。",
            "conclusion": "国家不是社会之外的永恒机构，而是阶级对立的产物与阶级统治的工具。",
            "kind": "原文"
        }
    ],
    "works": [
        {
            "title": "《反杜林论》",
            "edition": "《马克思恩格斯文集》，人民出版社（第 9 卷含《反杜林论》等）",
            "note": "1878 年成书；哲学编系统表述“自然辩证法”与唯物史观，被称为马克思主义的“百科全书”"
        },
        {
            "title": "《自然辩证法》",
            "edition": "《马克思恩格斯文集》，人民出版社（第 9 卷含《反杜林论》等）",
            "note": "1873—1882 年间的手稿，1925 年才以完整形态刊行；含《劳动在从猿到人转变过程中的作用》"
        },
        {
            "title": "《家庭、私有制和国家的起源》",
            "edition": "《马克思恩格斯文集》，人民出版社（第 9 卷含《反杜林论》等）",
            "note": "1884 年，依据摩尔根《古代社会》的研究；副题“就路易斯·亨·摩尔根的研究成果而作”"
        },
        {
            "title": "《路德维希·费尔巴哈和德国古典哲学的终结》",
            "edition": "《马克思恩格斯文集》，人民出版社（第 9 卷含《反杜林论》等）",
            "note": "1888 年；提出哲学基本问题（思维与存在的关系）与“实践是检验真理的标准”式表述"
        }
    ],
    "influenced_by": [
        {
            "name": "黑格尔",
            "id": None,
            "note": "辩证法的形式框架，被其从“概念自我运动”倒转为物质运动的规律"
        },
        {
            "name": "费尔巴哈",
            "id": None,
            "note": "宗教异化批判与唯物主义转向的中介，但其直观唯物主义受到恩格斯的批评"
        },
        {
            "name": "马克思",
            "id": "gr-19c-marx",
            "note": "终身合作者；恩格斯自认是“第二提琴手”，并在马克思逝世后整理《资本论》第二、三卷"
        }
    ],
    "influenced": [
        {
            "name": "第二国际理论（考茨基、普列汉诺夫）",
            "id": None,
            "note": "以《反杜林论》为教科书式范本，形成“辩证唯物主义”的普及叙述"
        },
        {
            "name": "苏联教科书体系",
            "id": None,
            "note": "将“辩证唯物主义+历史唯物主义”固定为两大部分的结构，影响 20 世纪社会主义国家的哲学教育"
        },
        {
            "name": "西方马克思主义（卢卡奇、法兰克福学派）",
            "id": None,
            "note": "主要作为被批评的对象出现：其“自然辩证法”被视为对辩证法的实证化误读"
        }
    ],
    "criticisms": [
        {
            "critic": "卢卡奇与西方马克思主义传统",
            "view": "把辩证法扩展到自然界，等于抽掉辩证法的主体—客体统一结构，使之退化为可实证的“自然规律”，从而遮蔽了无产阶级作为历史主体的意识问题。",
            "response": "可为恩格斯辩护的是：他把辩证法界定为“关于外部世界和人类思维运动的一般规律”，其自然研究意在破除机械论的自然观，而不是取消实践与主体的维度。",
            "kind": "后人解读",
            "sources": ["sep-engels", "sep-marx"]
        },
        {
            "critic": "分析马克思主义（G. A. 科恩等）",
            "view": "恩格斯在 1890 年代书信中的表述仍带功能解释的含混：既说经济“归根到底”决定，又承认上层建筑的反作用，却未给出可检验的机制说明。",
            "response": "回应是：这种弹性表述本身就是有意为之，用以拒绝单线因果；科恩本人的工作也可视为替“归根到底”补上功能解释的技术化重建。",
            "kind": "后人解读",
            "sources": ["sep-engels", "sep-marx"]
        }
    ],
    "misconceptions": [
        {
            "claim": "恩格斯把辩证法归结为三条固定“定律”的教条",
            "why": "他本人把三规律说成从自然与历史研究中抽象出来的整理方式，而非可套用于任何材料的先验公式，并明确反对把辩证法当作证明工具。"
        },
        {
            "claim": "恩格斯是“经济决定论”者，认为一切历史事件只由经济决定",
            "why": "他在 1890 年致布洛赫的信中直接反驳这种读法：经济是“归根到底”的因素，政治与观念领域有相对独立性并会反作用。"
        }
    ],
    "quotes": [
        {
            "text": "国家决不是从外部强加于社会的一种力量",
            "source_id": "marx-chinese",
            "locator": "《家庭、私有制和国家的起源》（《马克思恩格斯文集》第四卷）",
            "kind": "原文"
        }
    ],
    "svg": svg,
    "svg_caption": "恩格斯：自然与历史的同一套辩证规律，及其经济—上层建筑关系（示意图）",
    "sources": ["sep-engels", "sep-marx", "marx-chinese"],
    "needs_verification": False,
    "pending_notes": ""
}

with open(PATH, encoding="utf-8") as f:
    unit = json.load(f)

ids = [p["id"] for p in unit["philosophers"]]
assert "gr-19c-engels" not in ids, "已存在，勿重复追加"
unit["philosophers"].append(entry)

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(unit, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("ok", len(unit["philosophers"]), [p["id"] for p in unit["philosophers"]])
