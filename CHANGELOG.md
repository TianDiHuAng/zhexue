# CHANGELOG.md —— 里程碑变更

只记**结构性**变化（新增区域/维度/工具/规则），不记每轮的常规增量。逐轮细节见 `REPORT.md` 与 `PROGRESS.md`。

## v1.2（第 300—343 轮）
- **新增第三区域：印度哲学**（单元 15 → 16）
  - 架构：`gen_site.py` 三区域化（`REGIONS/REG_LABEL/REG_ORDER/REG_FILL`、`present_regions()`）；导航与时间线**按区域动态生成**；`check.py` 允许 `region/tradition = india`，且单元发现改为遍历三区域（此前只扫 china/west，印度单元会被静默漏检）。
  - 人物 12 人：乔答摩 · 世亲 · 龙树 · 鸠摩利罗 · 商羯罗 · 陈那 · 法称 · 无著 · 月称 · 清辨 · 筏差衍那 · 阇弥尼。
  - 著作：正理经 · 颂释补 · 唯识二十论 · 广破论 · 明句论 · 集量论 · 释量论 · 吉祥注 · 正理注 · 梵经注 · 弥曼差经（＋补挂中论、俱舍论、摄大乘论、瑜伽师地论）。
  - 争论 9 场（知觉是否带概念／语言能否触及实在／有我无我／量有几种／梵有属性吗／解脱是知还是行／语言无作者吗／恩典与自力／**阿赖耶识是实有吗**）。
  - **流派 5 个**：佛教量论 · 中观 · 瑜伽行 · 正理 · 吠檀多 · 弥曼差（正统六派＋佛教三家全部落页）。
- **新维度：概念层级**（`concepts[].broader`）—— 借 PhilPapers 分类树；**R21** 校验（同单元／不自指／**成环检测**）；概念页新增「概念的层级」。已回填 **166 条**。
- **新维度：影响关系类型**（`influenced_by/influenced[].relation`）—— 借 InPhO 多重关系；**R22** 白名单（承继／批驳／重述／同门相诤／私淑／影响）。已标 **303 / 443 条**，且**两侧镜像**（受谁影响／影响了谁 显示一致）。
- **新维度：著作年代异说**（`works[].date_note`）—— 借 CBDB 异说并记；**R23** 要求 ≥10 字。
- **新页：世纪视图**（`timeline/century.html`，零 JS 表格；空世纪如实写「（此处空）」）。
- **新工具**：`tools/gapscan.py`（年代空档扫描 → `GAP_SCAN.md`）、`tools/debtclass.py`（欠账按"为何待核"分类 → `DEBT_CLASSES.md`）、`tools/thincheck.py`（代表作 ≤1 → `THIN_WORKS.md`）。
- **新文档**：`BENCHMARK.md`（外部对标）、`GAP_SCAN.md`、`DEBT_CLASSES.md`、`VERIFIED.md`（已核记录）。
- **中国年代空档清零**：补入宋初三先生之二（孙复·胡瑗）、元代吴澄、明初薛瑄。
- **规则**：D75（CI 失败根因＝Pages 未启用）、D76（SEP 无 Freud 专条→不凑第二来源）、D77（著作页引文能力，**未核不挂**）、D78/D79（三区域架构）、D80（外部对标：学结构不搬数据）、D81（四项全吸收）、D82（欠账先分类再核销）。

## v1.1（第 100—299 轮）
- 单元 8 → 14（中国 6 时期 ＋ 西方 8 时期）。
- 新增维度：经典著作页（`data/works.json`）、比较视野（`data/comparative.json`）、流派页（`data/schools.json`）、思想谱系总图。
- 规则与工具：`dupcheck.py`（D61）、`refcheck.py`（D62）、`srccheck.py`（D67）、`debtcheck.py`（D72）、`precheck_src.py`（D60 前置查重）。
- 体例成型：原文/后人解读二分、引文 ≤60 字须原典、双源互证、并述不裁定。

## v1.0（第 1—99 轮）
- 8 个单元、90 位哲学家、121 概念；322 页、177 来源。
- 纯静态零 JS 站点骨架（`gen_site.py`）、校验器首版（`check.py`）、链接核验（`check_links.py`）。

## 第 447 轮（交付整理）

- **重写 `README.md`**：作为项目门面（在线站点链接、徽章、规模表、页面类型、数据→站点流程图、本地运行命令、质量关口表、部署说明、体例、诚实边界、文档索引）
- **新增 `.gitignore`**：忽略 `__pycache__/`、`*.pyc`、`_tmp_*.py`、`tools/_tmp_*.py`、`.DS_Store`
- **清理**仓库内遗留的一次性脚本：`_tmp_add_pascal.py`、`tools/_tmp_add_{pascal,engels,kripke}.py`，以及被误提交的 `tools/__pycache__/*.pyc`
- **`pages.yml` 增加部署重试**：`deploy-pages` 首次失败 → 等 15 秒 → 重试一次；两次都失败才判定失败（应对 GitHub Pages 接口偶发 500）
- 复跑校验：`check.py` 错误 0／1789 页／56139 链接 0 断链／查重无重复
