# HANDBOOK.md —— 实现细节与交接手册

> 给**接手这个仓库的人**（包括几周后的我自己）看的一份操作手册。
> 想先了解"这是什么库"，看 [README.md](README.md)；想了解"交付到什么程度"，看 [DELIVERY.md](DELIVERY.md)；想了解"为什么这样定规矩"，看 [DECISIONS.md](DECISIONS.md)。
> **本文档讲的是：代码怎么跑、数据长什么样、规则怎么守、坏了怎么修。**

---

## 1. 一分钟上手

```bash
git clone git@github.com:TianDiHuAng/zhexue.git
cd zhexue

python tools/check.py          # 期望：错误 0（警告为信息性，可忽略）
python tools/gen_state.py      # 生成 coverage.json（唯一真源）
python tools/gen_site.py       # 生成 site/：约 1789 页
python tools/check_links.py    # 期望：断链 0
python -m http.server -d site 8000   # 打开 http://localhost:8000
```

坏了的判断标准（全部为**硬门槛**）：

| 命令 | 期望输出 |
|---|---|
| `check.py` | `错误 0`（警告数不设门槛，当前 312） |
| `check_links.py` | `断链 0` |
| `dupcheck.py` | `未发现重复` |
| `refcheck.py` | `全部引用有效` |
| `relcheck.py` | `SUSPECT 0` |
| `authcheck.py` | `CANDIDATE 0` |

---

## 2. 架构：四层，单向依赖

```
data/（唯一内容源，JSON）  ──►  tools/（校验 + 生成，Python 3）  ──►  site/（产物，纯静态）  ──►  GitHub Pages
        ▲                                                                  │
        └──────────────────── 只改 data，不改 site ─────────────────────────┘
```

**铁律：`site/` 是产物，永远不手改。** 改内容只改 `data/**`，然后重生成。
（`site/` 确实被提交进仓库，那是为了"clone 后能离线双击打开"；CI 每次会用 `data/` 重新生成一遍。）

### 目录职责

| 路径 | 是什么 | 备注 |
|---|---|---|
| `data/china/*.json` | 中国 7 个单元 | 每单元一个文件 |
| `data/west/*.json` | 西方 8 个单元 | |
| `data/india/in-india.json` | 印度 1 个单元 | |
| `data/schools.json` | 流派（49） | 跨单元引用 |
| `data/works.json` | 著作页（785） | 跨单元引用 |
| `data/comparative.json` | 比较视野（243） | 单独渲染成一页 |
| `sources.json` | 来源登记（432） | `verified: true` 才可用于双源互证 |
| `coverage.json` | 由 `gen_state.py` 生成 | **一切统计数字以此为准** |
| `tools/*.py` | 校验器与生成器 | 见 §5 |
| `site/**` | 生成的静态站 | 1789 页，零 JS |
| `.github/workflows/pages.yml` | CI：校验 → 生成 → 发布 Pages | 见 §9 |

---

## 3. 数据模型（字段字典）

### 3.1 单元文件 `data/{china,west,india}/<unit>.json`

```jsonc
{
  "unit_id": "cn-xianqin",          // 必填，a-z0-9-，全局唯一
  "region": "china",                // china | west | india
  "title": "先秦诸子",
  "period": "前6世纪—前221",
  "start_year": -600, "end_year": -221,
  "summary": "……（单元导语）",
  "threads": [ … ],                 // 线索/主线（渲染在单元页）
  "philosophers": [ … ],            // 见 3.2，每个单元 4—60 人（R7 下限 4）
  "concepts":     [ … ],            // 见 3.3，每个单元 6—30 个
  "debates":      [ … ]             // 见 3.4，每个单元 2—12 场
}
```

> 计数上下限由 `check.py` R7 约束，**实际值是：哲学家 4—60 / 概念 6—30 / 争论 2—12**（源码 docstring 写的 4-8／6-10／2-3 是旧值，以代码为准）。**改单元结构时注意别越界。**

