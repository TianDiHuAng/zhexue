# DEBT_CLASSES.md —— 欠账按「为何待核」分类（工具生成，勿手改）

`DEBT.md` 给的是总量；本表回答**哪些能核、哪些核不了**。

分类按 `pending_notes` 的关键词判定，规则顺序即优先级（先判硬阻塞）。

| 类别 | 条数 | 能否核销 |
|---|---|---|
| A 无底本（原书已佚／仅存辑本） | 44 | **不能**（底本已佚） |
| B 无原典可读（未读梵本／未校原书） | 37 | **不能**（缺原典） |
| C 版本与篇次（须核校本） | 782 | 需**校外书**（站内无该文本时，能核者有限） |
| D 生卒与年代推定 | 51 | **部分能**（若有专门研究） |
| E 归属与真伪（托名／作者问题） | 21 | **部分能**（若有研究） |
| F 解释分歧（本页只作并述） | 57 | **不能**（本页的写法即结论：并述不裁定） |
| G 无专门研究（只有语境性引用） | 7 | **不能**（须先有专门研究） |
| Z 其他 | 103 | 待判 |
| **合计** | **1102** | |

## 结论

**其中 665 条的条目已挂着「原典」类来源** —— 这些是最有望先核的一批（有底本线索）。

**145 / 1102 条属「结构性待核」**（无底本、无原典、本页即作并述、无专门研究）——这些不是欠账，是**方法的边界**：在拿到材料之前，它们的正确写法就是「待核实」。

可动的只有 **版本篇次（C）** 与部分 **生卒（D）／归属（E）**。每轮只挑其中的少数去核，并在 `VERIFIED.md` 记「已核（第 N 轮，据 source_id）：内容」。

## A 无底本（原书已佚／仅存辑本）（44 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 两汉经学与气论 | `cn-lianghan-huan-tan` | 桓谭 |
| 哲学家 | 两汉经学与气论 | `cn-lianghan-liu-xiang` | 刘向 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-daosheng` | 竺道生 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-sengchou` | 僧稠 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-baochang` | 宝唱 |
| 概念 | 南北朝佛道与形神之争 | `cn-nanbei-yichanti` | 一阐提成佛 |
| 概念 | 南北朝佛道与形神之争 | `cn-nanbei-baihei` | 白黑论 |
| 哲学家 | 魏晋玄学 | `cn-weijin-xiangxiu` | 向秀 |
| 概念 | 魏晋玄学 | `cn-weijin-caixing` | 才性四本 |
| 概念 | 魏晋玄学 | `cn-weijin-yan-jin-yi` | 言尽意 |
| 概念 | 魏晋玄学 | `cn-weijin-jise` | 即色 |
| 概念 | 魏晋玄学 | `cn-weijin-xinwu` | 心无 |
| … | | | 余 32 条 |

## B 无原典可读（未读梵本／未校原书）（37 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 宋明理学与心学 | `cn-songming-wu-cheng` | 吴澄 |
| 哲学家 | 宋明理学与心学 | `cn-songming-xue-xuan` | 薛瑄 |
| 哲学家 | 宋明理学与心学 | `cn-songming-sun-fu` | 孙复 |
| 哲学家 | 宋明理学与心学 | `cn-songming-hu-yuan` | 胡瑗 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-vasubandhu` | 世亲 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-nagarjuna` | 龙树 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-kumarila` | 鸠摩利罗（童中尊） |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-shankara` | 商羯罗 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-dignaga` | 陈那 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-dharmakirti` | 法称 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-candrakirti` | 月称 |
| 哲学家 | 印度哲学（正统六派与佛教） | `in-india-bhaviveka` | 清辨 |
| … | | | 余 25 条 |

## C 版本与篇次（须核校本）（782 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 两汉经学与气论 | `cn-lianghan-wang-fu` | 王符 |
| 哲学家 | 两汉经学与气论 | `cn-lianghan-xun-yue` | 荀悦 |
| 哲学家 | 两汉经学与气论 | `cn-lianghan-liu-an` | 刘安 |
| 概念 | 两汉经学与气论 | `cn-lianghan-shijiao` | 诗教 |
| 概念 | 两汉经学与气论 | `cn-lianghan-sanben` | 三本 |
| 概念 | 两汉经学与气论 | `cn-lianghan-wenzhi` | 文质 |
| 概念 | 两汉经学与气论 | `cn-lianghan-shiyi` | 师法家法 |
| 概念 | 两汉经学与气论 | `cn-lianghan-xingming` | 刑名 |
| 概念 | 两汉经学与气论 | `cn-lianghan-xungu` | 训诂 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-fanzhen` | 范缜 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-sengyou` | 僧祐 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-taohongjing` | 陶弘景 |
| … | | | 余 770 条 |

## D 生卒与年代推定（51 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 两汉经学与气论 | `cn-lianghan-liu-xin` | 刘歆 |
| 概念 | 两汉经学与气论 | `cn-lianghan-wuyi` | 五经博士与经学制度 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-huisi` | 慧思 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-damo` | 菩提达摩 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-tanluan` | 昙鸾 |
| 哲学家 | 南北朝佛道与形神之争 | `cn-nanbei-zhongrong` | 钟嵘 |
| 哲学家 | 隋唐佛学 | `cn-suitang-wang-tong` | 王通 |
| 哲学家 | 魏晋玄学 | `cn-weijin-guoxiang` | 郭象 |
| 哲学家 | 魏晋玄学 | `cn-weijin-zhang-zhan` | 张湛 |
| 概念 | 魏晋玄学 | `cn-weijin-gui-xu` | 贵虚 |
| 哲学家 | 先秦诸子 | `cn-xianqin-laozi` | 老聃（老子） |
| 概念 | 先秦诸子 | `cn-xianqin-daoshu` | 道术将为天下裂 |
| … | | | 余 39 条 |

