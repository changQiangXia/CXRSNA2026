# Skill 后处理经验映射与终盘冻结

**北京时间：2026-10-22 12:53 CST**

## 结论先行

本赛的指标是 12 个独立二分类 AUC 的 macro 平均，因此本质上是
“十二场彼此独立的小排序赛”，不是一个可以用全局概率校准或大堆叠统一
解决的单一目标。

目前最细腻、也最符合 skill 证据的形态已经找到：

```text
强宿主
→ 目标列内百分位秩
→ 独立 A5 五折 mean-rank residual
→ 固定低剂量
→ 只改有独立证据的目标列
→ 覆盖/异常失败时精确回退 anchor
```

当前生产配置：

```text
Effusion  0.30
Baker's   0.12
其他 10 列 byte-identical
```

这不是“再加一个大模型”，而是逐目标纠错。A5 单体并不强；它的价值来自
与宿主只部分相关，并在少数宿主排错的样本对上净修复更多 pair。

## 证据底座

| 证据 | 等级 | 当前事实 |
|---|---:|---|
| A5 Effusion `.30` hidden 结果 | A：我方线上 | 成为最高分；排名 185 → 175 |
| A5 Effusion `.20` hidden 结果 | A：我方线上 | 被系统选中，但顺序低于 `.30` |
| A5 Effusion `.40` | B：本地反证 | 870 增量转负、折方向崩溃；关闭 |
| A5 Effusion solo | B：本地 OOF | 870 macro `.871770`，并不强 |
| A5–宿主 Effusion 相关 | B：本地 OOF | Spearman 约 `.78–.86`，不是冗余复制 |
| A5eff30 + Baker's `.12` | B：六 Reader/A5 面 | Gold `0` / `+.000151`；870 六面 `+.000715–.000791`，全 5/5 |
| Baker12 hidden 结果 | 未观测 | ref `57509367` PENDING；不得冒充成功 |

当前 anchor：

```text
intoxicatinglips/rsna-knee-newtable-a5eff30-only
Version 1
ref 57481279
```

当前唯一进攻 challenger：

```text
intoxicatinglips/rsna-knee-newtable-a5eff30-baker12
Version 1
ref 57509367
dev PASS
```

## Skill 机制映射

### 1. 多目标按每列选择，而非全局同权

**Skill 类比**

- `playground-series-s3e18`：“不是多标签，而是两场比赛”。EC1 的最优族和
  EC2 的最优族明显不同；每列最好单独验证。
- `playground-series-s4e3`：Mean Columnwise AUC 下，多类、多标签和逐目标
  二分类都可能赢；形态必须用 OOF 对照，不能凭题面猜。

**本场迁移**

```text
12 findings = 12 targets
```

Effusion 和 Baker's 只有在“独立信号 + 宿主错序净修复 + 五折同向”同时
成立时才允许进入最终 residual。A5 在 Effusion 上的 hidden 成功不能免费
外推到其他 11 列。

**裁决**

保留逐目标单列 residual；不采用全 12 列同权重 A5 融合。

---

### 2. AUC 用秩空间残差，不做概率校准

**Skill 机制**

- M3：AUC 只依赖每列相对次序，对任何严格单调变换不变。
- M21/B2：模型融合的主要增量来自降低协方差；同质模型堆叠不会自动增益。
- `playground-series-s3e23`：异质成员、只在 OOF 上调权重。
- `playground-series-s6e2`：简单 Ridge/秩类和稳定选择优于复杂非线性 stack。

**本场实现**

```text
host_rank = percentile rank(host probability)
a5_rank   = mean_f percentile rank(a5_fold_f probability)
final     = (1 - dose) * host_rank + dose * a5_rank
```

固定剂量先验：

```text
Effusion .30
Baker's  .12
```

这里不拟合概率偏移，不学 logistic stacker，也不做 isotonic。对 AUC 而言，
这些操作只改变绝对分数，却增加小样本过拟合风险。

**已关闭**

- probability / logit / z-rank 全局融合曾多次导致 Gold 退化；
- isotonic、cross-label logistic、GBDT 和逐 study 学权重此前均被拒绝；
- public LB 搜阈值/剂量禁止进入最终方案。

---

### 3. 低剂量只负责纠错，不负责替换强宿主

**Skill 边界**

- 一个成员即使更弱，也可能在少数 pair 上带来净信息；
- 但它不能主导强宿主，否则会把自身误差注入最终排序；
- 权重必须在同折 OOF 上定价，并检查边际修复是否开始小于边际破坏。

