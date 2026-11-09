# Endgame portfolio

> 历史快照：文中的“当前”、`PENDING`、未提交等状态仅对应文首时间。
> 终盘状态见 [`final_submissions/README.md`](../final_submissions/README.md)。

**北京时间：2026-10-22 02:56 CST**

## 当前在途 scoring

```text
ref 57481279  newtable A5eff30 only       PENDING
ref 57480145  newtable classroute75       PENDING
ref 57493876  newtable A5eff20 only       PENDING
```

不重复提交，不轮询。由用户观察完成后回传实际 score、是否被系统选中以及
同分区间排名变化。

**2026-10-22 11:09 CST update:** `ref 57481279` 已完成并成为当前最高分，
实数排名 `185 -> 175`。`A5eff30-only` 因此升级为新线上 anchor：

```text
new highest anchor = rsna-knee-newtable-a5eff30-only V1
```

`ref 57493876` 也完成并被系统选中，但线上顺序低于 `.30`。因此：

```text
A5eff30-only  = current highest
A5eff20-only  = selected fallback
A5eff40-only  = rejected by proxy/fold regression
```

**2026-10-22 23:11 CST update:** `mm08` ref `57514882` 已完成：

```text
public score                0.959
order vs A5eff30-only       lower
order vs A5eff20-only       higher
system selected             yes
current portfolio position  2
```

因此当前系统选中的 top-two 更新为：

```text
1  rsna-knee-newtable-a5eff30-only V1
2  rsna-knee-newtable-a5eff30-coatfull-stable11-mm08 V1

A5eff20-only 退出当前 top-two，保留为已验证历史 fallback
```

这同时修正了对运行期的粗判：同一重底座并非必然超时；Baker12 的 timeout
与 mm08 的成功并存，说明重底座存在明显的运行方差，后续仍应坚持零额外
模型前向和 fail-open。

**2026-10-22 23:34 CST:** `A5eff30 R150` Version 2 dev PASS，用户批准后已
提交 scoring：

```text
ref     57530094
version 2
status  PENDING
```

不轮询，由用户观察。

## 本轮新增静态候选

### 1. Anchor-preserving hedge

```text
intoxicatinglips/rsna-knee-newtable-a5eff20-only
```

- dev PASS；
- 只改 Effusion；
- A5 失败时完整回退 anchor；
- 已 scoring，ref `57493876`。

这是当前证据最干净、线上语义最明确的探针。

### 2. R225 attack（已降级）

```text
intoxicatinglips/rsna-knee-r225-double35-a5eff20
```

- hold；
- 对正确父模型 R150-double35：Gold `-.0000806`、870 `+.0006072`；
- A5 `.20` 在六种 reader/A5 稳健性组合上继续为正；
- A5 单元和数据集挂载与已 dev-pass 的 `a5eff20-only` 完全一致；
- 但在相同 A5 剂量下，production reader 的 Gold 仍为
  `-.0000806`，头对头 P(>0)=0。

文件保留作实验资产，不再进入 dev 队列。

### 3. Selected-anchor hedge

```text
intoxicatinglips/rsna-knee-anchor-double-effusion-half
```

- **dev PASS Version 1（用户回执）；未 scoring**；
- 只混合两个系统选中 anchor 的 Effusion 列；
- Gold/870 双 A5 表面均 5/5 正增量；
- 没有额外模型前向。

如果 `A5eff20-only` 失败，这是当前最合理的保守备胎；仍须用户批准
dev 后才能使用。

### 4. A5eff30 + Baker's .08

```text
intoxicatinglips/rsna-knee-newtable-a5eff30-baker08
```

- **dev PASS Version 1；未 scoring**；
- 新 anchor 的唯一新增是 Baker's A5 residual `.08`；
- 与 Effusion `.30` 共用同一次 A5 worker，不多跑模型；
- 六种 reader/A5 组合 870 增量 `+.000504–+.000555`，全部 5/5；
- 2500 次 bootstrap 全部 CI 下界为正；
- 嵌套 held-out 五折在六个表面全部为正。

这是当前最强的未提交候选，但 Baker's 还没有独立 hidden read。

### 5. A5eff30 + Baker's .12

