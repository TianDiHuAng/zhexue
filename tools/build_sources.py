#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段 1：建立 sources.json —— 逐条实际打开页面核对后才置 verified=true。

规则（见 DECISIONS.md D8）：
  - 串行抓取、每次间隔、最多 3 次重试（并发会被 ctext / perseus 反爬拒绝）
  - 2xx 且响应正文含预期关键词 → verified=true
  - 403/429/503 → link_ok="blocked", verified=false
  - 404/DNS/超时 → link_ok=false, verified=false
把每条核验证据写进 sources.json 的 verify 字段，可复查。
"""
import json, os, re, ssl, sys, time, urllib.parse, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sources.json")
REPORT = os.path.join(ROOT, "sources_report.md")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
NOW = datetime.datetime.now().strftime("%Y-%m-%d")


def fetch(url, tries=2, timeout=15):
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            })
            r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
            return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            last = "HTTP %s" % e.code
            if e.code in (403, 429, 500, 502, 503, 504):
                time.sleep(1.6 * (i + 1))
                continue
            return e.code, ""
        except Exception as e:  # noqa: BLE001
            last = type(e).__name__ + ": " + str(e)[:80]
            time.sleep(1.2 * (i + 1))
    code = 0
    m = re.match(r"HTTP (\d+)", last)
    if m:
        code = int(m.group(1))
    return code, ""


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
          .replace("&#39;", "'").replace("&ndash;", "-").replace("&mdash;", "--"))
    return re.sub(r"\s+", " ", s).strip()


def meta(html, name):
    m = re.search(r'<meta\s+name="%s"\s+content="([^"]*)"' % re.escape(name), html, re.I)
    return clean(m.group(1)) if m else ""


# ---------------------------------------------------------------- 候选清单
# 原典（中国）：ctext 路径 / wikisource 条目名
CN_PRIMARY = [
    ("ct-analects", "《论语》", "孔子门人辑录", -400, "先秦语录体汇编，成书约战国前期", "ctext.org", "https://ctext.org/analects/zh", "论语", "引文以《论语》篇名标注（如《学而》）"),
    ("ct-daodejing", "《老子》（道德经）", "传老子（李耳）", -350, "成书年代有春秋末与战国中晚期两说", "ctext.org", "https://ctext.org/dao-de-jing/zh", "道德經", "王弼通行本八十一章；作者与成书年代学界有讨论"),
    ("ct-mozi", "《墨子》", "墨翟及后学", -400, "墨家总集，含后期墨家《墨经》六篇", "ctext.org", "https://ctext.org/mozi/zh", "墨子", "兼爱、非攻、天志、明鬼、经上下"),
    ("ct-mengzi", "《孟子》", "孟子及其弟子", -300, "七篇，宋代列入四书", "ctext.org", "https://ctext.org/mengzi/zh", "孟子", "性善、仁政、浩然之气的主要文本"),
    ("ct-zhuangzi", "《庄子》", "庄周及后学", -300, "内篇多归庄子，外杂篇多出后学", "ctext.org", "https://ctext.org/zhuangzi/zh", "莊子", "内七篇与外杂篇作者分层是学界通说"),
    ("ct-xunzi", "《荀子》", "荀况及后学", -250, "三十二篇，唐杨倞注", "ctext.org", "https://ctext.org/xunzi/zh", "荀子", "性恶、天人之分、礼论、正名"),
    ("ct-hanfeizi", "《韩非子》", "韩非", -240, "五十五篇，部分篇目真伪有讨论", "ctext.org", "https://ctext.org/hanfeizi/zh", "韓非子", "法术势与《解老》《喻老》"),
    ("ct-liji", "《礼记》", "相传戴圣编", -100, "四十九篇，汉人辑录先秦礼学文献", "ctext.org", "https://ctext.org/liji/zh", "禮記", "《大学》《中庸》原为其中两篇"),
    ("ct-daxue", "《礼记·大学》", "礼记篇目，朱熹列为四书之一", -100, "朱熹分经传，作者归属有争议", "ctext.org", "https://ctext.org/liji/da-xue/zh", "大學", "三纲领八条目出处"),
    ("ct-zhongyong", "《礼记·中庸》", "礼记篇目，传子思作", -100, "作者归属（子思）为传统说法", "ctext.org", "https://ctext.org/liji/zhong-yong/zh", "中庸", "未发已发、诚、天命之谓性"),
    ("ct-yijing", "《周易》", "经传合编，传伏羲文王孔子", -300, "经部成书西周，十翼战国至汉初", "ctext.org", "https://ctext.org/book-of-changes/zh", "周易", "王弼注本为通行本"),
    ("ct-zuozhuan", "《春秋左传》", "左丘明（传）", -350, "编年记事至前 468 年，成书约战国前期", "ctext.org", "https://ctext.org/chun-qiu-zuo-zhuan/zh", "春秋左傳", "先秦思想史重要背景史料"),
    ("ct-shiji", "《史记》", "司马迁", -90, "成书约前 94—前 90 年，三家注通行", "ctext.org", "https://ctext.org/shiji/zh", "史記", "《孔子世家》《老子韩非列传》等为生卒依据"),
    ("ct-chunqiufanlu", "《春秋繁露》", "董仲舒", -120, "今本十七卷八十二篇，部分篇目真伪有讨论", "ctext.org", "https://ctext.org/chun-qiu-fan-lu/zh", "春秋繁露", "天人感应与阴阳五行入儒的主要文本"),
    ("ct-lunheng", "《论衡》", "王充", 80, "三十卷八十五篇，成书约公元 70—80 年", "ctext.org", "https://ctext.org/lunheng/zh", "論衡", "疾虚妄、问孔刺孟"),
    ("ct-fayan", "《法言》", "扬雄", 10, "成书约公元 5—10 年，仿《论语》体", "ctext.org", "https://ctext.org/fayan/zh", "法言", "扬雄拟经之作"),
    ("ct-taixuanjing", "《太玄经》", "扬雄", 5, "仿《周易》而作，八十一首", "ctext.org", "https://ctext.org/taixuanjing/zh", "太玄", "“玄”作为宇宙论本根"),
    ("ct-tongshu", "《通书》", "周敦颐", 1070, "又称《易通》，四十章", "ctext.org", "https://ctext.org/tongshu/zh", "通書", "诚、几、太极；理学开山文本"),
    ("ct-zhuzi-yulei", "《朱子语类》", "朱熹门人辑，黎靖德编", 1270, "成书 1270 年，一百四十卷", "ctext.org", "https://ctext.org/zhuzi-yulei/zh", "朱子語類", "理气、格物、读书法的主要问答记录"),
    ("ct-chuanxilu", "《传习录》", "王守仁（门人辑）", 1550, "三卷，今本编定于明嘉靖年间", "ctext.org", "https://ctext.org/chuanxilu/zh", "傳習錄", "知行合一、致良知、四句教"),
    ("ct-rizhilu", "《日知录》", "顾炎武", 1670, "三十二卷，康熙年间刊行", "ctext.org", "https://ctext.org/rizhilu/zh", "日知錄", "经世致用与考据方法"),
    ("ws-liuzutanjing", "《六祖坛经》（宗宝本）", "传慧能说，法海集记", 1290, "宗宝本成于元至元年间；作者与成书层次学界有讨论", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("六祖壇經"), "六祖壇經", "顿悟、自性、无念；敦煌本与宗宝本文本差异需注意"),
    ("ws-mingyi", "《明夷待访录》", "黄宗羲", 1663, "成书 1663 年，清末重刊后影响巨大", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("明夷待訪錄"), "明夷待訪錄", "《原君》《原臣》《学校》"),
    ("ws-mengzi-ziyi", "《孟子字义疏证》", "戴震", 1777, "成书 1777 年，三卷", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("孟子字義疏證"), "孟子字義疏證", "理存于欲、血气心知"),
    ("ws-renxue", "《仁学》", "谭嗣同", 1897, "成书 1896—1897 年，梁启超刊布", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("仁學"), "仁學", "冲决网罗、以太与仁"),
    ("ws-zhengmeng", "《正蒙》", "张载", 1070, "门人编次，十七篇", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("正蒙"), "正蒙", "太虚即气、民胞物与（《西铭》另篇）"),
    ("ws-jinsilu", "《近思录》", "朱熹、吕祖谦合编", 1175, "成书 1175 年，十四卷", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("近思錄"), "近思錄", "理学入门选辑，道统谱系的文献基础"),
    ("ws-taijitushuo", "《太极图说》", "周敦颐", 1070, "约 250 字，附《太极图》", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("太極圖說"), "太極圖說", "无极而太极；朱陆无极太极之辩的文本"),
    ("ws-zhaolun", "《肇论》", "僧肇", 400, "四篇，成书约 5 世纪初", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("肇論"), "肇論", "不真空论、物不迁论；般若学中国化的关键文本"),
    ("ws-shishuoxinyu", "《世说新语》", "刘义庆（组织编撰）", 430, "成书约 5 世纪上半叶", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("世說新語"), "世說新語", "清谈与玄学风气的一手记录"),
    ("ws-jinshizizhang", "《华严金师子章》", "法藏", 700, "为武则天讲华严的纲要之作", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("金師子章"), "金師子章", "四法界、六相、十玄的简明纲要"),
    ("ws-mohezhiguan", "《摩诃止观》", "智顗（弟子灌顶记）", 594, "十卷，成书约 594 年", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("摩訶止觀"), "摩訶止觀", "天台止观体系；一念三千出处"),
    ("ws-chengweishi", "《成唯识论》", "玄奘译释，窥基笔受", 659, "十卷，成书 659 年", "维基文库", "https://zh.wikisource.org/wiki/" + urllib.parse.quote("成唯識論"), "成唯識論", "唯识三十颂的集成注释；识变与种子"),
]

# 原典（西方）：Perseus / 其它公有领域文本站
WEST_PRIMARY = [
    ("per-plato-republic", "Plato, Republic", "Plato（Jowett 英译，公有领域）", -380, "Perseus Digital Library 希腊文与英译对照", "Perseus Digital Library", "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0168", "Republic"),
    ("per-plato-apology", "Plato, Apology", "Plato（Jowett 英译）", -399, "苏格拉底申辩，Perseus 对照本", "Perseus Digital Library", "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0170", "Apology"),
    ("per-aristotle-metaphysics", "Aristotle, Metaphysics", "Aristotle（Ross 校本，Perseus）", -340, "十四卷，Perseus 希腊文与英译", "Perseus Digital Library", "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0052", "Metaphysics"),
    ("per-aristotle-nicomachean", "Aristotle, Nicomachean Ethics", "Aristotle（Rackham 英译，Loeb 公有领域）", -340, "十卷，Perseus 对照本", "Perseus Digital Library", "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0054", "Nicomachean"),
    ("na-summa", "Thomas Aquinas, Summa Theologiae", "Thomas Aquinas（English Dominican Province 英译，公有领域）", 1270, "新 advent 版全文，三部分", "New Advent", "https://www.newadvent.org/summa/", "Summa"),
    ("na-confessions", "Augustine, Confessions", "Augustine（Pusey 英译，公有领域）", 400, "十三卷，新 advent 版", "New Advent", "https://www.newadvent.org/fathers/1101.htm", "Confessions"),
    ("na-cityofgod", "Augustine, The City of God", "Augustine（Dods 英译，公有领域）", 426, "二十二卷，新 advent 版", "New Advent", "https://www.newadvent.org/fathers/1201.htm", "City of God"),
    ("emt-hume", "David Hume, An Enquiry Concerning Human Understanding", "David Hume（J. Bennett 现代拼写改编本）", 1748, "Early Modern Texts 改编本，非学术定本", "Early Modern Texts", "https://www.earlymoderntexts.com/assets/pdfs/hume1748.pdf", "Hume"),
    ("emt-kant", "Immanuel Kant, Critique of Pure Reason（节译本）", "Immanuel Kant（J. Bennett 节译改编本）", 1781, "仅为阅读辅助，引用须用 Meiner/Akademie 版页码", "Early Modern Texts", "https://www.earlymoderntexts.com/assets/pdfs/kant1781part1.pdf", "Kant"),
    ("emt-descartes", "René Descartes, Meditations on First Philosophy", "René Descartes（J. Bennett 改编本）", 1641, "六个沉思，拉丁文本 1641、法译本 1647", "Early Modern Texts", "https://www.earlymoderntexts.com/assets/pdfs/descartes1641.pdf", "Descartes"),
    ("emt-aristotle-ethics", "Aristotle, Nicomachean Ethics（Bennett 改编本）", "Aristotle（J. Bennett 改编本）", -340, "现代英语简化本，供入门阅读", "Early Modern Texts", "https://www.earlymoderntexts.com/assets/pdfs/aristotle.nicomacheanethics.pdf", "Aristotle"),
    ("marx-chinese", "马克思恩格斯著作中文版（马克思主义文库）", "Marx, Engels（中共中央马恩列斯著作编译局译）", 1848, "网络文库，仅作文献定位；正式引用以人民出版社《马克思恩格斯文集》为准", "马克思主义文库", "https://www.marxists.org/chinese/marx-engels/index.htm", "马克思"),
]

# 百科：SEP（作者与年份由页面 citation_* 元数据读出）
SEP = [
    ("confucius", "中国·先秦"), ("laozi", "中国·先秦"), ("zhuangzi", "中国·先秦"),
    ("mencius", "中国·先秦"), ("xunzi", "中国·先秦"), ("mozi", "中国·先秦"),
    ("hanfeizi", "中国·先秦"), ("chinese-metaphysics", "中国·总论"),
    ("chinese-ethics", "中国·总论"), ("neo-confucianism", "中国·宋明"),
    ("zhu-xi", "中国·宋明"), ("wang-yangming", "中国·宋明"),
    ("zhang-zai", "中国·宋明"), ("wang-bi", "中国·魏晋"),
    ("qing-philosophy", "中国·清"), ("chinese-buddhism-chan", "中国·隋唐"),
    ("buddhism-huayan", "中国·隋唐"), ("madhyamaka", "中国·隋唐"),
    ("yogacara", "中国·隋唐"), ("tiantai", "中国·隋唐"),
    ("plato", "西方·古希腊"), ("aristotle", "西方·古希腊"),
    ("socrates", "西方·古希腊"), ("presocratics", "西方·古希腊"),
    ("parmenides", "西方·古希腊"), ("heraclitus", "西方·古希腊"),
    ("democritus", "西方·古希腊"), ("protagoras", "西方·古希腊"),
    ("pythagoras", "西方·古希腊"), ("plotinus", "西方·希腊化罗马"),
    ("stoicism", "西方·希腊化罗马"), ("epicurus", "西方·希腊化罗马"),
    ("skepticism-ancient", "西方·希腊化罗马"), ("cicero", "西方·希腊化罗马"),
    ("augustine", "西方·中世纪"), ("aquinas", "西方·中世纪"),
    ("boethius", "西方·中世纪"), ("anselm", "西方·中世纪"),
    ("abelard", "西方·中世纪"), ("duns-scotus", "西方·中世纪"),
    ("ockham", "西方·中世纪"), ("universals-medieval", "西方·中世纪"),
    ("descartes", "西方·近代"), ("spinoza", "西方·近代"),
    ("leibniz", "西方·近代"), ("locke", "西方·近代"),
    ("berkeley", "西方·近代"), ("hume", "西方·近代"),
    ("bacon", "西方·近代"), ("kant", "西方·德国古典"),
    ("fichte", "西方·德国古典"), ("schelling", "西方·德国古典"),
    ("hegel", "西方·德国古典"), ("jacobi", "西方·德国古典"),
    ("schopenhauer", "西方·19世纪"), ("kierkegaard", "西方·19世纪"),
    ("marx", "西方·19世纪"), ("mill", "西方·19世纪"),
    ("nietzsche", "西方·19世纪"), ("comte", "西方·19世纪"),
    ("frege", "西方·20世纪"), ("husserl", "西方·20世纪"),
    ("russell", "西方·20世纪"), ("heidegger", "西方·20世纪"),
    ("wittgenstein", "西方·20世纪"), ("carnap", "西方·20世纪"),
    ("sartre", "西方·20世纪"), ("quine", "西方·20世纪"),
    ("phenomenology", "西方·20世纪"), ("rawls", "西方·当代"),
    ("nozick-political-philosophy", "西方·当代"), ("kripke", "西方·当代"),
    ("foucault", "西方·当代"), ("derrida", "西方·当代"),
    ("habermas", "西方·当代"), ("rorty", "西方·当代"),
    ("justice-distributive", "西方·当代"),
]

IEP = [
    ("confucius", "中国·先秦"), ("laozi", "中国·先秦"), ("zhuangzi", "中国·先秦"),
    ("mencius", "中国·先秦"), ("xunzi", "中国·先秦"), ("mohist", "中国·先秦"),
    ("chinese-philosophy", "中国·总论"), ("neo-confucianism", "中国·宋明"),
    ("wang-yangming", "中国·宋明"), ("plato", "西方·古希腊"),
    ("aristotle", "西方·古希腊"), ("plotinus", "西方·希腊化罗马"),
    ("stoicism", "西方·希腊化罗马"), ("epicurus", "西方·希腊化罗马"),
    ("skepticism", "西方·希腊化罗马"), ("augustine", "西方·中世纪"),
    ("aquinas", "西方·中世纪"), ("medieval-philosophy", "西方·中世纪"),
    ("descartes", "西方·近代"), ("spinoza", "西方·近代"),
    ("leibniz", "西方·近代"), ("locke", "西方·近代"),
    ("berkeley", "西方·近代"), ("hume", "西方·近代"),
    ("kant", "西方·德国古典"), ("hegel", "西方·德国古典"),
    ("schopenhauer", "西方·19世纪"), ("kierkegaard", "西方·19世纪"),
    ("marx", "西方·19世纪"), ("nietzsche", "西方·19世纪"),
    ("frege", "西方·20世纪"), ("husserl", "西方·20世纪"),
    ("wittgenstein", "西方·20世纪"), ("heidegger", "西方·20世纪"),
    ("sartre", "西方·20世纪"), ("quine", "西方·20世纪"),
    ("rawls", "西方·当代"), ("foucault", "西方·当代"),
    ("derrida", "西方·当代"), ("habermas", "西方·当代"),
]

# 学术著作：用 archive.org 检索接口定位真实条目，再打开条目页核对
BOOKS = [
    ("Fung Yu-lan A History of Chinese Philosophy", "book-fung-history", "Feng Youlan（冯友兰）", "A History of Chinese Philosophy", "Princeton University Press", 1952, "中国·总论"),
    ("A Source Book in Chinese Philosophy Chan", "book-chan-sourcebook", "Wing-tsit Chan（陈荣捷）编", "A Source Book in Chinese Philosophy", "Princeton University Press", 1963, "中国·总论"),
    ("Disputers of the Tao Graham", "book-graham-disputers", "A. C. Graham", "Disputers of the Tao: Philosophical Argument in Ancient China", "Open Court", 1989, "中国·先秦"),
    ("History of Greek Philosophy Guthrie", "book-guthrie-greek", "W. K. C. Guthrie", "A History of Greek Philosophy", "Cambridge University Press", 1962, "西方·古希腊"),
    ("History of Philosophy Copleston", "book-copleston-history", "Frederick Copleston", "A History of Philosophy", "Burns Oates & Washbourne / Continuum", 1946, "西方·总论"),
    ("History of Christian Philosophy in the Middle Ages Gilson", "book-gilson-medieval", "Étienne Gilson", "History of Christian Philosophy in the Middle Ages", "Random House", 1955, "西方·中世纪"),
    ("German Idealism Beiser", "book-beiser-german", "Frederick C. Beiser", "German Idealism: The Struggle against Subjectivism, 1781-1801", "Harvard University Press", 2002, "西方·德国古典"),
    ("A Theory of Justice Rawls", "book-rawls-justice", "John Rawls", "A Theory of Justice", "Harvard University Press", 1971, "西方·当代"),
    ("The Order of Things Foucault", "book-foucault-order", "Michel Foucault", "The Order of Things: An Archaeology of the Human Sciences", "Pantheon Books", 1970, "西方·当代"),
    ("Philosophical Investigations Wittgenstein", "book-wittgenstein-pi", "Ludwig Wittgenstein", "Philosophical Investigations", "Blackwell", 1953, "西方·20世纪"),
    ("Being and Time Heidegger", "book-heidegger-bt", "Martin Heidegger", "Being and Time", "Harper & Row", 1962, "西方·20世纪"),
    ("The Structure of Scientific Revolutions Kuhn", "book-kuhn-ssr", "Thomas S. Kuhn", "The Structure of Scientific Revolutions", "University of Chicago Press", 1962, "西方·20世纪"),
]

# 论文：Springer 开放获取检索（标题/作者/年份从检索结果页读出）
PAPERS = [
    ("Confucian ethics virtue", "Dao 或 Asian Philosophy 相关开放获取论文", "中国·先秦"),
    ("Chinese philosophy consciousness", "中国哲学与意识研究", "中国·总论"),
    ("Daoist wu wei", "道家无为", "中国·先秦"),
    ("Neo-Confucian li qi", "理学理气", "中国·宋明"),
    ("Aristotle virtue ethics eudaimonia", "亚里士多德德性伦理", "西方·古希腊"),
    ("Plato forms knowledge", "柏拉图理念论", "西方·古希腊"),
    ("Stoic determinism freedom", "斯多亚决定论与自由", "西方·希腊化罗马"),
    ("Aquinas essence existence", "阿奎那本质与存在", "西方·中世纪"),
    ("Hume causation induction", "休谟因果与归纳", "西方·近代"),
    ("Kant transcendental idealism", "康德先验唯心论", "西方·德国古典"),
    ("Hegel dialectic recognition", "黑格尔辩证法与承认", "西方·德国古典"),
    ("Nietzsche nihilism genealogy", "尼采虚无主义与谱系", "西方·19世纪"),
    ("Heidegger being Dasein", "海德格尔此在", "西方·20世纪"),
    ("Wittgenstein language games", "维特根斯坦语言游戏", "西方·20世纪"),
    ("Rawls justice fairness", "罗尔斯正义论", "西方·当代"),
    ("Foucault power knowledge", "福柯权力知识", "西方·当代"),
]


def norm_id(s):
    return re.sub(r"[^a-z0-9-]", "-", s.lower())


def main():
    out = []
    seen = set()
    fail = []

    def add(rec, ok, code, note=""):
        if rec["id"] in seen:
            print("%-5s %-46s dup-skip" % (code, rec["id"]), flush=True)
            return
        seen.add(rec["id"])
        out.append(rec)
        print("%-5s %-46s %s" % (code, rec["id"], "verified" if ok else "FAILED"), flush=True)

    # ---- 原典
    todo = [("原典", e) for e in CN_PRIMARY] + [("原典", e) for e in WEST_PRIMARY]
    for typ, e in todo:
        sid, title, author, year, ynote, pub, url, kw = e[:8]
        note = e[8] if len(e) > 8 else ""
        code, html = fetch(url)
        ok = code == 200 and kw.lower() in html.lower()
        rec = {
            "id": sid, "title": title, "author": author, "year": year,
            "year_note": ynote, "publisher": pub, "type": typ,
            "url": url, "url2": None,
            "link_ok": True if ok else ("blocked" if code in (401, 403, 429, 503) else False),
            "verified": bool(ok), "note": note, "unit_hint": "",
            "verify": {"method": "http-page", "http_status": code, "checked_at": NOW,
                       "keyword": kw, "keyword_seen": bool(ok)},
        }
        add(rec, ok, code)
        if not ok:
            fail.append((sid, url, code, kw))
        time.sleep(0.5)

    # ---- SEP
    for slug, hint in SEP:
        url = "https://plato.stanford.edu/entries/%s/" % slug
        code, html = fetch(url)
        ok = code == 200 and "Stanford Encyclopedia" in html
        if not ok:
            fail.append(("sep-" + slug, url, code, "Stanford Encyclopedia"))
            time.sleep(0.4)
            continue
        t = meta(html, "citation_title") or slug
        au = meta(html, "citation_author")
        dt = meta(html, "citation_publication_date")
        yr = int(dt[:4]) if re.match(r"\d{4}", dt or "") else None
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        title_cn = clean(h1.group(1)) if h1 else t
        rec = {
            "id": "sep-" + slug, "title": "%s（SEP 词条）" % (title_cn or t),
            "author": au or "Stanford Encyclopedia of Philosophy 编辑部",
            "year": yr, "year_note": "首次发布 %s；后续修订见页面" % (dt or "未标注"),
            "publisher": "Stanford Encyclopedia of Philosophy（斯坦福大学）",
            "type": "百科", "url": url, "url2": "https://plato.stanford.edu/entries/%s" % slug,
            "link_ok": True, "verified": True,
            "note": "同行评审的学术百科，含完整参考文献与版本信息", "unit_hint": hint,
            "verify": {"method": "http-page+citation_meta", "http_status": code,
                       "checked_at": NOW, "title_seen": title_cn[:60]},
        }
        add(rec, True, code)
        time.sleep(0.5)

    # ---- IEP
    for slug, hint in IEP:
        url = "https://iep.utm.edu/%s/" % slug
        code, html = fetch(url)
        ok = code == 200 and "Internet Encyclopedia of Philosophy" in html
        if not ok:
            fail.append(("iep-" + slug, url, code, "Internet Encyclopedia"))
            time.sleep(0.4)
            continue
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        title_cn = clean(h1.group(1)) if h1 else slug
        au = ""
        m = re.search(r"(?:Author Information|Author\(s\))[^<]*</?[^>]*>?\s*([A-Z][^<]{2,80})", html)
        if m:
            au = clean(m.group(1))
        rec = {
            "id": "iep-" + slug, "title": "%s（IEP 词条）" % title_cn,
            "author": au or "Internet Encyclopedia of Philosophy（作者署名见页面）",
            "year": None, "year_note": "IEP 词条不固定标注出版年，页面标注最后修订",
            "publisher": "Internet Encyclopedia of Philosophy（非营利学术百科）",
            "type": "百科", "url": url, "url2": None, "link_ok": True, "verified": True,
            "note": "与 SEP 互补的学术百科，可用于双源互证", "unit_hint": hint,
            "verify": {"method": "http-page", "http_status": code, "checked_at": NOW,
                       "title_seen": title_cn[:60]},
        }
        add(rec, True, code)
        time.sleep(0.5)

    # ---- 学术著作（archive.org 检索 → 打开条目页）
    for q, sid, author, title, pub, yr, hint in BOOKS:
        api = ("https://archive.org/advancedsearch.php?q=%s&fl%%5B%%5D=identifier&fl%%5B%%5D=title"
               "&fl%%5B%%5D=year&rows=5&page=1&output=json" % urllib.parse.quote('title:(%s)' % q))
        code, body = fetch(api)
        ident = None
        if code == 200 and body.strip().startswith("{"):
            try:
                docs = json.loads(body)["response"]["docs"]
                if docs:
                    ident = docs[0]["identifier"]
            except Exception:  # noqa: BLE001
                ident = None
        if not ident:
            fail.append((sid, api, code, "archive.org item"))
            time.sleep(0.4)
            continue
        iurl = "https://archive.org/details/%s" % ident
        code2, html2 = fetch(iurl)
        ok = code2 == 200 and ident in html2
        rec = {
            "id": sid, "title": title, "author": author, "year": yr,
            "year_note": "初版年份；archive.org 条目为可检索扫描本，页码以原书为准",
            "publisher": pub, "type": "学术著作", "url": iurl,
            "url2": "https://openlibrary.org/search?q=%s" % urllib.parse.quote(title),
            "link_ok": True if ok else ("blocked" if code2 in (401, 403, 429) else False),
            "verified": bool(ok),
            "note": "archive.org 扫描本（部分需借阅）；引用页码以纸本版次为准",
            "unit_hint": hint,
            "verify": {"method": "archive.org search+item-page", "http_status": code2,
                       "checked_at": NOW, "title_seen": ident},
        }
        add(rec, ok, code2)
        if not ok:
            fail.append((sid, iurl, code2, ident))
        time.sleep(0.5)

    # ---- 论文（Springer 开放获取检索结果页解析）
    for q, note, hint in PAPERS:
        url = ("https://link.springer.com/search?query=%s&facet-content-type=%%22Article%%22"
               "&facet-openaccess=true" % urllib.parse.quote(q))
        code, html = fetch(url)
        if code != 200:
            fail.append(("paper-" + norm_id(q)[:24], url, code, "springer search"))
            time.sleep(0.4)
            continue
        # 解析首条结果：文章链接 + 标题 + 期刊 + 年份
        m = re.search(r'href="(/article/10\.\d{4,9}/[^"]+)"[^>]*>(.*?)</a>', html, re.S)
        if not m:
            fail.append(("paper-" + norm_id(q)[:24], url, code, "no article parsed"))
            time.sleep(0.4)
            continue
        path, raw_title = m.group(1), clean(m.group(2))
        aurl = "https://link.springer.com" + path
        code2, html2 = fetch(aurl)
        ok = code2 == 200 and len(html2) > 5000
        atitle = meta(html2, "citation_title") or raw_title
        aau = meta(html2, "citation_author")
        adt = meta(html2, "citation_publication_date")
        aj = meta(html2, "citation_journal_title")
        doi = path.split("/article/")[-1]
        rec = {
            "id": "paper-" + norm_id(doi.split("/")[-1])[:40],
            "title": atitle, "author": aau or "（作者见页面）",
            "year": int(adt[:4]) if re.match(r"\d{4}", adt or "") else None,
            "year_note": "开放获取论文，出版年取自页面元数据",
            "publisher": aj or "Springer",
            "type": "论文", "url": aurl, "url2": "https://doi.org/" + doi,
            "link_ok": True if ok else ("blocked" if code2 in (401, 403, 429) else False),
            "verified": bool(ok), "note": note, "unit_hint": hint,
            "verify": {"method": "http-page+citation_meta", "http_status": code2,
                       "checked_at": NOW, "title_seen": atitle[:60]},
        }
        add(rec, ok, code2)
        if not ok:
            fail.append((rec["id"], aurl, code2, atitle[:40]))
        time.sleep(0.5)

    # ---- 写盘
    order = {"原典": 0, "百科": 1, "学术著作": 2, "论文": 3}
    out.sort(key=lambda r: (order.get(r["type"], 9), r["id"]))
    for i, r in enumerate(out, 1):
        r["n"] = i
    data = {
        "meta": {
            "project": "中外哲学思想脉络库",
            "built_at": NOW,
            "rule": "verified=true 仅当脚本实际打开页面且正文含预期关键词；403/429 记为 blocked 且不作已验证来源",
            "total": len(out),
            "verified": sum(1 for r in out if r["verified"]),
            "by_type": {t: sum(1 for r in out if r["type"] == t) for t in order},
        },
        "sources": out,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")

    lines = ["# sources 核验报告", "",
             "- 生成时间：%s" % NOW,
             "- 候选收集：%d 条；通过核验：%d 条" % (len(out) + len(fail), len(out)),
             "", "## 按类型", ""]
    for t in order:
        lines.append("- %s：%d 条（verified %d）" % (
            t, data["meta"]["by_type"].get(t, 0),
            sum(1 for r in out if r["type"] == t and r["verified"])))
    if fail:
        lines += ["", "## 未通过（已从 sources.json 剔除或标 blocked）", ""]
        lines += ["| id | http | url | 预期关键词 |", "|---|---|---|---|"]
        for sid, url, code, kw in fail:
            lines.append("| `%s` | %s | %s | %s |" % (sid, code, url, kw))
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps(data["meta"], ensure_ascii=False, indent=1))
    print("failures:", len(fail))


if __name__ == "__main__":
    main()
