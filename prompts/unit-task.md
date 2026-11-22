# 单元写作任务书（子代理用）

你的任务：为「中外哲学思想脉络库」写**一个单元**的 JSON 数据文件。只写这一个文件，不要改任何其它文件，不要跑 git。

- 目标文件：`data/<region>/<unit_id>.json`（region = `china` 或 `west`）
- 参考样板（务必先读，结构、语气、颗粒度以它为准）：`data/china/cn-xianqin.json`
- 编辑基准（入选人物/概念/争论清单）：`scope.md` 中对应单元那一节
- 来源白名单：`sources.json`（**只能**引用其中 `verified: true` 的 id，不能自造 id）
- 体例规则：`DECISIONS.md`（尤其 D5 原文/后人解读、D6 引文政策、D7 双源规则、D9 年份）

写完后必须自检：

```
python tools/check.py --file data/<region>/<unit_id>.json
```

直到 `错误 0`（警告尽量清零）。不要用 `--quiet` 掩盖细节。

---

## 一、文件结构

```json
{
 "unit_id": "cn-xianqin",
 "region": "china",
 "title": "先秦诸子",
 "period": "前6世纪—前221",
 "start_year": -600,
 "end_year": -221,
 "summary": "80—200 字的时期背景：为什么这一时期会提出这些问题。",
 "threads": ["本单元 3—5 条思想线索，每条一句话"],
 "philosophers": [ ... 4—8 位 ... ],
 "concepts": [ ... 6—10 个 ... ],
 "debates": [ ... 2—3 场 ... ]
}
```

## 二、哲学家对象（每位都要写全九个字段组）

```json
{
 "id": "cn-xianqin-kongzi",
 "name": "孔子",
 "latin": "Confucius (Kong Qiu)",
 "birth_year": -551, "death_year": -479,
 "birth_display": "前551年", "death_display": "前479年",
 "birth_note": "据《史记·孔子世家》与《春秋》经传换算（通说）。",
 "death_note": "同上。卒年有前479/前478 两说，取通行前479。",
 "era": "春秋末期，王官之学散入民间，礼崩乐坏与诸侯争霸并行（40 字以上）。",
 "school": "儒家",
 "core_questions": ["礼乐秩序崩坏之后，凭什么重建人间秩序？", "人凭什么成其为人？"],
 "arguments": [
   {"claim": "仁是礼的内在根据",
    "premises": ["前提1（一句话）", "前提2"],
    "inference": "由前提推出结论的那一步（10 字以上，写清推理，不要跳步）",
    "conclusion": "结论（6 字以上）",
    "kind": "后人解读"}
 ],
 "works": [{"title": "《论语》", "edition": "杨伯峻《论语译注》，中华书局（现代标点整理本）；篇章以朱熹《集注》本为准", "note": "语录体，非孔子手著"}],
 "influenced_by": [{"name": "周公（传统谱系）", "id": null, "note": "孔子自述“述而不作”，以周礼为宗"}],
 "influenced": [{"name": "孟子", "id": "cn-xianqin-mengzi", "note": "仁→性善的转写"}],
 "criticisms": [{"critic": "墨子", "view": "儒者“繁饰礼乐”“厚葬久丧”，耗费民财而延误生事。", "response": "儒家的回应：礼是节文，丧祭是“慎终追远”，其用在于安人心而非耗财。", "kind": "后人解读", "sources": ["ct-mozi", "sep-mozi"]}],
 "misconceptions": [{"claim": "孔子主张“愚民”", "why": "“民可使由之，不可使知之”的断句与语境有争议；把它读作政策主张是后起的解释。"}],
 "quotes": [{"text": "学而时习之，不亦说乎", "source_id": "ct-analects", "locator": "《论语·学而》", "kind": "原文"}],
 "svg": "<svg ...>...</svg>",
 "svg_caption": "孔子的核心问题与论证走向（示意）",
 "sources": ["sep-confucius", "iep-confucius"],
 "needs_verification": false,
 "pending_notes": ""
}
```

### 硬性要求

1. `arguments` ≥ 2 条，每条必须真的写成「前提 → 推理 → 结论」，不能只写结论。前提是句子，不是关键词。
2. `kind` 只能是 `原文` 或 `后人解读`。凡属体系化重构（如“仁是礼的内在根据”）标 `后人解读`；凡原文明言（如“性相近也，习相远也”）标 `原文`。
3. `works.edition` 必须写具体版本（出版社/整理者/译本），≥8 字；不确定版本就写"以中华书局点校本为通行本，具体版次待核"。
4. `criticisms` ≥ 1 条，必须有 `critic`、`view`、`response`（被批评方如何回应），并各自 `sources` ≥ 2 个白名单 id。
5. `misconceptions` ≥ 1 条，写“常见说法 + 为什么容易误解/实际如何”。
6. `quotes` 可选，但一旦写就必须：`source_id` 是 `type=原典` 且在 sources.json 中 `verified: true`；`locator` 写到篇（如《孟子·告子上》《形而上学》Γ.2）；单条 ≤ 60 字。**找不到出处的名言绝对不要写**，宁可整条 `quotes` 省略。
7. `sources` ≥ 2 个不同 id 且都 verified；不够就 `needs_verification: true` + `pending_notes` 写清缺什么。
8. `id` 只能是 `a-z 0-9 -`：`<unit_id>-<拼音>`，如 `gr-ancient-plato`、`cn-songming-zhu-xi`。不要大写、不要撇号、ü 写成 v。
9. `birth_year`/`death_year` 必须是整数（公元前负数）；`birth_display` 首个数字的绝对值必须等于 `|birth_year|`。生卒不可考也要给学术界通行估值，并在 `*_note` 说明。