### 3.2 哲学家 `philosophers[]`

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | 形如 `cn-xianqin-kongzi`，**必须以单元前缀开头**，全局唯一（R9/R16） |
| `name` / `latin` | ✅ | 中文名 / 拉丁或拼音 |
| `birth_year` / `death_year` | ✅ | 整数，公元前为负数 |
| `birth_display` / `death_display` | ✅ | 人类可读，必须与 year 一致（R8） |
| `birth_note` / `death_note` | | 异说注（有争议时必写） |
| `era` | ✅ | 时代背景段落 |
| `school` | ✅ | 所属流派（文本，与 `schools.json` 呼应） |
| `core_questions` | ✅ | 2—3 条，**每条 ≥10 字** |
| `arguments[]` | ✅ | 每项：`claim` / `premises[]` / `inference` / `conclusion` / `kind`（**原文** 或 **后人解读**） |
| `works[]` | ✅ | 每项：`title` / `edition` / `note`（**必须是 dict，不能是字符串**，R19 只对 `works_detail` 校验） |
| `works_detail[]` | | 每项：`title` / `year` / `date` / `structure` / `core_thesis` / `editions` / `note` —— **`structure`、`core_thesis`、`editions` 必填**（R19） |
| `influenced_by[]` / `influenced[]` | ✅ | 每项：`name` / `id` / `note`；`id` 必须存在（R11）；`note` 里的关系词须在**白名单**：承继／批驳／重述／同门相诤／私淑／影响（R22） |
| `criticisms[]` | ✅ | 每项：`critic` / `view` / `response` / `kind` / `sources[]` |
| `misconceptions[]` | ✅ | 每项：`claim`（常被误认为什么）/ `why`（为什么不是）；**每页 ≥2 条**，当前平均 4—5 条 |
| `quotes[]` | | 每项：`text` / `source_id` / `locator` / `kind`；**单条 ≤60 字**，须有原典出处（R4）。**目前全库 0 条** |
| `svg` / `svg_caption` | ✅ | 内联 SVG 一图；须为合法 XML、只用白名单元素、坐标不越界（R6） |
| `sources[]` | ✅ | 来源 id，**≥2 且皆 `verified: true`**（R12） |
| `needs_verification` + `pending_notes` | ✅ | 见下方 R10：两者必须**联动** |
| `doctrine` | ✅ | `summary` / `system` / `phases` / `reception`，供"学说的系统"展示 |

### 3.3 概念 `concepts[]`

`id` / `term` / `term_latin` / `definition` / `usages[]` / `related[]` / `example{}` / `sources[]` / `needs_verification` / `pending_notes` / `broader`（可选）

- `usages[]`：**≥2 位**哲学家，且**说法必须不同**（R14）；每项 `name` / `id`（本单元必须存在，R11）/ `usage`
- `related[]`：必须是**本单元内**的概念 id（R11）
- `broader`：同单元内上位概念 id；**不得成环**（R21）。当前 199/467 有值，其余多为顶层概念

### 3.4 争论 `debates[]`

`id` / `title` / `question` / `positions[]`（**≥2 方**）/ `focus` / `status` / `status_note` / `sources[]` / `needs_verification` / `pending_notes`

### 3.5 流派 `data/schools.json` → `schools[]`

`id` / `name` / `region` / `era` / `unit` / `core_claims[]` / `representatives[]` / `rise` / `decline` / `misconceptions[]` / `sources[]` / `needs_verification` / `pending_notes`

### 3.6 著作 `data/works.json` → `works[]`

`id` / `title` / `title_original` / `tradition`（china|west|india）/ `date_display` / `structure` / `core_arguments[]` / `key_points[]`（`locator`+`point`）/ `editions[]` / `related_people[]`（**必须包含作者本人**，见 `authcheck`）/ `misreadings[]`（**≥2 条**）/ `sources[]`（≥2）/ `needs_verification` / `pending_notes` / `sort_year` / `date_note`（年代有异说时 **≥10 字**，R23）

### 3.7 比较视野 `data/comparative.json` → `essays[]`

`id` / `title` / `question`（**≥10 字**）/ `sections[]`（每项 `heading`+`text`，**text ≥80 字**）/ `caveat` / `sources[]` / `needs_verification` / `pending_notes`（**必须有**）

### 3.8 来源 `sources.json` → `sources[]`

`id` / `title` / `author` / `year` / `year_note` / `publisher` / `type`（**原典｜百科｜论文｜学术著作**）/ `url` / `url2` / `link_ok` / `verified` / `note` / `unit_hint` / `verify{method,http_status,checked_at,keyword,keyword_seen}` / `n`

> `type` 只允许上述四种，写别的 `srccheck.py` 会报"type 不在允许集合"（踩过一次）。

---

## 4. `check.py` 的规则清单（R1—R23）

