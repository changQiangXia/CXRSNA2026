# RSNA Knee Abnormality Detection 2026 — 赛后完整归档

> 本 README 同时提供中文和英文版本。中文在前，英文在后。

这是一个面向赛后的完整归档，记录 `intoxicatinglips` / **CHEN Xiang** 团队参加
[RSNA Knee Abnormality Detection 2026](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
的全过程。

仓库包含：

- 完整实验历史与决策台账；
- 终盘提交 notebook、candidate manifest 和 dev 回执；
- 公开/私有分数、提交 ref 和系统选中记录；
- 公开区高排名 write-up 的技术摘要与原文链接；
- 失败路线、超时案例和负面结果；
- 下一次医学影像比赛的实战 checklist。

原始 DICOM、竞赛标签、私有 checkpoint、Kaggle token 和大体积 notebook 输出
不会进入本仓库。

## 最终成绩

| 项目 | 数值 |
|---|---:|
| Public leaderboard | **0.959** |
| Private leaderboard | **0.945** |
| Public rank snapshot | **182 / 6,425** |
| 使用提交数 | 94 |
| 归档时间 | 2026-10-31 UTC |

公榜只显示三位小数。很多终盘候选都显示 `0.959`，但全精度排序并不相同。

## 这场比赛真正难在哪里

训练集有 4,407 个 study，其中只有 58 个有专家裁决标签。训练 study 有放射科报告，
但测试集没有报告。指标是 12 个独立二分类 AUC 的 macro 平均：

```text
ACL、MCL、内侧半月板、外侧半月板、
内侧 OA、外侧 OA、髌股 OA、
积液、滑膜炎、Baker 囊肿、
骨挫伤、骨折
```

核心任务不是“堆一个更大的模型”，而是：

1. 把多语言报告和图像转成更好的监督；
2. 训练一个真正只依赖图像、能泛化到 hidden studies 的 reader；
3. 把 9 小时 hidden rerun 的耗时和 fail-open 设计进模型；
4. 只做有机制、可解释、逐目标的后处理。

所有高分公开方案都指向同一个结论：**标签和 anatomy-aware inputs 的收益，
远大于盲目更换时髦模型。**

## 我们的爬升路径

```text
0.943  早期公开 stack
0.945  specialist stack
0.949  CoAtNet reader
0.950  reader fusion + FOV ladder
0.951  更强的公开 checkpoint family
0.954  laddered family
0.956  改进的公开组合
0.957  自研 R-slot checkpoint + compact-model fusion
0.958  rank-band 与逐病种路由
0.959  newtable anchor + A5 Effusion residual
```

终盘停在 `0.959 public / 0.945 private`。最关键的后处理增量是 A5 Effusion
residual `.30`；更高剂量、更多目标列或更大的 residual bundle 都无法稳定迁移。

## 最终 scoring wave

所有终盘候选完整保存在 [`final_submissions/`](final_submissions/README.md)。

| Submission | Ref | Public | Private | 作用 |
|---|---:|---:|---:|---|
| `A5eff30-only V1` | 57481279 | 0.959 | 0.945 | 最干净的 anchor |
| `A5eff20-only V1` | 57493876 | 0.959 | 0.945 | 低剂量 fallback |
| `mm08 V1` | 57514882 | 0.959 | 0.945 | CoAtFull 半月板 residual |
| `allgold V6` | 57525829 | 0.959 | 0.945 | 三 child 保守路线 |
| `allproxy V4` | 57525824 | 0.959 | 0.945 | 三 child 进攻路线 |
| `R150 V2` | 57530094 | 0.959 | 0.945 | 最后一个 reader-scale 候选 |

按提交时间最后两发是 `allgold` 和 `R150`。由于多个提交几乎同时发出，
这里归档整个 final wave，避免“最后两个”产生歧义或遗漏。

`A5eff30 + Baker12`（ref `57509367`）作为失败案例保留：Kaggle 返回 notebook
超时，无分数。

## 仓库导航

- [`docs/COMPETITION.md`](docs/COMPETITION.md)：比赛卡片、指标、数据规模、
  leaderboard 和证据边界。
- [`docs/TIMELINE.md`](docs/TIMELINE.md)：按时间排列的探索历程。
- [`experiments/EXPERIMENT_LEDGER.csv`](experiments/EXPERIMENT_LEDGER.csv)：
  原始详细实验台账。
- [`experiments/FINAL_DECISION.md`](experiments/FINAL_DECISION.md)：最后的后处理
  选择，以及替代方案为什么被拒绝。
- [`public_intel/TOP_WRITEUPS.md`](public_intel/TOP_WRITEUPS.md)：顶级选手
  write-up 的技术摘要与链接。
- [`docs/LESSONS.md`](docs/LESSONS.md)：下一场比赛应该怎么做。
- [`final_submissions/`](final_submissions/README.md)：最终 notebook、manifest、
  dev 回执和 scoring ref。

## 正确理解这个结果

- public 与 private 是两个不同的样本，不能混为一谈；
- 显示为 `0.959` 不代表两个提交在全精度上相同；
- 本地 proxy 增量低于约 `0.001` 时，通常不足以预测显示分变化；
- 9 小时 code competition 中，推理耗时和模型精度同等重要；
- 58 例专家标注面板是过滤器，不是可靠的最终 ranker。

## 复现与私有资产

notebook 会引用公开 Kaggle 数据集和少量团队私有 artifact；这些 artifact
不会在本仓库中重新分发。复现者必须自行准备合法获得的比赛数据、公开权重和
有权限使用的私有资产。

归因见 [`docs/ATTRIBUTIONS.md`](docs/ATTRIBUTIONS.md)，共享边界见
[`NOTICE.md`](NOTICE.md)。

---

# RSNA Knee Abnormality Detection 2026 — Complete Archive (English)

This repository is a detailed, post-competition archive of team
`intoxicatinglips` / **CHEN Xiang** in the
[RSNA Knee Abnormality Detection 2026](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)
code competition.

The repository contains:

- the full experiment history and decision ledger;
- the final-wave submission notebooks and candidate manifests;
- dev receipts, scoring references, and public/private scores;
- summaries of the most useful public write-ups and discussions;
- the failure paths that prevented a stronger result;
- a practical playbook for the next medical-imaging competition.

Raw DICOM data, competition labels, private checkpoints, Kaggle credentials,
and large notebook outputs are intentionally not included.

## Final result

| Field | Value |
|---|---:|
| Public leaderboard | **0.959** |
| Private leaderboard | **0.945** |
| Public rank snapshot | **182 / 6,425** |
| Submissions used | 94 |
| Final archive prepared | 2026-10-31 UTC |

The leaderboard displays only three decimals. Many different final candidates
therefore displayed `0.959` while differing at a finer, invisible precision.

## What this competition really was

There were 4,407 training studies and only 58 studies with expert-adjudicated
labels. Every training study had a free-text radiology report, but test studies
did not. The target was the mean of 12 independent ROC-AUC columns:

```text
ACL, MCL, medial meniscus, lateral meniscus,
medial OA, lateral OA, PF OA,
effusion, synovitis, Baker's cyst,
contusion, fracture
```

The central problem was not “train one larger model.” It was:

1. convert multilingual reports and images into better supervision;
2. build an image-only reader that generalizes to hidden studies;
3. control runtime and failure modes in a nine-hour rerun;
4. make small, target-specific post-processing changes.

The strongest public solutions all converged on the same conclusion: **labels
and anatomy-aware inputs produced more gain than fashionable model changes**.

## Our path

The team started from the public code ecosystem and improved in short,
evidence-gated steps:

```text
0.943  early public stack
0.945  specialist stack
0.949  CoAtNet reader
0.950  reader fusion + FOV ladder
0.951  stronger public checkpoint family
0.954  laddered family
0.956  improved public composition
0.957  our own R-slot checkpoint + compact-model fusion
0.958  rank-band and per-finding routing
0.959  newtable anchor + A5 Effusion residual
```

The final wave stayed at `0.959 public / 0.945 private`. The most useful
late-game change was the A5 Effusion residual at dose `0.30`; larger or broader
residual bundles repeatedly failed local or hidden checks.

## Final scoring wave

Every final-wave candidate is preserved under
[`final_submissions/`](final_submissions/README.md).

| Submission | Ref | Public | Private | Role |
|---|---:|---:|---:|---|
| `A5eff30-only V1` | 57481279 | 0.959 | 0.945 | strongest clean anchor |
| `A5eff20-only V1` | 57493876 | 0.959 | 0.945 | lower-dose fallback |
| `mm08 V1` | 57514882 | 0.959 | 0.945 | CoAtFull MedMen residual |
| `allgold V6` | 57525829 | 0.959 | 0.945 | three-child conservative route |
| `allproxy V4` | 57525824 | 0.959 | 0.945 | three-child aggressive route |
| `R150 V2` | 57530094 | 0.959 | 0.945 | final reader-scale candidate |

The last two scoring submissions by time were `allgold` and `R150`; because
several submissions were nearly simultaneous, the whole final wave is archived
instead of guessing which two a reader might mean.

`A5eff30 + Baker12` (`ref 57509367`) is retained as a documented failure:
Kaggle reported a notebook timeout and no score.

## Repository map

- [`docs/COMPETITION.md`](docs/COMPETITION.md): competition card, metric,
  data shape, leaderboard, and interpretation boundaries.
- [`docs/TIMELINE.md`](docs/TIMELINE.md): chronological exploration history.
- [`experiments/EXPERIMENT_LEDGER.csv`](experiments/EXPERIMENT_LEDGER.csv):
  the original detailed experiment ledger.
- [`experiments/FINAL_DECISION.md`](experiments/FINAL_DECISION.md): the final
  post-processing decision and the reasons alternatives were rejected.
- [`public_intel/TOP_WRITEUPS.md`](public_intel/TOP_WRITEUPS.md): summaries and
  links to the strongest post-competition write-ups.
- [`docs/LESSONS.md`](docs/LESSONS.md): what to do differently next time.
- [`final_submissions/`](final_submissions/README.md): final notebooks,
  manifests, dev receipts, and scoring references.

## Reading the result correctly

- Public and private leaderboards must be treated as different samples.
- A displayed `0.959` is not proof that two submissions are equal at full
  precision.
- A local proxy gain below roughly `0.001` is usually too small to predict a
  displayed leaderboard move.
- A nine-hour code competition can lose an otherwise strong submission to
  runtime variance. Inference accounting is part of the model.
- The 58-expert-study panel is a useful filter, not a reliable ranker.

## Reproducibility and private assets

The notebooks reference public Kaggle datasets and a small number of private
artifacts used by the team. Those artifacts are not redistributed here. A reader
must attach their own legally obtained competition data, public weights, and
eligible private artifacts before rerunning a notebook.

See [`docs/ATTRIBUTIONS.md`](docs/ATTRIBUTIONS.md) for attribution and
[`NOTICE.md`](NOTICE.md) for the archive’s legal and sharing boundary.