## 三、概念对象

```json
{
 "id": "cn-xianqin-ren",
 "term": "仁",
 "term_latin": "ren（humaneness / benevolence）",
 "definition": "20—120 字的一句话定义，中性描述，不作评价。",
 "usages": [
   {"name": "孔子", "id": "cn-xianqin-kongzi", "usage": "仁是……（15 字以上，写出这位哲学家特有的用法）"},
   {"name": "孟子", "id": "cn-xianqin-mengzi", "usage": "把仁收到心上，讲……"}
 ],
 "related": ["cn-xianqin-li"],
 "example": {"text": "一个具体场景或文本片段（20 字以上），说明这个概念怎么用。", "figure": "孔子", "locator": "《论语·颜渊》"},
 "sources": ["ct-analects", "sep-confucius"],
 "needs_verification": false, "pending_notes": ""
}
```

- `usages` ≥ 2 位，**必须写出差异**（同一人同一说法会被校验器判为重复）。id 必须是本单元哲学家。
- 例子要具体（谁、在什么场合、怎么用），不要用“例如某人认为……”的空话。

## 四、争论对象

```json
{
 "id": "cn-xianqin-human-nature",
 "title": "人性善恶之争",
 "question": "人的本性是善还是恶？（8 字以上）",
 "positions": [
   {"holder": "孟子", "id": "cn-xianqin-mengzi", "stance": "性善", "reasons": ["四端说……", "……"], "kind": "原文"},
   {"holder": "荀子", "id": "cn-xianqin-xunzi", "stance": "性恶", "reasons": ["……"], "kind": "原文"}
 ],
 "focus": "争论焦点：争的是“性”指什么——天生倾向还是天生潜能（10 字以上）。",
 "status": "无定论",
 "status_note": "两千年注疏史中两说并存；现代研究多认为二者对“性”的定义不同（15 字以上）。",
 "sources": ["ct-mencious", "ct-xunzi", "sep-mencius"],
 "needs_verification": false, "pending_notes": ""
}
```
- ≥ 2 方，每方 ≥ 1 条理由，`id` 必须是本单元哲学家。
- `status` 用「无定论」「学界主流意见」「已有定论（简述）」之一，并在 `status_note` 说明。不要替读者裁决。

## 五、SVG 规范（每页一张，内联，无外部引用）

- 根元素：`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 760 400'>`（可 760x400 或 760x460）
- 底色 `<rect x='0' y='0' width='760' height='400' fill='#f0f5fa'/>`
- 配色只用：`#f0f5fa`（底）、`#dbe8f3`、`#dce8f4`（填充）、`#1c3a5c`（描边/深字）、`#4a7ba6`（强调/箭头）、`#1e2d3d`（正文文字）
- 允许元素：svg g text tspan rect line path circle defs marker title desc。**禁止** script、image、foreignObject、style、on* 属性、外部 url()
- 所有坐标必须落在 viewBox 内（校验器会逐元素检测越界，容差 2px）
- 箭头写法：
  `<defs><marker id='ar' markerWidth='10' markerHeight='8' refX='9' refY='4' orient='auto'><path d='M0,0 L10,4 L0,8 Z' fill='#4a7ba6'/></marker></defs>`
  再 `<line x1='..' y1='..' x2='..' y2='..' stroke='#4a7ba6' marker-end='url(#ar)'/>`
- 字体大小：标题 18—20，框内 12—14，注释 10—11；不要依赖外部字体
- 图要**表达论证或谱系**，不是装饰：典型画法＝左边“问题/前提”框 → 中间“推理步骤” → 右边“结论”；或自上而下的师承箭头链
- 每个 `<text>` 都要 `text-anchor='middle'`（或 left/right 但坐标留够宽度），中文标签控制在 14 字内，长句拆成两行

## 六、语气与内容纪律

- 中文书面语，学术中性，不煽情、不用"伟大""深刻""划时代"等评价词。
- 写观点就写"他主张……，理由是……"；写争议就并列，不说谁对。
- 不虚构学者姓名与观点；不确定的写"学界有讨论"并标待核实。
- 数字（年份、篇数、人数）要能对上来源；不确定就写"约"并注明依据。
- 每位哲学家的 `era`、`core_questions`、`arguments` 要体现其**独有问题**，不要套话（不要每人都写"如何在变化中寻求不变"）。

## 七、常见返工原因（自查清单）

1. `year_display` 与 `year` 不一致（"约前10世纪" vs -980）→ 写成"约前980年（前10世纪末）"。
2. JSON 里用了 ASCII 引号 `"` 导致解析失败 → 字符串内部一律用中文引号「」或“”。
3. SVG 里 `text` 的 x 或 y 超过 viewBox。
4. 概念 `usages` 两位哲学家写了同一句话。
5. 引用了 sources.json 里没有或未 verified 的 id。
6. `criticisms` 的 sources 少于 2 个。
7. 哲学家 id 用了大写或空格或撇号。
8. 争论 `positions[].id` 指向了本单元之外的哲学家。