> 规则不止"写在文件头"，而是**每条都真跑**（源码里的报错都带规则号）。改数据前先扫一眼。

| 规则 | 内容（按源码实际实现） | 常见触发与修法 |
|---|---|---|
| R1 | 各类型对象的必填字段非空 | 漏字段；按报错指出的字段补 |
| R2 | 年份合法：整数（公元前为负）、生 ≤ 卒、年份在合理范围；单元 `start_year < end_year`；人物生卒不应远超单元范围 | 写成年份字符串；把 `-551` 写成 `551` |
| R3 | `sources` 里的来源 id 必须在 `sources.json` 中**存在** | 先登记来源再引用 |
| R4 | 引文须有 `locator`（原典出处），且**来源类型必须是「原典」**（`type=原典`） | 想引研究著作 → 应写成"后人解读"而非引文 |
| R5 | 单元内同名检测（人物/概念等同名） | 同名不同人 → 加限定语 |
| R6 | SVG 合法性：可解析 XML、只用白名单元素、坐标不越界 | 手写 SVG 少闭合标签、用 `<foreignObject>` |
| R7 | 单元计数：**哲学家 4—60 / 概念 6—30 / 争论 2—12** | 超上限或不足下限 |
| R8 | `birth_display`/`death_display` 与 `*_year` 一致 | 改年份忘改 display |
| R9 | 全局 id 唯一（人物、概念、争论、著作、流派、比较篇共用一个命名空间） | **概念 id 与争论 id 撞车**也报这条 |
| R10 | `needs_verification` 与 `pending_notes` 联动：`true` 而 pending 空 → **ERROR**；`false` 而 pending 非空 → **WARN** | 按纪律：既然写了"待核"，就应置 `true` |
| R11 | 内部引用目标必须存在（人物/概念/争论/流派 id，概念 `related` 还须**在本单元内**） | 引用别单元概念；人名 id 拼错 |
| R12 | 双源：`sources` 去重后 **≥2**；不足 2 个时，**必须**同时满足 `needs_verification=true` 且 `pending_notes` 非空 | 单源条目 → 补源，或按上述"如实标低" |
| R13 | 流派页结构完整（`kind` 取值须为 原文/后人解读 等） | 缺 `rise`/`decline`；kind 写了别的词 |
| R14 | 概念用法差异：`usages` **≥2 位**哲学家，且**说法不得重复** | 两人用法写一样 → 判为"未体现差异" |
| R15 | 争论结构：`positions` ≥2 方、有 `focus`、有 `status`/`status_note` | 只有一方 = 不是争论 |
| R16 | id 字符集 `^[a-z0-9][a-z0-9-]*$` | 用了大写、下划线、中文 |
| R17 | `works.json` 总量 ≥10，且每条著作含必填字段（`title`/`title_original`/`tradition`/`date_display` …） | 新著作漏 `title_original` 或 `tradition` |
| R18 | `comparative.json` ≥2 篇，且每篇含 `title`/`question`/`sections`/`caveat`/`sources`，分节文字有最小长度 | 节文字过短（曾因 76 字被拦） |
| R19 | 结构类必填：`doctrine` 四字段（`summary`/`system`/`phases`/`reception`）且 `system` ≥2 条；`works_detail` 每项须有 `structure`/`core_thesis`/`editions` | 只写 `title`+`note` 必报 |
| R20 | 著作引文结构：`text`/`source_id`/`locator`/`kind` 齐全，且来源须为「原典」 | 引文挂到百科条目上会被拒 |
| R21 | `broader`：须指向**同单元**概念，且**不得成环** | 跨单元挂父；A→B→A 循环 |
| R22 | 影响链关系类型白名单：承继／批驳／重述／同门相诤／私淑／影响 | 写了"影响深远""相关"这类自由词 |
| R23 | 著作年代异说须写 `date_note`（**≥10 字**） | 有异说却不注明 |

> 源码文件头的 docstring 里 R7 那行还写着旧上限（4-8/6-10/2-3），**以代码为准**（见 §12 交接注意）。

**警告（WARN）不是错误**：多半是"单源""某字段偏短"之类的提示，当前 312 条属历史遗留。**别为了清零而注水。**

---

## 5. 工具契约