**本场 pair 证据**

Effusion `.30`：

```text
870 original: fixed 584 host-wrong pairs, broke 266 correct pairs, net +318
870 mirror:   fixed 628 host-wrong pairs, broke 233 correct pairs, net +395
```

五个子折的净修复方向均为正。`.40` 虽然修复更多，却同时破坏更多，
净增量反而下降。因此 `.30` 不是“越大越好”的经验值，而是边际纠错与
边际破坏的平衡点。

**裁决**

保留固定低剂量；最后 48 小时不再继续细扫剂量。

---

### 4. 额外列必须通过逐列准入门，而不是“同家族可继承”

**Skill 类比**

- `playground-series-s3e18`：两列最优模型族不同，某列成功不能自动迁移。
- B11：多目标应先做拆/合和逐目标最优族比较。

**本场准入**

Baker's 是唯一通过无门控第三列扫描的第二个 A5 目标：

```text
Gold 不退
870 六 Reader/A5 面全正
5/5 folds
bootstrap CI 下界 > 0
nested held-out 全正
```

其他列没有任何一个同时达到这套门槛。

**已关闭**

- 第三个无门控 A5 列：除 Baker's 外全部失败；
- PF OA 门控 `.05/q=.60`：固定点漂亮，但 nested held-out fold0 失败；
- 其他临床共现先验最多只有 2–3/5 正折。

**Baker's `.12` 的 pair 机制**

额外离线拆解显示，Baker's `.12` 在六个 Reader/A5 面只改变约
`1.2%–1.3%` 的正负 pair，却每面净修复 `700–774` 对：

```text
30 / 30 fold-surface combinations net positive
minimum fold net  +5 pairs
maximum fold net  +59 pairs
```

这说明它是准确定位的小范围纠错，而不是大范围重排。

详见：

```text
reports/BAKER12_PAIR_MECHANISM_2026-10-22.md
```

---

### 5. 稳健聚合优先于更复杂的置信度

**Skill 类比**

- `playground-series-s6e2`：最高 CV 不一定是最终最优，选择纪律与稳健元模型
  比继续复杂化重要。
- `playground-series-s4e3`：同折 OOF 上做小权重优化，等权混合常是强基线。

**本场 A/B**

| 聚合方式 | Gold | 870 / folds | 裁决 |
|---|---:|---:|---|
| 五折 mean percentile-rank | 当前基线 | 当前基线 | KEEP |
| median rank | 部分正 | 代理面负、折不稳 | REJECT |
| fold-variance confidence | 全负 | 全负 | REJECT |
| 原图/镜像 rank mean | `+.000263` | 仅 `+.000056–.000066`、2–3/5 正 | REJECT |

结论：五折 mean-rank 已经提供了足够的 checkpoint 去噪；再根据 fold variance
降权会把“分歧”误当成“不可信”，反而伤害真正有纠错价值的样本。

---

### 6. Fail-open 是医学影像后处理的一等能力

**Skill 类比**

- `rsna-intracranial-aneurysm-detection` 1st：数据异常序列直接回退；
  远端医学影像赛中，失败兜底和时延与模型同样重要。
- agentic-kaggle 收官规则：先保证可运行与契约，再追求增量。

**本场实现**

```text
coverage < .90      -> exact anchor fallback
worker failure      -> exact anchor fallback
timeout             -> exact anchor fallback
A5 receipt fail     -> exact anchor fallback
```

Baker12 的 dev 机械回执：

```text
a5_receipt                 PASS
labels                     Effusion, Baker's
doses                      .30 / .12
coverage                   1.0
worker exits               [0, 0]
fallback studies           0
submission_receipt         PASS
```

三例 dev 的 rank no-op 属于小样本预期，不是 hidden 负证据。

**隐藏级契约压缩**

另行用 `4407 study × 5 fold` 对后处理数学做离线压力测试，覆盖 shard
重排、覆盖率 `<.90`、NaN、单 study、常数列和 CSV 往返：

```text
28 / 28 checks PASS
non-target columns byte-identical
```

因此剩余的不确定性集中在“Baker's hidden 是否涨分”，而不是行数、ID
顺序、五折、非有限值或原子落盘。

详见：

```text
reports/ENDGAME_POSTPROCESS_CONTRACT_2026-10-22.md
```

---

### 7. 最终提交只做风险分层，不做公榜微差赌博

**Skill 类比**

- `playground-series-s3e22`：20/80 公私榜会产生大面积洗牌；前 11 中 7 队
  只提交 1–2 次。少而准的提交优于在公榜微差上反复下注。
