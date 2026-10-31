# NVIDIA skill 本地缓存交叉审计

**北京时间：2026-10-22 12:59 CST**

## 范围

使用 `nvidia-kaggle-skill` 的本地 SQLite 缓存，没有发起 Kaggle 网络请求：

```text
discussions   212
kernels       550
date range    2026-07-30 .. 2026-10-21
```

重点检索 `rank`、`blend`、`ensemble`、`stack`、`calibration`、`TTA`、
`OOF`、`Effusion`、`Synovitis`、`co-occurrence`。

## 1. 融合算子在三位公榜下不可分辨

讨论 `740439` 做了一次很干净的外部实证：

```text
不同公开权重 0.00 .. 1.00
rank / probability / logit / geometric / power / clipped / adaptive
大量变体最终都显示同一 0.937
```

作者明确记录 13 个提交读成同一个三位分数，flat plateau 约在
public weight `.50–.75`。

这条证据对本赛的意义：

- 不要继续扫概率域、logit 域、几何平均、幂平均；
- 不要再做 per-study / per-label adaptive blend；
- 保留 rank mean 与固定剂量，因为这些是当前唯一有 hidden 方向和
  pair 机制支持的形式；
- 显示分相同不等于真实分相同，同分块内名次变化更细。

## 2. 公榜约 390 studies，三位显示噪声约 .003

讨论 `748011` 的测量与评论：

```text
public split 约 30% of ~1300 studies ≈ 390
macro AUC 0.955 的单次 public standard deviation ≈ 0.003
displayed score truncated to 3 decimals
within tie block, rank follows unrounded score
```

因此：

- 单次 public 分差 `0.001` 大多不能证明模型更好；
- 同一 base 的单变量 A/B，应优先看系统选中和 tie-block 名次；
- 0.959 区间内的 10–20 名变化也可能是真实的小数第四位差异；
- 不能从一次 public 微差推导 hidden 稳定性。

这与我们最近多轮“同分但系统选中顺序变化”的观察一致。

## 3. AUC 对硬标签阈值不敏感

讨论 `745949` 的公开实验提到：

```text
Effusion image model: AUC .986 / accuracy .931
Synovitis image model: AUC .859 / accuracy .776
```

作者建议以软概率排序 `explicit present > equivocal > not mentioned >
explicit absent`，而不是用 0.5 硬切。

对本赛：

- 我们已在 rank space 操作，不需要概率校准；
- Effusion 的独立视觉证据强于 Synovitis；
- 不应把 Effusion 的成功平均分配给 Synovitis。

## 4. Synovitis 是弱监督上限，不是“再调一下”的问题

讨论 `737566`：

```text
~16% reports mention synovitis terms
public label tables vs Gold58: Synovitis ~.79 AUC, ACL ~.99
Effusion↔Synovitis Gold correlation ~.5
```

这支持此前的裁决：

```text
REJECT Synovitis residual
REJECT unfocused co-occurrence smoothing
```

即使临床共现存在，标签噪声与视觉可分性仍然让弱门控极易在 held-out
fold 失效。我们的 PF/Synovitis 共现实验也正是这个结果。

## 5. 损坏 DICOM 与单类列必须 fail-open

讨论 `740094` 指出两个隐藏边界：

- 某列在 hidden 只有单一类别时，官方 macro AUC 行为未明确；
- test 可能存在截断 PixelData 或无法解码的 DICOM。

当前链路：

```text
read_crop / pixel_array guarded by try-except
empty or unreadable slot -> mask false
study coverage < .90 -> exact submission fallback
single-study / single-class -> rank no-op, no crash
```

隐藏级契约测试已经确认单 study、常数成员、coverage `<.90` 和 NaN
均安全 fail-closed。

## 6. 环境与路径

讨论 `735854` 的 code-submission 常见故障：

- GPU compute capability 不兼容；
- 缺少 DICOM codecs；
- `/kaggle/input/` 路径层级变化。

当前 Baker12 已对应处理：

```text
GPU enabled
internet disabled
offline wheels attached
assets/weights/data discovered with bounded patterns
dev PASS with codecs and two shards
```

这解释了为什么继续改 notebook 本体风险高于收益。

## 7. 切片顺序讨论的适用边界

讨论 `745759` 证明某些公开 baseline 把 SOP UID 当切片顺序，导致相邻
通道不对应；修正 IPP 顺序在一折上约 `+0.028 AUC`。

当前 A5 worker：

```text
ordered_files sorted by InstanceNumber
render uses single slices
model does not build [i-1, i, i+1] RGB channels
sample band is a coarse 12%-88% selection
```

因此该反例不能直接外推为 A5 新 axis；若要省时间应优先验证
ImagePositionPatient 排序，而不是改模型结构。最后 48h 不启动该实验。

## 8. 公开 fork plateau 是后处理过拟合警报