| 工具 | 输入 | 输出 | 失败语义 | 何时跑 |
|---|---|---|---|---|
| `check.py` | `data/**`、`sources.json` | 逐条 ERROR/WARN + 汇总 | 有 ERROR → `exit 1` | 每次改数据 |
| `gen_state.py` | `data/**` | `coverage.json` | 无 | 改数据后 |
| `gen_site.py` | `data/**` + `sources.json` | `site/**` | 无（需先过 check） | 改数据后 |
| `check_links.py` | `site/**` | 页面数 / 链接数 / 断链数 | 断链 >0 → `exit 1` | 生成后 |
| `dupcheck.py` | `data/**` | 重复清单 | 有重复 → `exit 1` | **新建实体名前** |
| `refcheck.py` | 全库 | 悬空引用清单 | 有悬空 → `exit 1` | 改引用后 |
| `srccheck.py` | `sources.json` | 登记结构检查 | 有结构问题 → `exit 1` | 加来源后 |
| `precheck_src.py` | 传入标题/id 列表 | 撞名预警 | 断言失败 → `exit 1` | **写新页前**（D60） |
| `relcheck.py` | 著作→人物 | `RELCHECK.md`（SUSPECT） | 无（人工判） | 改 `related_people` 后 |
| `authcheck.py` | 著作→作者 | `AUTHCHECK.md`（CANDIDATE） | 无（人工判） | 同上 |
| `gapscan.py` | 人物生年 | `GAP_SCAN.md` | 无 | 加人物后 |
| `thincheck.py` | 著作关联 | `THIN_WORKS.md` | 无 | 改关联后 |
| `debtcheck.py` | `needs_verification` | `DEBT.md` | 无 | 每轮 |
| `debtclass.py` | 同上 | `DEBT_CLASSES.md`（按"为何待核"分类） | 无 | 每轮 |

---

## 6. 生成器实现要点（`tools/gen_site.py`，1062 行）

- **无模板引擎**：全部 f-string 拼接，函数按页型划分：
  `render_person` / `render_concept` / `render_debate` / `render_school` / `render_unit` / `render_work` / `render_comparative` / `render_century_timeline` / `render_timeline` / `render_sources` / `render_about` / `render_graph`（纯 SVG 谱系图）/ `render_home` / `render_region` / 四个索引页 / 误读索引。
- **骨架函数**：`head()`（`<head>` + CSS 链接）、`header()`（全站导航，含世纪视图入口）、`page()`（拼标题与 `<h1>`）、`footer()`、`rel(depth)`（相对路径前缀，站点在子目录也能用）。
- **样式**：单一 `site/assets/style.css`；调色板固定（`--ink #1e2d3d / --paper #f0f5fa / --navy #1c3a5c / …`）。
- **零 JS**：全站无 `<script>`；交互仅靠 CSS 与链接。
- **SVG**：人物页的"一图"为内联 SVG，直接写在 JSON 的 `svg` 字段；渲染时原样输出，合法性由 R6 兜。
- **链接**：所有内部链接由 `rel(depth)` + 目标相对路径生成；`check_links.py` 事后全量核验。
- **确定性**：同样的 `data/` 必得同样的 `site/`（无时间戳、无随机），差分不会出现噪声改动。

---

## 7. 标准作业程序（SOP）

### 7.1 新增一位哲学家

1. **先查重**：`python -c "from tools.precheck_src import find_work_conflicts"` 或直接 `python tools/dupcheck.py`；用 `precheck_src.py` 断言 id/标题不存在（D60）。
2. 在对应单元 JSON 的 `philosophers[]` 追加对象；`id` 以单元前缀开头。
3. 九个板块**都要有**：`era` / `core_questions` / `arguments`（≥1，标 kind）/ `works`（dict）/ `influenced_by`·`influenced`（关系词走白名单）/ `criticisms` / `misconceptions`（**≥2**，实际写 4 条最佳）/ `svg` / `pending_notes`。
4. `sources[]` 填 **≥2 个已 verified 的来源**；不足就在 `pending_notes` 明写"低于双源标准"并把 `needs_verification` 置 `true`。
5. 跑 `check.py`；按报错逐条修（R10/R11/R14/R22 最常见）。
6. 若新开了著作页：改 `data/works.json`，`related_people` **务必含作者本人**，再跑 `authcheck.py`。
7. 跑 `relcheck.py`、`gapscan.py`、`thincheck.py` 更新派生清单。
8. `gen_state.py` → `gen_site.py` → `check_links.py`。
9. 提交：`第N轮：<一句话>`。