- B20：候选相关性高时，多头对冲没有意义；应保留语义不同、风险来源不同的
  两层。

**本场组合**

| 层级 | 候选 | 风险语义 |
|---:|---|---|
| Anchor | A5eff30-only | hidden 已证明正序 |
| Challenger | A5eff30 + CoAtFull mm08 | public `0.959`；hidden 有效且被系统选中 |
| Conservative | A5eff20-only | 已被 mm08 替换出 top-two，保留为历史 fallback |
| Cross hedge | anchor/double Effusion half | 无额外前向，但语义较绕；低优先级 |

系统会自动选择我方最强的两个有效提交。因此最终不需要为了“多交几个”
继续制造高度相关变体。

## 已关闭清单

以下方向不再重开：

```text
HOLD_A5_THIRD_COLUMN
HOLD_COOCCURRENCE_SMOOTHING
REJECT_A5_MIRROR_AGGREGATION
REJECT_FOLD_VARIANCE_CONFIDENCE_WEIGHTING
REJECT_MEDIAN_RANK_AGGREGATION
HOLD_R225
REJECT_SLICESEQ_ON_A5EFF30_HOST
REJECT_TEACHER_WEAK_LABEL_STUDENT
REJECT_CROSS_LABEL_LEARNED_STACKER
REJECT_ISOTONIC_OR_PROBABILITY_CALIBRATION
```

共同原因不是“想法不高级”，而是没有同时通过：

```text
Gold 不退
870 六面同向
五折同向
bootstrap / nested 支持
不损害时延与 fail-open
```

## Baker12 结果后的决策树

### A. Baker12 被系统选中，且总名次高于当前 anchor

```text
冻结 Baker12 + A5eff30-only 为 top-two
不再追加第三列
不再做剂量细扫
```

### B. Baker12 被系统选中，但顺序低于当前 anchor

```text
保留 A5eff30-only 为最高分
Baker 轴停止升级
不自动改投 Baker08：同一信号更弱，且当前没有“高剂量伤、低剂量好”的 hidden 证据
```

### C. Baker12 完成但未被系统选中

```text
视为 Baker hidden 迁移不足
冻结当前 top-two
Baker08 只在有明确高剂量反转证据时才考虑
```

### D. Baker12 技术失败或精确回退

```text
先读 a5/submission receipt
区分“工程失败”与“模型无增益”
工程失败不等于 Baker 信号失败
不自动重推；需要用户批准
```

## 最后 48 小时纪律

1. 不引入新模型族、新学习式 stacker 或新临床后处理。
2. 不根据 public LB 搜剂量、门控或阈值。
3. 不轮询 Kaggle；由用户低频观察并回传状态。
4. 每次 dev/scoring 都需要用户明确批准。
5. 只运行轻量本地审计；当前 GPU 与下载进程均空闲。
6. 任何重推先重新核对 notebook/metadata SHA 与 manifest。
7. 最终只从“线上已验证 anchor”和“有独立证据的 challenger”中选择。

## NVIDIA skill 本地缓存交叉复核

另用 `nvidia-kaggle-skill` 的本地缓存复查了本赛 `212` 个 discussion 和
`550` 个 kernel，没有发起 Kaggle 网络请求。新增确认：

```text
three-decimal LB makes many fusion operators indistinguishable
public split ~390 studies; single-run sigma ~.003
rank/prob/logit/adaptive blends can round to the same score
Synovitis is label-limited
corrupt DICOM / single-class column require fail-open
slice-order correction is not directly transferable to the single-slice A5
```

报告：

```text
reports/NVIDIA_SKILL_OFFLINE_CROSSCHECK_2026-10-22.md
reports/postprocess_axis_registry_2026-10-22.json
reports/POSTPROCESS_LOCK_AUDIT_2026-10-22.md
reports/ACTIVE_POSTPROCESS_PORTFOLIO_AUDIT_2026-10-22.md
```

## 当前状态

```text
A5eff30-only V1            COMPLETE 0.959, top-1
mm08 ref 57514882          COMPLETE 0.959, top-2
A5eff20-only ref 57493876  COMPLETE 0.959, replaced from top-two
Baker12 ref 57509367       TIMEOUT, no score
A5eff30 R150 dev           Version 1 pushed, awaiting user receipt
本地训练                    none
下载任务                    none
GPU                         空闲
Kaggle 轮询                 未执行
```

下一步只等待用户报告 A5eff30 R150 dev 回执；未获单独 scoring 批准前不提交。
