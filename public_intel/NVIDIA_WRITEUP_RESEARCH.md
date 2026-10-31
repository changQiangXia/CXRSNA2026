# Deep Research: Strong Public Write-Ups

Research workflow: Kaggle discussion/write-up retrieval plus the NVIDIA Kaggle
skill’s write-up and research-brief guidance. Scores below are the scores stated
by the write-up authors unless explicitly marked as a fetched leaderboard
value. Popularity (votes/comments) is not treated as performance.

## Research question

The archived entry's final result was `0.959 public / 0.945 private`. The high-score public
write-ups reached roughly `0.965–0.970 public` and `0.954–0.960 private`.
What did those teams do that is both technically and operationally different
from a large ensemble of public models?

## Score and approach matrix

| Final role | Team / contributor | Reported public / private | Main source of gain | Fusion style |
|---|---|---:|---|---|
| 1st | Team Kangaroo (`tascj0` + `liushuzhi`; companion post by `sakaku`) | `0.969 / 0.960` | Agentic image-aware labels, ROI/lesion boxes, anatomy-guided readers | complementary model groups |
| 2nd | MURAD (`azamat1ch` et al.) | `0.969 / 0.960` | LLM report/image labels, OOF teacher mixing, six 2.5D readers | hand-set probability + rank blend, specialists |
| 3rd | DataTech Club | `0.968 / 0.959` | multimodal soft labels, OAI supervision, balanced checkpoint groups | group-aware probability blend |
| 5th | Rashmi B team | `0.968 / 0.958` (write-up around `0.958` private) | calibrated labels, bone masks, crops and region specialists | weighted probability + per-finding rank blends |
| 7th | BarryZhou | `0.970 / 0.957` | competition-data-only three-read labels + label-query reader | equal rank mean of four recipes |
| 8th | Tomoki Hirose et al. | public/private not both independently captured here | image-first Astra labels, calibrated OOF self-distillation, 168-slice cache | global/local multi-view readers |
| 22nd | matsurih | `0.965 / 0.954` | DICOM attributes, femur landmarks, compartment models, image labels | 56 networks, per-finding OOF weights |
| 19th | yuto083 / shin0000 et al. | final blend around `0.965 / 0.955` | ensemble distillation + MedSAM-guided global/local views | fixed three-model rank blend |
| 49th | Komil Parmar | `0.962 / 0.951` | whole-study 2.5D reader, scanner-grouped folds, teacher labels | four-member per-finding rank blend |
| 33rd | hirokenn / team | `0.966 / 0.952` ensemble; single model `~0.962 / 0.947` | no external training data, structured LLM labels, DINO/CoAt reader | rank ensemble |
| 235th | Chris Deotte / team | best `0.959 public` at their finish | simple image reader plus report/image labels | rank blend with public strong notebook |

## What the winners actually optimized

### 1. Labels were the model

The first-place and second-place solutions both concentrated most of their
effort on supervision:

- continuous probabilities;
- report plus image evidence, with the agent able to request more slices;
- explicit finding criteria and “not mentioned” handling;
- image-only or verification reads to avoid copying report errors;
- out-of-fold teacher predictions as a second supervision signal;
- hospital/site-specific corrections for systematically biased findings such
  as Synovitis.

The 1st-place write-up reports that replacing earlier multimodal labels with
Astra labels moved a matched CoAtNet from roughly `0.922` to `0.935` public
AUC. This is much larger than a typical post-processing gain.

The 7th-place no-external-data write-up makes the same point from a smaller
resource envelope: three Astra reads, a hospital-level Synovitis correction,
and a cross-model teacher moved the solution into the top ten.

### 2. Anatomy beat “larger backbone”

Strong solutions repeatedly added one of:

- physical geometry and patient-coordinate slice ordering;
- side and plane normalization;
- knee-centred/field-of-view crops;
- femur landmarks and compartment-specific crops;
- target-specific ROI/box pooling;
- lesion boxes as training-only auxiliary supervision;
- in-box attention or regional MIL.

The 5th-place team showed why both global and local views matter: a close-up
without the whole-knee context was not automatically better. The 22nd-place
solution went further with femur landmarks and a compartment classifier that
could not see the opposite compartment, structurally blocking medial-to-lateral
shortcuts.

### 3. Diversity had to be real

The winners added checkpoints with different error profiles:

- 2nd place used different backbones, views, seeds, and two finding specialists;
- 3rd place used explicit groups with different labels, OAI dose, resolutions,
  and readout types;