### 7.2 新增一个概念

- **≥2 位本单元哲学家**的 `usages`，且**说法必须不同**（R14）。
- `related[]` 只能指本单元已有概念（R11）。
- 若概念名与其他区域已有术语撞车（如"共相""三性""佛性"），**改名加括注**（如「共相（jāti／sāmānya）」），别硬开第二页（D60/D61）。
- 想加 `broader`：只能指本单元概念，且不能成环（R21）。

### 7.3 新增著作页

- 先查同书异译（《人权论》/《人的权利》）、同名异书（徐幹《中论》vs 龙树《中论》）——**同书不开两页；同名异书要分清**（D71）。
- `misreadings` **≥2 条**；`sources` ≥2；有年代异说就写 `date_note`（≥10 字，R23）。
- `related_people` 必须含**作者本人**（`authcheck.py` 会告警 CANDIDATE）。

### 7.4 新增比较篇

- `question` ≥10 字；每节 `text` ≥80 字；`pending_notes` **必填**。
- 标题里若含在册篇目的关键词，会触发 D70 语义护栏 —— **撞题就撤，撞词则收窄关键词并说明论理不同**。

### 7.5 新增来源

1. **实开核验**（`web_fetch` 或等价手段）：记录 HTTP 状态与命中关键词。
2. 写 `verify{method,http_status,checked_at,keyword,keyword_seen}`，`verified: true` 仅在**真打开且正文含预期关键词**时置真。
3. `type` 只能用 `原典｜百科｜论文｜学术著作`。
4. 抓不到就**不登记**，并把实测结果写进 `BACKLOG_SOURCES.md`（已有先例：SEP 的 404、ctext 反爬、维基文库无《正蒙》页）。

---

## 8. 数字口径（唯一真源）

| 数字 | 真源 | 谁需要同步 |
|---|---|---|
| 单元/人物/概念/争论/流派/来源 | `coverage.json`（`gen_state.py` 生成） | README、DELIVERY、CHANGELOG |
| 页面数/链接数/断链 | `check_links.py` 输出 | README、DELIVERY、REPORT |
| 著作/比较篇 | `data/works.json`、`data/comparative.json` | README、DELIVERY |
| `broader` 覆盖 | 手工统计脚本或 `gen_state.py` | README、DELIVERY |
| 待核实 | `debtcheck.py`（`DEBT.md`，人物/著作/比较）与 `debtclass.py`（`DEBT_CLASSES.md`，含概念与争论） | **两个口径不可相减** |
| 已核销 | `VERIFIED.md` 的条目数 | README、DELIVERY |

> **写报告时只抄工具输出，不抄记忆。** 第 427 轮就因为抄记忆，把 `DEBT_CLASSES` 1183 写成真值（实为 1185）。

---

## 9. 发布与运维

`.github/workflows/pages.yml`：

```
push main ──► build（checkout → py3.12 → dupcheck → srccheck → refcheck → check → gen_site → check_links → upload artifact）
                 └──► deploy（deploy-pages 首次尝试；失败则等 15s 重试一次；两次皆失败才 exit 1）
```

| 场景 | 处理 |
|---|---|
| `Failed to create deployment (status: 500)` | GitHub Pages 接口瞬时故障。**重跑即可**；工作流已内置一次重试 |
| 部署成功但页面没变 | 检查 `site/` 是否真的重生成；`gen_site.py` 是否跑过；浏览器缓存 |
| 想手动发一版 | Actions → Deploy to GitHub Pages → **Run workflow** |
| 回滚 | `git revert <commit>` 后推送；或在 Actions 里对旧 commit 重跑 |
| 站点地址 | https://tiandihuang.github.io/zhexue/ （Pages 源 = GitHub Actions） |

---

## 10. 故障排查速查

