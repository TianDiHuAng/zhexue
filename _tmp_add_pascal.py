# -*- coding: utf-8 -*-
"""向 data/west/gr-modern.json 追加帕斯卡（gr-modern-pascal）。"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "data", "west", "gr-modern.json")

SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 760 400'>"
    "<rect x='0' y='0' width='760' height='400' fill='#f0f5fa'/>"
    "<text x='380' y='30' text-anchor='middle' font-size='18' fill='#1c3a5c'>帕斯卡：两种精神—赌注—可悲与伟大（示意）</text>"
    "<defs><marker id='ar-pascal' markerWidth='10' markerHeight='8' refX='9' refY='4' orient='auto'>"
    "<path d='M0,0 L10,4 L0,8 Z' fill='#4a7ba6'/></marker></defs>"
    "<rect x='36' y='52' width='210' height='60' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='141' y='74' text-anchor='middle' font-size='12' fill='#1e2d3d'>几何精神</text>"
    "<text x='141' y='95' text-anchor='middle' font-size='10' fill='#1e2d3d'>定义→演绎→必然结论</text>"
    "<rect x='290' y='52' width='180' height='60' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='380' y='74' text-anchor='middle' font-size='12' fill='#1c3a5c'>心（cœur）</text>"
    "<text x='380' y='95' text-anchor='middle' font-size='10' fill='#1e2d3d'>第一原理在此被感到</text>"
    "<rect x='514' y='52' width='210' height='60' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='619' y='74' text-anchor='middle' font-size='12' fill='#1e2d3d'>微妙精神</text>"
    "<text x='619' y='95' text-anchor='middle' font-size='10' fill='#1e2d3d'>直觉把握具体处境</text>"
    "<line x1='246' y1='82' x2='286' y2='82' stroke='#4a7ba6' marker-end='url(#ar-pascal)'/>"
    "<line x1='514' y1='82' x2='474' y2='82' stroke='#4a7ba6' marker-end='url(#ar-pascal)'/>"
    "<line x1='380' y1='112' x2='380' y2='132' stroke='#4a7ba6' marker-end='url(#ar-pascal)'/>"
    "<rect x='100' y='136' width='560' height='110' rx='6' fill='#dce8f4' stroke='#1c3a5c'/>"
    "<text x='380' y='158' text-anchor='middle' font-size='12' fill='#1c3a5c'>赌注：理性不能判定，行动却必须选择</text>"
    "<rect x='118' y='170' width='250' height='60' rx='6' fill='#dbe8f3' stroke='#4a7ba6'/>"
    "<text x='243' y='192' text-anchor='middle' font-size='10' fill='#1e2d3d'>下注（信）：神在则得无限</text>"
    "<text x='243' y='212' text-anchor='middle' font-size='10' fill='#1e2d3d'>神不在则只失有限之物</text>"
    "<rect x='392' y='170' width='250' height='60' rx='6' fill='#dbe8f3' stroke='#4a7ba6'/>"
    "<text x='517' y='192' text-anchor='middle' font-size='10' fill='#1e2d3d'>不下注（不信）：神在则失无限</text>"
    "<text x='517' y='212' text-anchor='middle' font-size='10' fill='#1e2d3d'>神不在则只得有限之物</text>"
    "<line x1='380' y1='246' x2='380' y2='266' stroke='#4a7ba6' marker-end='url(#ar-pascal)'/>"
    "<rect x='140' y='270' width='480' height='66' rx='6' fill='#dbe8f3' stroke='#1c3a5c'/>"
    "<text x='380' y='294' text-anchor='middle' font-size='13' fill='#1c3a5c'>可悲：想象与自爱遮蔽真实处境</text>"
    "<text x='380' y='316' text-anchor='middle' font-size='13' fill='#1c3a5c'>伟大：思想使人超出宇宙的广袤</text>"
    "<text x='380' y='364' text-anchor='middle' font-size='10' fill='#4a7ba6'>注：《思想录》Lafuma 512（两种精神）／418（赌注）／200、347（芦苇）</text>"
    "</svg>"
)

PASCAL = {
    "id": "gr-modern-pascal",
    "name": "帕斯卡",
    "latin": "Blaise Pascal",
    "birth_year": 1623,
    "death_year": 1662,
    "birth_display": "1623年",
    "death_display": "1662年",
    "birth_note": "据其姊吉尔贝特（Gilberte Périer）所作传记，1623 年 6 月 19 日生于克莱蒙费朗。",
    "death_note": "1662 年 8 月 19 日卒于巴黎，年仅 39；姊传与尸检记录所记日期相符。",
    "era": "宗教战争与科学革命交错之际的法国。帕斯卡幼年丧母，由父亲（税务官、数学爱好者）在家教育，16 岁写出圆锥曲线论文，19 岁造出加法机，与费马通信奠定概率论的基础；1654 年 11 月 23 日的「火之夜」经验使他转向护教写作。他身处冉森派与耶稣会的争论中心，又亲眼见到机械论哲学的成功与它无法安顿人的界限，其问题是：在几何学已能计算自然、却算不出人的得救的条件下，人凭什么活下去、凭什么相信。",
    "school": "冉森派奥古斯丁主义（理性论与经验论之外的「第三条路线」）",
    "core_questions": [
        "几何学的证明方式在什么对象上失效，失效之处靠什么认识？",
        "理性既不能证明也不能否证上帝时，人应当如何行动？",
        "人的可悲与伟大为何出自同一个根源？"
    ],
    "arguments": [
        {
            "claim": "几何精神与微妙精神是两种不可互相替代的认识方式",
            "premises": [
                "几何精神（esprit de géométrie）从定义与公理出发，只在可被定义、可被演绎的对象上有效，其推进方式是证明，且结论是必然的。",
                "微妙精神（esprit de finesse）面对的是人心、处境与人生这类不可定义的具体对象；它不靠中间命题的链条，而靠一眼把握整体与分寸。",
                "同一条原理在几何学中位于开端并可被证明，在微妙精神中却位于末端，是被直接感到而非被推出的。"
            ],
            "inference": "若两类对象的本性不同，则把几何学的证明程序普遍化为唯一的理性形式，就会在不可定义者上强行下定义、在需要整体感的地方只交出碎片；故认识必须按对象调整形式，微妙精神的判断虽不能形式化，却并不因此低于几何精神。",
            "conclusion": "两种精神各有其合法领域；把其中一种硬套到另一种的对象上，是雄辩与虔诚同时失败的根源（《思想录》Lafuma 512）。",
            "kind": "原文"
        },
        {
            "claim": "上帝存在与否无法由理性裁定，而赌注使信仰成为合理的实践选择",
            "premises": [
                "理性既不能证明上帝存在，也不能证明他不存在；双方的论证都不能迫使心智同意。",
                "但人无法悬置行动：信与不信都不是中立状态，人已经置身赌局之中，必须为其中一边下注。",
                "若上帝存在，信者得无限之善、不信者失无限之善；若上帝不存在，信者所失与不信者所得都只是有限之物。"
            ],
            "inference": "以期望衡量，有限得失的差额抵不过无限得失的差额，故选择信仰的期望优于不选择信仰；论证的结论只是「应当开始下注」，随后才谈得上通过仪式与习惯削弱激情、使信仰变得可生活。",
            "conclusion": "赌注论证是实践理性的抉择论证，只说明应当下注，并不证明上帝存在；它针对尚可被说服的「冷漠者」，而非已受启示者（Lafuma 418）。",
            "kind": "原文"
        },
        {
            "claim": "人的可悲与伟大出自同一根源：思想",
            "premises": [
                "人在宇宙中极其微小：一口气、一滴水便足以致其死命，故就物理而言人只是一根芦苇。",
                "然而人知道自己会死，也知道宇宙比他更强，而宇宙对此一无所知；能认识自身的可悲，本身是一种特权。",
                "人又因想象、自爱与消遣（divertissement）不断遮蔽自己的真实处境，把依赖与有限误认为自足。"
            ],
            "inference": "伟大与可悲来自同一个根源：思想。思想使人超出宇宙的广袤，也使人看见自己的坠落；故不能以伟大否认可悲，也不能以可悲否认伟大，二者互为证据。",
            "conclusion": "人是「会思想的芦苇」：全部尊严在于思想，而可悲也正由思想所揭示（Lafuma 200、347）。",
            "kind": "原文"
        }
    ],
    "works": [
        {
            "title": "《思想录》（Pensées）",
            "edition": "1670 年波尔-罗亚尔（Port-Royal）版首次刊行，据遗稿分类整理；编号依 Lafuma 版；《思想录》何兆武译，商务印书馆",
            "note": "护教残稿，非成书；Lafuma 编号依手稿卷宗顺序，与 Brunschvicg 编号不同，引用时必须注明所用编号系统"
        },
        {
            "title": "《致外省人信札》（Les Provinciales）",
            "edition": "1656—1657 年以 Louis de Montalte 之名匿名刊行于巴黎，共 18 封信；中译参商务印书馆汉译世界学术名著本（译者与版次待核）",
            "note": "为阿尔诺辩护、抨击耶稣会决疑论的宽松道德神学，同时是近代法语散文的典范"
        },
        {
            "title": "《论圆锥曲线》（Essai pour les coniques）",
            "edition": "1640 年单页印行于巴黎，时年 16 岁；参《帕斯卡全集》（Œuvres complètes，七星文库本）",
            "note": "以射影几何方法给出帕斯卡定理：内接于圆锥曲线的六边形，其三对对边的交点共线"
        }
    ],
    "influenced_by": [
        {
            "name": "蒙田（Michel de Montaigne）",
            "id": None,
            "note": "《随笔集》的怀疑与自我描绘为帕斯卡所承；「可悲与伟大」的辩证直接与蒙田对话，并试图以恩典补其怀疑之不足"
        },
        {
            "name": "笛卡尔（见本单元另页）",
            "id": "gr-modern-descartes",
            "note": "接受其机械论与几何学方法，却拒绝以「上帝存在的证明」安顿信仰；「笛卡尔在哲学上无益而可疑」一语见《思想录》"
        },
        {
            "name": "冉森派与奥古斯丁主义",
            "id": None,
            "note": "通过波尔-罗亚尔修道院与圣西朗接受奥古斯丁的恩典论：人是堕落而依赖恩典的存在，理性不能自救"
        }
    ],
    "influenced": [
        {
            "name": "克尔凯郭尔",
            "id": None,
            "note": "抉择、赌注与「主体性的真理」的结构被其继承，帕斯卡因而被读作存在主义式基督教思想的先驱"
        },
        {
            "name": "存在主义（雅斯贝尔斯、马塞尔等）",
            "id": None,
            "note": "以处境、界限与抉择取代体系构造，格言体写作成为哲学表达方式"
        },
        {
            "name": "近代宗教哲学与决策论",
            "id": None,
            "note": "赌注论证成为宗教认识论与期望效用讨论的标准案例，被反复形式化与反驳"
        }
    ],
    "criticisms": [
        {
            "critic": "伏尔泰",
            "view": "赌注论证是「赌徒的论证」：把信仰当作以无限收益为赌注的投机，既亵渎神，也冒犯理性；况且赌局的前提（只有两种可能、收益为无限）本身未经证明。",
            "response": "辩护者指出：论证的目标不是证明上帝存在，而是指出在理性无能为力之处「不下注」并非中立，故须依期望作实践抉择；伏尔泰的批评即使成立，也只否定了论证的修辞包装，未触及「必须抉择」这一前提。",
            "kind": "后人解读",
            "sources": ["sep-pascal", "iep-pascal"]
        },
        {
            "critic": "现代决策论（如 Hájek 对无穷效用与「多神」反驳的分析）",
            "view": "赌注论证依赖无穷效用可比与二分假设：若存在多个可能的神，各自要求不同的信仰与惩罚，期望计算便无法给出唯一选择；而无穷与无穷之差在标准效用理论中不可比较。",
            "response": "辩护路径有二：把论证限制在「至少有一个要求信仰的上帝」的弱前提上；或承认它只是护教修辞，其力量在动员而非证明——帕斯卡本人以「赌」自称，并未把它当作严格证明。",
            "kind": "后人解读",
            "sources": ["sep-pascal", "iep-pascal"]
        }
    ],
    "misconceptions": [
        {
            "claim": "赌注论证是上帝存在的证明",
            "why": "论证的前提明说理性无法判定上帝是否存在；它比较的是信与不信两种行动的期望得失，结论只是「应当下注」的实践判断。若它已是证明，赌局便无须设立；手稿中这部分属护教谈话，而非形而上学的证明。"
        },
        {
            "claim": "帕斯卡是反理性主义者",
            "why": "他从未弃置理性：几何精神被承认为理性的严格形式，他本人是圆锥曲线与概率论的计算者；所争者是理性的界限——理性能推出结论，却须由「心」感到第一原理。把「划定界限」读成「废弃理性」，是对《思想录》的误读。"
        }
    ],
    "quotes": [],
    "svg": SVG,
    "svg_caption": "帕斯卡：几何精神与微妙精神之分、赌注的得失结构与「会思想的芦苇」（重构示意图）",
    "sources": ["sep-pascal", "iep-pascal"],
    "needs_verification": True,
    "pending_notes": "sources.json 中无帕斯卡原典译本（无 emt-pascal），故 quotes 留空、needs_verification 置 true；三条论点所标 Lafuma 编号（512、418、200／347）依 SEP 与 IEP 的通行引证转录，具体段落归属与何兆武译本页码待核；《致外省人信札》中译本的译者与版次亦待核。"
}


def main():
    with open(PATH, encoding="utf-8") as f:
        unit = json.load(f)
    ids = [p["id"] for p in unit["philosophers"]]
    assert "gr-modern-pascal" not in ids, "已存在"
    assert len(ids) == 7, "现有哲学家数量异常：%d" % len(ids)
    unit["philosophers"].append(PASCAL)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(unit, f, ensure_ascii=False, indent=1)
    print("OK philosophers=%d" % len(unit["philosophers"]))
    print([p["id"] for p in unit["philosophers"]])


if __name__ == "__main__":
    main()