- 5th place added regional crops and a dedicated Lateral Meniscus fine-tune;
- 7th place found that four similar models added only `+0.001 public` and
  nothing private over the best single model;
- 22nd place valued plane models and compartment crops more than tiny
  architecture/head changes.

The practical test is whether a new member’s ranking-error profile is different
enough to repair the existing blend, beyond its solo score.

### 4. Fixed/simple blends beat flexible post-processing

Several independent write-ups report that flexible weights did not transfer:

- 2nd place: tuned weights lost `0.002–0.007` to fixed weights on held-out
  exams;
- 7th place: equal-weight rank mean was enough; the model family lacked
  diversity;
- 22nd place: changes in the main recipe were often more correlated than two
  seeds; the useful members came from different data views;
- 49th place: public probe reads were more useful than a tiny gold panel for
  per-finding decisions.

This aligns with the archived experiment ledger: per-target rank residuals and low-dose
corrections were useful; learned stackers, isotonic calibration, and flexible
co-occurrence gates repeatedly failed.

### 5. Inference engineering was a scoring axis

The best write-ups treat runtime as part of the solution:

- one decode per study with shared preprocessing;
- process/worker separation and model-by-model cleanup;
- bounded/skipable members;
- robust DICOM parsing across transfer syntaxes;
- FP16, chunking, TensorRT, or C++ readers where justified;
- candidate selection based on whether it fits the nine-hour hidden rerun.

The endgame evidence confirmed this directly: a candidate can look strong locally and
still receive no score after a timeout. A fallback submission is not optional.

### 6. Distillation can buy both score and runtime

The 19th-place write-up is a useful counterexample to “a bigger ensemble always
wins.” It distilled a seven-hour multi-family teacher into a ConvNeXt-Tiny
student trained on OOF teacher predictions mixed with label probabilities. The
student was reported at roughly `0.962 public / 0.951 private` in about half an
hour, slightly above its teacher, and left room for the final ensemble under
the nine-hour limit.

The 8th-place solution shows a related pattern: a larger slice cache improved
public AUC from `0.930` to `0.937`, image-first labels improved it further, and
a second OOF self-distillation round gave a smaller but useful gain.

## Public reference links

- [1st place — Team Kangaroo (tascj0)](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752468)
- [1st-place companion — sakaku](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752474)
- [2nd place — MURAD](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752370)
- [3rd place — DataTech Club](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752510)
- [5th place — Rashmi B team](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752190)
- [7th place — BarryZhou](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752217)
- [8th place — Tomoki Hirose et al.](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752219)
- [22nd place — matsurih](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752052)
- [19th place — yuto083 / shin0000 et al.](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752252)
- [49th place — Komil Parmar](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/751972)
- [33rd place — no external data](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/751962)
- [235th place — report/image labels](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/751888)

## Transfer priorities for next time

### Priority 1: build an image-aware label factory

Use one finding-specific protocol, continuous probabilities, explicit
“not mentioned” semantics, and an evidence trace. Evaluate both ranking and
calibration on a genuinely held-out expert set. Do not let an LLM annotate
without a viewer or without a rule for uncertainty.

### Priority 2: build anatomy-aware input once

Create a cached, geometry-normalized study representation with:

- side-corrected orientation;
- physical field of view;
- five or six series roles;
- knee centre and compartment landmarks;
- region boxes and optional lesion boxes.

Use the annotations as training-time attention/auxiliary supervision so hidden
inference does not need an extra LLM or detector unless the budget allows it.

### Priority 3: one strong reader before a zoo

Start with a 2.5D window reader and per-finding attention pooling. Add label
quality, ROI pooling, and report/lesion auxiliary heads before adding more
backbones. A large ensemble of correlated readers is not a substitute for
better supervision.

### Priority 4: validation by site and anatomy

Use scanner/site-grouped folds, not random folds. Keep the 58 expert studies as
a sanity and definition check. Use a larger weak-label surface for model
selection, and reserve a completely untouched subset for final decisions.

### Priority 5: explicit runtime portfolio

Decide the number of members from the measured hidden-scale time budget. Keep
an anchor submission and make every extra stage fail-open. A model that cannot
finish is worth zero regardless of its local AUC.

## What not to copy blindly

- Do not copy a public blend without reproducing its checkpoint lineage,
  geometry, series roles, and preprocessing.
- Do not treat the 58-study gold panel as a reliable weight optimizer.
- Do not add identical seeds/backbones and call it diversity.
- Do not use a flexible target-specific stacker just because it improves the
  local proxy.
- Do not publish a notebook with private data paths or uncontrolled external
  artifacts without checking the competition and dataset terms.
