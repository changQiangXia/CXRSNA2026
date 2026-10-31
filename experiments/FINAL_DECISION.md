# 最后一发的细腻后处理方案

**北京时间：2026-10-22 23:09 CST**

## 1. 台账结论

本场比赛不是“一个模型越重越好”，而是 12 个独立 AUC 列的平均：

```text
score = mean(AUC_1, ..., AUC_12)
```

因此有效的后处理必须满足：

```text
逐目标有机制
→ rank 空间操作
→ 六 Reader/A5 面同向
→ 五折同向
→ Gold 不退化
→ fail-open
```

总台账中最可靠的线上事实是：

```text
A5eff30-only V1 ref 57481279   online 0.959, highest completed
mm08 V1 ref 57514882           online 0.959, second selected
A5eff20-only V1 ref 57493876   online 0.959, selected but lower
A5eff30+Baker12 V1 ref 57509367 timeout, no score
```

因此当前 anchor 只能是 `A5eff30-only`，不能把 Baker12 当作已成功父体。
mm08 仅替换了第二候选，并没有超过 anchor；其本地 proxy 增量远大于
R150，却仍只达到同分 tie-break 层，说明本地面板到 hidden 的传导很弱。

## 2. 为什么大多数“更高级”后处理不能用

台账已经否定了这些方向：

| 方向 | 事实 | 裁决 |
|---|---|---|
| 概率/logit/isotonic | AUC 对单调变换不变，Gold 多次退化 | 不使用 |
| 学习式 cross-label stacker | 58/870 小面过拟合，fold 不稳 | 不使用 |
| fold-variance 置信度 | Gold 与 proxy 同时下降 | 不使用 |
| median rank | mirror proxy 不稳 | 不使用 |
| 临床共现门控 | 最多 2–3/5 折，固定点易碎 | 不使用 |
| A5 mirror 平均 | proxy 只有约 `+.00006`，折不稳且翻倍耗时 | 不使用 |
| 第三个 A5 列 | 无列同时通过六面五折 | 不使用 |
| 重 child（CoAtFull/R384） | 底座已出现 hidden timeout | 不再追加 |

这正是“细腻”的含义：不是继续增加后处理层数，而是承认多数方向没有
足够证据，保留唯一能被多个独立面同时支持的单变量。

## 3. 候选细化实验

在 A5eff30-only 上比较了：

```text
uniform R150
Effusion-isolated R150
ACL/MedMen/MedOA/Baker 1.75 tier
conservative 1.75 tier
```

结果：

- 统一 R150 相对 A5eff30：
  - Gold `0`，无负列；
  - 870 proxy `+.000664 / +.000671`；
  - 两面 5/5 fold；
  - bootstrap 下界均大于 `+.00050`。
- 逐目标 `1.75` tier：
  - proxy 更高，但 Gold ACL `-.0001021`；
  - 不满足“最后一发不退化”约束，拒绝。
- Effusion-isolated R150：
  - 没有优于统一 R150；
  - focused-severity 跨列耦合仍使 Effusion mirror pair net 为 `-2`；
  - 因此不选择“看起来更细、实际没有证据”的隔离版。

结论：

```text
FINAL = A5eff30-only + uniform reader R150
```

这不是随手乘一个系数，而是在预注册 tier 中保留唯一通过 Gold、
proxy、fold 和 bootstrap 的版本。

## 4. 最终候选

```text
intoxicatinglips/rsna-knee-newtable-a5eff30-r150
```

实现：

```text
21 cells
cell 18: 12 reader OWN_W_PER_TARGET × 1.50
A5 Effusion .30: byte-identical
no new model
no new checkpoint
no extra TTA
no extra child
```

工程状态：

```text
static audit               PASS
input preflight            0 uncovered / 0 risky
all code cells compile     PASS
private / GPU / offline    PASS
dev pushed                 false
scoring submitted          false
```

## 5. 最后一发的执行纪律

1. 不推 dev，除非用户明确批准。
2. dev 只验证执行链和 reader 权重实际加载，不把 3 例 no-op/hit 当 hidden
   增益证明。
3. dev PASS 后仍需用户单独批准 scoring。
4. 不轮询 Kaggle；不根据公榜微差改剂量或 Gate。
5. 若 dev 超时或 A5 receipt 不完整，停止候选，不重推同一 notebook。
6. 若 scoring 超时，保留 `A5eff30-only` 作为历史最高有效分数，不再把
   重底座候选当作可交付。

## 6. 预期

```text
当前 anchor: 0.959
本地增量:   +.000664 到 +.000671
显示分桶:   仍大概率 0.959
真正价值:   同分区间内的 rank 微调，而不是承诺 0.960
```

本场公榜只显示三位小数，且总分由 12 列平均；任何 `+.0006` 级改动都
不能保证显示分变化。因此最终选择的目标是“有机制的 tie-break 改善”，
不是用最后一发赌一个大集成。
