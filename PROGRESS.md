# PROGRESS.md — 阶段进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| 0 | 读参考工作流（`WORKFLOW.md`）与旧样板库（`history/`），确定架构与配色 | ✅ |
| 1 | `scope.md` 入选清单（14 单元）、`DECISIONS.md`、`prompts/unit-task.md` | ✅ |
| 1b | 联网检索建 `sources.json`：177 条，**169 条 verified**（逐条 HTTP 打开 + 关键词核对，证据写入 `verify` 字段） | ✅ |
| 2 | `tools/check.py`（R1—R16 规则 + 双源 + 引文出处 + SVG 越界） | ✅ |
| 3 | 样板：中国「先秦诸子」+ 西方「古希腊哲学」，通过校验后继续 | ✅ |
| 4 | 逐时期写完 14 单元（中国 6 + 西方 8） | ✅ |
| 5 | 时间线×2、概念索引、哲学家索引、争论索引、流派索引、思想谱系总图、来源页、体例页 | ✅ |
| 6 | `tools/gen_site.py` 生成 322 页；`tools/check_links.py` 全站 7422 条内部链接 **0 断链** | ✅ |
| 7 | `REPORT.md`、`README.md`、逐单元 git commit | ✅ |

## 内容规模

- 时期单元 **14**（中国 6 / 西方 8）
- 哲学家页 **90**、概念页 **121**、争论页 **42**、流派页 **43**
- 时间线 2、索引页 3、谱系总图 1、来源页 1、体例页 1、首页与区域页 3
- 生成页面合计 **322**

## 校验状态

```
单元文件：14；来源：177 条（verified 169）；错误 0；警告 4
页面 322；内部链接 7422；断链 0
```

4 条警告均为「某概念的用法条目只写了对照人物、未关联本单元哲学家 id」（如「近代机械论者（对照）」「柏拉图（对照）」），属**有意保留**的对照性用法说明，不影响内容正确性。

## 阶段4 的单元提交（每单元一次 commit）

`cn-xianqin`（样板）→ `gr-ancient`（样板）→ `cn-weijin` → `cn-songming` → `gr-medieval` → `gr-modern` → `cn-lianghan` → `cn-qingmod` → `gr-hellenistic` → `gr-german` → `gr-19c` → `gr-20c` → `gr-suitang` → `gr-contemp` → 索引与总图。

ALL_DONE
