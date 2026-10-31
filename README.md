# RSNA Knee Abnormality Detection 2026 — Complete Archive

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