讨论 `742050` 复盘了约 200 个 `0.941` 公开 fork：

```text
0.941 recipe = per-label outer weights
             + inner CoAt/Raptor rerank
             + Raptor arms 0.55/0.15

last rerank was a no-op because input was already percentile rank
Mattia's own stack kept arms 0.60/0.10
```

评论区的关键结论是：在没有新模型、新数据或独立 validation signal 时，
继续在两三个 blend 权重之间搜索，本质上是在 public split 上调超参。

这与当前 A5eff30/Baker12 的区别是：

- A5 不是另一个 public blend 权重；
- A5 有独立 DINOv3 模型、五折 OOF、pair-level 净修复；
- Effusion `.30` 已有 hidden 正序；
- Baker's 是唯一通过逐列准入的第二个 target。

但这条证据仍要求我们停止继续扫 `Baker .12/.13/.14`、停止制造
第三列 gate，不要在 public tie block 内做无独立证据的微调。

补充阅读 `749570` 后，热门 stack 的 `Lateral Meniscus = 1.00` 也被确认是
public-split 不可分辨的硬路由：它把另外三路完全乘零，而作者自己的
ablation（uniform 0.60）当时仍 pending。`742926` 的独立小面板则报告：

```text
fixed 50/50 percentile-rank blend   0.9077
nested-CV tuned rank weights        0.9026  (worse)
raw 50/50 probability mean          0.9105
```

这再次说明：在没有新的独立信号时，复杂 rank-weight tuning 不可信。
我们不会复制 `LM=1.00` 或把它改成另一个 public 权重；若要动，必须先有
同折 OOF、Gold 不退和六面正增量，当前时间窗不允许。

## 9. Hidden rerun 的 NaN / 坏 DICOM 风险

讨论 `749623` 记录了两个“public notebook 正常、hidden rerun 失败”的
提交；Chris Deotte 的评论建议用约 `1300` 个训练 study 做 commit-only
模拟，并重点检查 NaN 与 malformed DICOM。

当前 A5 worker 对该风险的处理：

```text
metadata failure       -> skip file
pixel decode failure   -> empty slot
no usable series       -> NaN output + applicable=false
coverage < .90         -> exact base submission fallback
NaN in applicable rows -> fail-closed before write
worker exit != 0       -> exact fallback
```

已有的 raw-DICOM 实测：

```text
58 Gold studies
RTX 4090, two shards
about 11.8s + 12.8s
coverage 58/58
rank correlation vs reference .999416
```

线性外推到约 1300 studies 仍显著低于 60 分钟 A5 wall-clock 上限；
T4 更慢，但 A5eff30 anchor 已经在真实 hidden 上完整通过同一 worker，
所以不再为“可能坏 DICOM”临时改 notebook。

## 10. 共现先验可用于标签，不等于可用于最终 rank

本地 notebook 语料中的 Qwen2.5-32B 弱标签卡给出了明确对照：

```text
raw report labels vs Gold58      macro AUC .8521
+ conservative co-occurrence    macro AUC .8686
```

其中只对 report 未提及的格子做低置信填充：

| 规则 | 填充概率 |
|---|---:|
| PF OA ← Medial OA | `.60` |
| Synovitis ← Medial OA | `.60` |
| Synovitis ← Effusion | `.55` |

这说明共现结构主要是在修复**训练标签的 silence / missingness**。

但在当前强宿主上，把这些临床共现直接用于最终预测 rank 时：

- Effusion `.30 + Baker12` 之后，Baker←Effusion `.03` 仅勉强稳定；
- 其他 PF/Synovitis 图最多 2–3/5 正折；
- nested held-out 会把固定点增益推翻。

因此正确边界是：

```text
co-occurrence fill        MAY help labels
co-occurrence rank smooth REJECT on current inference
```

当前没有时间重新训练标签模型，所以不把这条重新包装成推理 trick。

## 11. 公开 3-study MCL swap 不是 hidden-safe 后处理

早期公开 stack 中存在：

```text
MCL S3=highest swap
```

它直接在公开 test 的 3 个 study 上交换 MCL 最大值与第二值，理由是
CoAtNet / maxspan_reverse 对该列的排序与主链不同。

这类操作：

- 只对可见 3 个 study 可验证；
- 没有 study-level 独立性；
- hidden 无法知道是哪三个 study；
- 本质接近 public dev 的手工标签修正。

当前 anchor/Baker12 不包含该 swap；不得在最后窗口按同一思路增加
per-study override。

## 裁决

```text
KEEP rank residual
KEEP fixed dose
KEEP exact fail-open
REJECT fusion-operator sweep
REJECT adaptive per-label blend
REJECT Synovitis residual
HOLD slice-order axis
NO new model / data / submission
```

当前最强 anchor 与 Baker12 challenger 不变。
