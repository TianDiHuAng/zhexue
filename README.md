# 中外哲学思想脉络库 · 镜花水月

**一个纯静态、零 JavaScript、可离线打开的中外哲学资料库：中国 7 个时期 ＋ 西方 8 个时期 ＋ 印度 1 个单元。**

[![Deploy to GitHub Pages](https://github.com/TianDiHuAng/zhexue/actions/workflows/pages.yml/badge.svg)](https://github.com/TianDiHuAng/zhexue/actions/workflows/pages.yml)
[![Live site](https://img.shields.io/badge/在线站点-tiandihuang.github.io%2Fzhexue-1c3a5c)](https://tiandihuang.github.io/zhexue/)
![Zero JS](https://img.shields.io/badge/JavaScript-0%20行-4a7ba6)
![Sources](https://img.shields.io/badge/来源-432%20条(全部实开核验)-5b8db8)
![Pages](https://img.shields.io/badge/页面-1789-1e2d3d)

> **在线站点：<https://tiandihuang.github.io/zhexue/>**
> 想改内容/接手维护：先读 [HANDBOOK.md](HANDBOOK.md)（实现细节与交接手册）。
> 也可 `git clone` 后直接双击 `site/index.html` —— 无外部依赖、无构建产物运行时、无 JavaScript。

---

## 一、这是什么

按时期整理的哲学思想资料库。每位哲学家一页，按固定九节展开：

> 生卒与时代背景 → 核心问题 → 主要论点（前提 → 推理 → 结论）→ 代表著作及推荐版本 → 影响链（带关系类型）→ 批评与回应 → 常见误解 → 一图（内联 SVG）→ 待核实

另有概念页、争论页、流派页、著作页、比较视野，以及三个区域的双向时间线、世纪视图、思想谱系总图与误读索引。

### 规模（以 `coverage.json` 与各工具输出为准）

| 项 | 数 |
|---|---|
| 时期单元 | **16**（中国 7 · 西方 8 · 印度 1） |
| 哲学家 | **326** |
| 核心概念 | **467** |
| 重要争论 | **127** |
| 流派 | **49** |
| 经典著作页 | **785** |
| 比较视野 | **243** |
| 页面总数 | **1789** |
| 内部链接 / 断链 | **56139 / 0** |
| 来源 | **432（全部实开核验，`verified: true`）** |
| 常见误读条目 | **2295**（哲学家页合计 709 条，**无一人少于 4 条**） |
| 概念层级 `broader` | 199 / 467（43%） |
| 影响关系 `relation` | 588 / 596（99%，其余为并述级，故意留空） |
| 已核销待核实 | **46 条**（逐条记于 `VERIFIED.md`） |

---

## 二、页面类型

| 类型 | 结构 |
|---|---|
| **哲学家页** | 生卒与时代背景 / 核心问题 / 论点（前提→推理→结论）/ 著作与推荐版本 / **影响链（承继·批驳·私淑·同门相诤·重述·影响）** / 批评与回应 / 常见误解 / 一图（内联 SVG）/ 待核实 |
| **概念页** | 定义 / 在不同哲学家处的用法差异（≥2 人，说法须不同）/ 一个具体例子 / **层级（上位·下位）** / 相关概念 |
| **争论页** | 问题是什么 / 各方立场与理由 / 焦点 / 至今是否有定论 |
| **流派页** | 核心主张 / 代表人物 / 兴起与衰落之因 / 常见误解 |
| **著作页** | 文本结构 / 核心论证 / 版本与推荐阅读 / 相关人物 / 常见误读 / **年代异说** / 待核实 |
| **比较视野** | 两方各自的纲 / 最尖锐的差别 / 为何不能互换 / 分寸（并述而不裁定） |

---

## 三、怎么生成的（数据 → 站点）

```
data/                    tools/                      site/
├─ china/*.json   ──►    check.py（22 条规则）   ──►  1789 个静态 HTML
├─ west/*.json           gen_state.py → coverage.json     纯 HTML + CSS
├─ india/*.json          gen_site.py                  零 JS、可离线
├─ schools.json          check_links.py（断链须 0）
├─ works.json            dupcheck / refcheck / srccheck
└─ comparative.json      relcheck / authcheck / gapscan / thincheck / debtreport
```

固定顺序（D53）：**写数据 → `check.py` 零错误 → `gen_state.py` → `gen_site.py` → `check_links.py` → 体检 → 提交**。

本地跑一遍（只需 Python 3）：

```bash
python tools/check.py          # 内容规则：错误须 0
python tools/gen_state.py      # 生成 coverage.json
python tools/gen_site.py       # 生成 site/（约 1800 页）
python tools/check_links.py    # 断链须 0
# 然后直接打开 site/index.html，或 python -m http.server -d site 8000
```

---

## 四、质量关口（每次提交前全跑）

| 工具 | 作用 | 当前结果 |
|---|---|---|
| `tools/check.py` | 22 条内容规则（双源、引文出处、概念层级不成环、关系白名单…） | **错误 0**，警告 312 |
| `tools/dupcheck.py` | id／拉丁名／标题／概念 查重 | 无重复 |
| `tools/refcheck.py` | 所有 id 引用可解析 | 全部有效 |
| `tools/srccheck.py` | 来源登记结构自洽 | 432 条自洽 |
| `tools/check_links.py` | 内部链接 | 56139 条，**断链 0** |
| `tools/relcheck.py` | 著作→人物的「无据挂靠」 | **SUSPECT 0** |
| `tools/authcheck.py` | 著作页是否挂上作者本人 | **CANDIDATE 0** |
| `tools/gapscan.py` | 年代空档扫描 | 中国无空档；其余见 `GAP_SCAN.md` |
| `tools/thincheck.py` | 代表作 ≤1 者 | 26 人 |
| `tools/debtcheck.py` / `debtclass.py` | 待核实清单与**性质分类** | 997 条 / 1208 条（结构 194） |

---

## 五、部署（GitHub Pages）

`.github/workflows/pages.yml` 在每次 `push main` 或手动触发时：

1. **build**：checkout → Python 3.12 → 跑 dupcheck／srccheck／refcheck／check／gen_site／check_links → 上传 `site/` 为 Pages artifact；
2. **deploy**：`actions/deploy-pages@v4` 把 artifact 发布到 GitHub Pages。

> 曾出现 `Failed to create deployment (status: 500)` —— 那是 **GitHub Pages 接口的瞬时服务端错误**（annotation 原文建议"稍后重跑"），与仓库内容无关；后续推送均部署成功。工作流已加**一次自动重试**兜住此类 5xx。

站点地址：**<https://tiandihuang.github.io/zhexue/>**

---

## 六、体例（这个库守什么）

- **原文 vs 后人解读**：每条论点、批评、引文都标注属哪一类。
- **不挂没核过的引文**：著作页具备引文能力（`quotes` 字段＋「原文引文与出处」节），但**目前 0 条** —— 因为可公开核验的全文抓不到（ctext 反爬、维基文库章节抓取失败）。**宁可空着。**
- **双源互证**：每条内容至少两个独立来源；不足者标「待核实」并写明**待核什么**，个别条目在页面上明写「低于本站双源标准」。
- **争议并述不裁定**：作者归属（伪狄奥尼修斯、弥勒五论、伊本·阿拉比《智慧的珍宝》、敦煌本《无生方便门》）、读法之争（《论语》"不患寡而患不均"）一律并列，不替学界下判。
- **同一本书不开两页**：同书异译（《人权论》/《人的权利》）、同概念异译（物自体/自在之物）一律合并，不另立页。

---

## 七、诚实边界（做不到的三处，都写在文件里）

| 缺口 | 情况 |
|---|---|
| **西方 6—8 世纪** | SEP 候选条目 `maximus-confessor`／`john-damascus` 皆 **404**（三次实测） |
| **印度 9—10 世纪** | SEP 逻辑篇全检索 `Udayana`／`Gaṅgeśa`／`Vācaspati` **0 次** |
| **引文 0 条** | 无公开可核全文可引，见上 |

另：**194 条待核实属结构性**（无底本／无原典／"并述即结论"），不是靠再排几轮能消的。

---

## 八、文档索引

| 文件 | 内容 |
|---|---|
| [`HANDBOOK.md`](HANDBOOK.md) | **实现细节与交接手册**：数据字段字典／R1—R23 规则表／工具契约／SOP／发布运维／故障排查／交接清单 |
| [`DELIVERY.md`](DELIVERY.md) | **交付状态总表**：七项目标逐条核对＋「这个库不做什么」五条＋最终验收 |
| [`DECISIONS.md`](DECISIONS.md) | 关键决策 D1—D84（含每条规则的动因） |
| [`VERIFIED.md`](VERIFIED.md) | 已核记录：据哪个来源、核到什么、还差什么 |
| [`GAP_SCAN.md`](GAP_SCAN.md) | 年代空档扫描（按世纪分桶） |
| [`DEBT.md`](DEBT.md) / [`DEBT_CLASSES.md`](DEBT_CLASSES.md) | 待核实清单与性质分类 |
| [`THIN_WORKS.md`](THIN_WORKS.md) | 代表作仅 1 部的哲学家 |
| [`RELCHECK.md`](RELCHECK.md) / [`AUTHCHECK.md`](AUTHCHECK.md) | 关系与作者挂载检查 |
| [`BACKLOG_SOURCES.md`](BACKLOG_SOURCES.md) | 待补来源及**实测结果**（含 404 记录） |
| [`BENCHMARK.md`](BENCHMARK.md) | 同类项目调查（SEP／InPhO／PhilPapers／CBDB／ctext）与吸收清单 |
| [`CHANGELOG.md`](CHANGELOG.md) / [`PROGRESS.md`](PROGRESS.md) | 版本变更与轮次状态 |

---

## 九、许可与引用

- 本站内容为学习整理，**不构成学术结论**；引用请核对原始文献与版本页码。
- 来源条目（`sources.json`）均标注出处与核验状态；引用第三方文本时请遵循其原始许可。

> 体例一句话：**宁可少一页，不破一条规矩；空着比填错好；宁可不挂，不乱挂。**
