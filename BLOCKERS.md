# BLOCKERS.md — 阻塞与已绕过的问题

> 规则：同一问题连续失败 3 次即记此并跳过，不死磕。

## 已绕过（保留记录，供后续轮次避免重犯）

| # | 问题 | 现象 | 处理 |
|---|---|---|---|
| 1 | 子代理上下文耗尽 | 让子代理先读 `sources.json`（12 万字节）再写 8 万字节 JSON，连续 5 次「ran out of room」 | 改为在任务书里**内联 verified 来源白名单**，并禁止整份读 `sources.json`／单元文件，改用 python 载入→append→写回。第 2 轮起 6 个子代理全部一次成功 |
| 2 | ctext.org 反爬 | 并发请求返回 403／2781 字节的空壳页 | 串行 + 间隔 0.5s + 重试；仍失败的中文原典改投**维基文库**（`tools/fill_gaps.py`），并在 sources.json 注明「ctext 反爬时的替代核验源」 |
| 3 | Perseus 403 | `perseus.tufts.edu` 对脚本请求长期 403（403 出现在首次批量抓取之后） | 希腊罗马原典改投 **MIT Classics**（Jowett／Ross 公有领域译本，`tools/add_sources.py`），并在页面注明译者与版本 |
| 4 | SEP 缺条目 | `sep-feuerbach`、`sep-kripke`、`sep-avicenna`、`sep-mozi`、`sep-hanfeizi`、`sep-wang-bi`、`sep-chinese-buddhism-chan`、`sep-tiantai` 均 404 | 改用 **IEP** 对应词条（`iep-kripke`、`iep-avicenna`、`iep-mohist` 等）或哲学史著作；确无专属词条者，条目 `needs_verification=true` 并写明「无专属百科来源」 |
| 5 | 维基文库个别页面抓不到目标串 | `ws-chongyoulun`（《晋书》卷三十五）、`ws-qiusu`（《訄书》）未通过关键词校验 | 改用同单元其他已验证来源（`ws-shishuoxinyu`、`ws-liuzutanjing`、`book-chan-sourcebook` 等），不虚报核验 |
| 6 | 生成器格式化字符串中的 `%` | 表头 `style="width:30%"` 与 `%` 格式化冲突，抛 `ValueError: unsupported format character` | 移除内联宽度样式，改由 CSS 控制列宽 |
| 7 | 页面层级（depth）错配 | `graph.html`／`about.html` 位于站点根目录却按 depth=1 渲染，导致 29 条断链 | 改为 depth=0；`tools/check_links.py` 全量核验（7422→8716 条链接，0 断链），此类问题列为每轮体检固定项 |
| 8 | 概念页 `related` 只渲染裸 id | 生成 `href="cn-xxx"` 造成 259 条断链 | 渲染时查表取概念名并补 `concepts/<id>.html` 路径 |

## 未解决（不影响当前交付）

| # | 问题 | 现状 | 后续 |
|---|---|---|---|
| A | 希腊罗马原典的权威校勘本页码 | 只能用公有领域英译定位，无法核对 OCT／Loeb 页码 | 若日后需要精确引用，须逐条核对纸本校勘本 |
| B | 伊斯兰与拜占庭哲学覆盖薄 | 阿维森纳已入（第 2 轮），阿威罗伊、奥利金、波菲利、普罗克洛仍无独立条目 | 列入 BACKLOG（下一轮） |
| C | 女性哲学家占比低 | 现有 90→ 位中女性为 0（波伏瓦、安斯康姆已在来源中，未成页；`gr-20c` 已满 8 人） | 第 2 轮 BACKLOG 的 C6：或调整单元上限，或开设「女性哲学家」专题页 |