```text
intoxicatinglips/rsna-knee-newtable-a5eff30-baker12
```

- static-ready；
- `.12` 位于 `.08-.14` 安全平台内部，`.15` 首次出现 Gold 退化；
- 相对 `.08`，六种表面 870 增量 `+.000205-.000245`，bootstrap CI 下界全正；
- 与 `.08` 共用同一 A5 worker；
- 是 `.08` 线上回执之前的进攻备胎，不先于 `.08` 使用。

**2026-10-22 12:24 CST:** `Version 1` 已 dev PASS 并正式 scoring，
ref `57509367`，当前 PENDING。

## 已关闭

```text
R225 + A5 Effusion .30
```

相对无 A5 仍为正，但相对 `.20` 的增益：

```text
Gold   +.000104 / +.000207
870    +.000042 / +.000064
folds  4/5 original, 3/5 mirror
```

CI 跨零，不构建候选。只有 ref `57481279` 的正式线上结果明确优于 `.20`
时，才重新打开。

## 决策树

```text
1. A5eff20 被系统选中或同分区间名次改善
   -> 保留 A5eff20 为新增益；不自动推 R225

2. A5eff20 未被选中且低于 anchor
   -> 比较 half-cross 是否值得一发；R225 保持 HOLD

3. A5eff30 明确优于 A5eff20
   -> 先重新评估 R150-double35 与 R225 的正确父模型头对头

4. 三个 pending 均无正向 hidden 证据
   -> 冻结当前最强两个提交，不再消耗探测额度
```

保持当前 top-two 不变；所有 dev/scoring 仍等待用户明确批准。

## A5 第三列

无门控第三列和 PF OA 共现门控均未通过嵌套稳定性。`PF OA .05` 的
全量六面结果很好，但 held-out fold0 只有 `3/6` 表面为正，因此裁决为：

```text
HOLD_A5_THIRD_COLUMN
```

当前保持 `A5eff30 + Baker12`，不增加第三列。

## Other independent signal scan

复用公开 six-token ConvNeXt-Tiny sliceseq OOF 后，没有任何单列在当前
A5eff30+Baker12 宿主上达到六面 `5/5`；最好仅 `4/5`。因此不构建
sliceseq 叠加候选。

当前 active challenger 仍只有 `Baker12`。

## 公开区低频快照

北京时间 `2026-10-22 03:00` 左右取了一次单页真实分数快照，未轮询：

```text
requested pages       1
notebooks retrieved   100
public maximum        .958
above current .959     none
```

`.958` 同档包括 `evgendvorkin/rsna-versia-7`、`goodpjw2008` 的
CoAtNet/R6 notebook、`heliosli` 的新数据 notebook 和
`lavinwins` 的 fork。没有出现可复现、且真实分数高于当前锚的新资产。

快照：

```text
reports/comp_code_scores_2026-10-22_0300.csv
```

## Post-processing portfolio lock

**2026-10-22 13:03 CST update**

终盘 portfolio 已用机器可读 axis registry 和两组本地审计互相锁定：

```text
postprocess lock          33/33 checks + 4/4 negative controls
active portfolio audit    78/78 checks
pending submissions       1 (Baker12 ref 57509367)
archived R225 candidates  2, dev_eligible=false
```

产物：

```text
reports/postprocess_axis_registry_2026-10-22.json
reports/postprocess_lock_audit_2026-10-22.json
reports/active_postprocess_portfolio_audit_2026-10-22.json
reports/ACTIVE_POSTPROCESS_PORTFOLIO_AUDIT_2026-10-22.md
```

在 Baker12 返回真实结果前，不重推、不改 notebook、不再新增 PENDING。

## New model-side challengers

**2026-10-22 14:05 CST update**

Two independent static model candidates are now ready for a future dev gate:

```text
rsna-knee-newtable-a5eff30-coat384core3
  CoAtNet-384 SWA, core3 .035
  conservative single-model residual

rsna-knee-newtable-a5eff30-coatfull-adapted20
  adapted CoAtFull, pre-declared stable10 route .20
  larger local signal, heavier child forward
```

Both have `dev_eligible=false`; neither has been dev-pushed or scored.
The adapted20 candidate has the stronger local evidence but has not been
validated through Kaggle yet.