| 现象 | 原因 | 处理 |
|---|---|---|
| `'str' object has no attribute 'get'`（check 崩） | 某处把 dict 列表写成了字符串列表（如 `works`／`works_detail`） | 改回 dict 列表 |
| `SyntaxError: invalid character '《'` | 一键脚本里用英文双引号套中文引号 | 改用「」，或写成 `.py` 文件再跑 |
| `R10`：填了 pending 却 `needs_verification=false` | 认了待核却标已核 | 改 `true` |
| `R11`：`related` 不在本单元 | 引用了别单元的概念 | 改本单元 id 或删 |
| `R19`：`works_detail` 缺 `structure/core_thesis/editions` | 只写了 `title/note` | 补齐四字段 |
| `D60 拦截 标题` | 与在册页同书异译/同概念异译 | **整篇不写**，或合并进已有页 |
| `D70 语义提醒` | 标题与在册篇目撞题 | 撞题撤稿；仅撞词则收窄关键词并说明论理不同 |
| 断链 >0 | 删页/改 id 后未重生成 | 重跑 `gen_site.py`；再 `check_links.py` |
| `authcheck` CANDIDATE >0 | 著作页没挂作者本人，或真漏 | 逐条判：该补就补，同名异书则加进 `KNOWN_HOMONYM` |
| `relcheck` SUSPECT >0 | 跨区域挂了正文没提的人 | 删掉，或在正文补出该人 |
| ctext 抓不到 | 站点反爬（明确禁止抓取） | **不抓**；换维基文库或纸本，或标待核 |

---

## 11. 已知边界（别试图"补齐"这些）

1. **西方 6—8 世纪 / 印度 9—10 世纪**：无可引来源（SEP 实测 404 / 检索 0 次），见 `BACKLOG_SOURCES.md`。
2. **引文 0 条**：无公开可核全文，**不挂未核引文**。想挂引文，必须先拿到可核文本。
3. **194 条结构性待核**（无底本/无原典/并述即结论）：不是工作量问题。
4. **`broader` 43%**：余者多为顶层概念，硬挂即编造。
5. **`relation` 余 8 条**：属"并称级"，无师承或诤论记载，故意留空。

---

## 12. 交接清单

**接手第一小时**

- [ ] 读 `README.md`（是什么）→ `DELIVERY.md`（到哪了）→ 本文（怎么动）
- [ ] 跑一遍 §1 的六条命令，确认本地全绿
- [ ] 打开 `DECISIONS.md` 扫 D53—D84 的标题（每条规则都写明了动因）
- [ ] 看一次 Actions 最近一次运行

**每次改动前**

- [ ] 新实体先 `dupcheck` / `precheck_src`（撞名是最高频的返工原因）
- [ ] 只改 `data/**`，不改 `site/**`
- [ ] 改完跑完整链：`check → gen_state → gen_site → check_links`

**每次提交后**

- [ ] 更新 `REPORT.md`（本轮做了什么、拦下什么、数字变化）
- [ ] 更新 `PROGRESS.md`（下一步起点）
- [ ] `SATURATION.json` 追加一条轮次记录
- [ ] 每 5 轮做一次"体检"并更新 `HEALTH_STATE.json`（当前节奏：第 91 次在 444 轮，下次 449）

**绝不要做**

- ❌ 手改 `site/`（会被覆盖）
- ❌ 为清零警告而注水内容
- ❌ 为填空档而编造人物/著作
- ❌ 批量把 `needs_verification` 置 `false`
- ❌ 挂没有 `locator` 的引文
- ❌ 同一本书/同一个概念开两页
- ❌ 把 `DEBT`（997）与 `DEBT_CLASSES`（1208）两个口径相减

---

## 13. 术语与决策索引

- **D53**：固定生产顺序（数据→check→state→site→links→提交）
- **D60/D61**：新建实体前必须断言 id 与标题全库不存在
- **D62**：引用有效性
- **D69/D70**：比较篇的 id 与语义双重护栏
- **D71**：同名异书要分清、同书异译要合并
- **D72**：`debtcheck` 口径
- **D73**：R10（`needs_verification` 与 `pending_notes` 联动）
- **D74**：派生清单必须由工具生成，不手写
- **D75**：CI 红 = Pages 未启用（当时的问题）
- **D76**：无 SEP 条目的思想家不建页（如弗洛伊德）
- **D77**：著作页支持 `quotes`，但没核过就 0 条
- **D78/D79**：三区域架构
- **D80**：外部项目对标（借结构不借数据）
- **D81**：四项吸收
- **D82**：欠账先分类再核销
- **D83**：`relcheck`（无据挂靠）
- **D84**：`authcheck`（著作页须挂作者本人）

> 完整条文见 [DECISIONS.md](DECISIONS.md)。

---

**最后一句**：这个库的价值不在"页数多"，而在**每一页都说得清它凭什么是这样说的**。改内容时若犹豫，宁可少写一条，也不要写一条说不出出处的。