## E 归属与真伪（托名／作者问题）（21 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 两汉经学与气论 | `cn-lianghan-he-xiu` | 何休 |
| 概念 | 隋唐佛学 | `cn-suitang-yixin-ermen` | 一心二门 |
| 哲学家 | 魏晋玄学 | `cn-weijin-sengzhao` | 僧肇 |
| 哲学家 | 先秦诸子 | `cn-xianqin-zhuangzi` | 庄周 |
| 哲学家 | 先秦诸子 | `cn-xianqin-gongsunlong` | 公孙龙 |
| 概念 | 先秦诸子 | `cn-xianqin-xing-qing` | 性情形于外 |
| 争论 | 印度哲学（正统六派与佛教） | `in-india-grace-self-effort` | 恩典与自力：解脱靠谁？ |
| 哲学家 | 古希腊哲学 | `gr-ancient-pythagoras` | 毕达哥拉斯 |
| 哲学家 | 古希腊哲学 | `gr-ancient-diogenes-sinope` | 第欧根尼（西诺佩的） |
| 哲学家 | 希腊化与罗马哲学 | `gr-hellenistic-zeno` | 芝诺（季蒂昂） |
| 概念 | 希腊化与罗马哲学 | `gr-hellenistic-fate` | 命运 |
| 哲学家 | 中世纪经院哲学 | `gr-medieval-averroes` | 阿威罗伊（伊本·鲁世德） |
| … | | | 余 9 条 |

## F 解释分歧（本页只作并述）（57 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 两汉经学与气论 | `cn-lianghan-sima-tan` | 司马谈 |
| 争论 | 两汉经学与气论 | `cn-lianghan-chunqiu-bifa` | 《春秋》笔法是实录还是托寄 |
| 概念 | 南北朝佛道与形神之争 | `cn-nanbei-foxing` | 佛性本有 |
| 争论 | 清代与近代转型 | `cn-qingmod-mingyi` | 《明夷待访录》是否具有民主性 |
| 概念 | 宋明理学与心学 | `cn-songming-wenjian-dexing` | 闻见之知与德性之知 |
| 概念 | 宋明理学与心学 | `cn-songming-jing-zuo` | 静坐 |
| 哲学家 | 隋唐佛学 | `cn-suitang-zhanran` | 湛然 |
| 哲学家 | 隋唐佛学 | `cn-suitang-shenxiu` | 神秀 |
| 概念 | 隋唐佛学 | `cn-suitang-famen-busi` | 法门不二 |
| 概念 | 隋唐佛学 | `cn-suitang-fajie-yuanqi` | 法界缘起 |
| 概念 | 先秦诸子 | `cn-xianqin-xiaoyao` | 逍遥 |
| 概念 | 19世纪哲学 | `gr-19c-existential-irony` | 生存的反讽 |
| … | | | 余 45 条 |

## G 无专门研究（只有语境性引用）（7 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 哲学家 | 20世纪：分析哲学、现象学与存在主义 | `gr-20c-benjamin` | 本雅明 |
| 哲学家 | 德国古典哲学 | `gr-german-jacobi` | 雅可比 |
| 哲学家 | 近代理性论与经验论 | `gr-modern-smith` | 亚当·斯密 |
| 著作 | （著作） | `work-theory-moral-sentiments` | 《道德情操论》 |
| 著作 | （著作） | `work-begriff-des-politischen` | 《政治的概念》 |
| 著作 | （著作） | `work-truth-meaning` | 《真理与意义》 |
| 比较篇 | （比较） | `cmp-time` | 循环、线性与刹那：中西时间观的三种结构 |

## Z 其他（103 条）

| 层 | 单元 | id | 名称 |
|---|---|---|---|
| 概念 | 两汉经学与气论 | `cn-lianghan-shishi-qiushen` | 实事疾妄 |
| 概念 | 南北朝佛道与形神之争 | `cn-nanbei-dunwu` | 顿悟成佛 |
| 概念 | 清代与近代转型 | `cn-qingmod-shishi-qiushi` | 实事求是 |
| 哲学家 | 宋明理学与心学 | `cn-songming-shao-yong` | 邵雍 |
| 概念 | 宋明理学与心学 | `cn-songming-dexing-lunli` | 德性伦理的儒家形态 |
| 争论 | 宋明理学与心学 | `cn-songming-tianli-renyu-zhi` | 天理人欲是截然二分，还是同一欲的过与不及 |
| 哲学家 | 隋唐佛学 | `cn-suitang-shenhui` | 神会 |
| 概念 | 隋唐佛学 | `cn-suitang-sanxing` | 三性 |
| 哲学家 | 魏晋玄学 | `cn-weijin-huiyuan` | 慧远 |
| 概念 | 魏晋玄学 | `cn-weijin-xingjin-shenmie` | 形尽神灭之辩 |
| 哲学家 | 先秦诸子 | `cn-xianqin-yang-zhu` | 杨朱 |
| 概念 | 先秦诸子 | `cn-xianqin-shi-li` | 诗言志 |
| … | | | 余 91 条 |

