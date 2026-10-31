# Top Public Write-Ups: Technical Summary

All links are from the competition discussion forum. The original text belongs
to its authors; this file is a technical summary and a reading guide.

## 1st place — Team Kangaroo

Links:

- [tascj0: 1st Place Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752468)
- [sakaku: 1st place solution — Better labels, anatomy-aware MRI models](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752474)

Public result in the write-up: public `0.969`, private `0.960`.

The team treated the problem primarily as a **labeling problem**. They generated
continuous study-level probabilities, 3D anatomical ROI boxes, and per-slice
lesion boxes with agentic multimodal readers.

Key mechanisms:

- continuous Astra probabilities instead of hard report labels;
- report-aware, image-aware verification;
- a trained guide derived iteratively from the 58 expert studies;
- anatomy boxes used for box pooling and in-box attention;
- lesion boxes and report embeddings as training-only auxiliary targets;
- a shared image backbone with target-specific pooling;
- a final ensemble combining several backbones and label recipes.

The matched-label comparison was decisive: replacing earlier multimodal labels
with Astra labels moved a CoAtNet from roughly `0.922` to `0.935` public AUC.
The model changes added further gains, but the largest leverage was supervision.

Their inference was engineered aggressively: one process per T4, TensorRT,
C++ DICOM reading, and reading only the fluid-sensitive series where possible.

## 2nd place — MURAD

Link: [2nd Place Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752370)

Public `0.969`, private `0.960`.

The solution used:

- multilingual report reading with GPT-6.1 Sol;
- GPT-6 Astra image-aware rereading of every training exam;
- targeted fixes for PF OA, Lateral OA, and Synovitis;
- out-of-fold teacher predictions mixed into the final soft labels;
- six 2.5D MIL models with different views and backbones;
- hand-set rank blend weights, not public-leaderboard search.

Their most transferable observations:

- report-only labels were insufficient;
- PF OA and Lateral OA needed definition-aware treatment;
- a broader image view was essential: early models read too few slices;
- specialist members helped only when they were genuinely unlike the core;
- tuned blend weights lost to fixed weights on held-out exams.

## 3rd place — DataTech Club

Link: [3rd Place Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752510)

Private `0.959`.

This was the most explicit example of **group-aware probability blending**:

- multimodal soft labels;
- PF/Lateral OA/Synovitis refinements;
- OAI external supervision;
- 2.5D windows with physical geometry;
- depth attention and OA-coupled heads;
- a large, curated ensemble organized into mature, architecture-balanced, and
  expert groups;
- a second hard-routed submission with independent specialist groups.

The team did not simply tune every member weight. They fixed group budgets and
used different fusion semantics for weak findings. Their write-up is a strong
reference for controlled ensemble composition under a runtime limit.

## 5th place — Rashmi B team

Link: [5th Place Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752190)

The solution combined:

- calibrated public report labels;
- LLM report and image interpretations;
- out-of-fold teacher predictions;
- bone-segmentation-driven full-field and regional crops;
- EfficientNetV2-M and ConvNeXt-Base families;
- region specialists and Lateral Meniscus fine-tunes;
- per-finding rank blends.

Important negative result: close-up crops without enough whole-knee context
were not automatically better. The team kept both global anatomy and local
resolution.

## 7th place — BarryZhou

Link: [7th place solution with no external training data](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752217)

Public `0.970`; private `0.957`.

This is the best compact example of a **competition-data-only** solution:

- three GPT-6 Astra reads: structured report+images, image-only, and
  verification;
- per-label rank blending;
- a hospital-level Synovitis correction;
- a cross-model teacher mapped back to the label prevalence;
- one 2.5D label-query network, four backbones/recipes;
- equal-weight per-label rank mean.

Their conclusion is important: label changes moved the board more than model
changes, and a four-model ensemble with the same labels and input pipeline added
little because the members were too correlated.

## 8th place — Tomoki Hirose et al.

Link: [8th Place Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752219)

The solution used a large, center-preserving slice cache (up to 168 slices) and
image-first Astra labels. Its label mixture combined three report-derived
sources with image assessments, using finding-specific image weights and a
neighboring-weight perturbation check.

It also ran two calibrated OOF self-distillation rounds:

```text
final training target = 0.6 * image/report soft label
                      + 0.4 * calibrated OOF teacher
```

This is a useful example of improving supervision while keeping the label
recipe fixed and auditable.

## 22nd place — matsurih (solo gold)

Link: [22nd Place Solo Gold Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752052)

Public `0.965`, private `0.954`.

This solution is especially useful for future small teams:

- DICOM-header-derived series attributes rather than trusting series names;
- femur segmentation and landmarks for compartment crops;
- a compartment classifier that sees one side at a time;
- image-only GPT-6 Astra labels for most findings;
- out-of-fold model predictions blended into the labels;
- 56 networks in 12 groups with per-finding weights fit on OOF predictions.

The write-up carefully distinguishes local anchor noise from public-leaderboard
noise and documents many failed post-processing ideas.

## 33rd place — no external data

Link: [33rd Place (Silver) Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/751962)

This is a useful lower-resource reference: no external training data, simpler
readers, and conservative blend choices. The write-up is a reminder that a
well-calibrated competition-data-only pipeline can reach silver without a large
model zoo.

## 49th place — Komil Parmar (solo silver)

Link: [49th place whole-study 2.5D reader](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/751972)

Public `0.962`, private `0.951`.

Notable contributions:

- whole-study slice-bag inference rather than random bag sampling;
- 5-fold folds grouped by scanner;
- scanner-name auditing and robust DICOM metadata handling;
- text teachers followed by image-teacher rounds;
- per-finding rank blend;
- a clever public probe:

```text
AUC_f ≈ 0.5 + 6 × (base submission score - one-finding inverted probe score)
```

The probe is useful when a public leaderboard hides per-column AUC, but it uses
submission budget and should be planned in advance.

## 19th place — yuto083 / shin0000 et al.

Link: [19th Place Solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/752252)

This is the clearest “distill the ensemble” case in the competition. An earlier
multi-family teacher took about seven hours, leaving almost no budget for
another strong branch. The team distilled it into a ConvNeXt-Tiny student:

- OOF teacher predictions from models that never saw the study;
- a 50/50 target mixture of LLM labels and calibrated OOF predictions;
- a slice-attention reader on a 140 mm / 384 px field of view;
- 32 epochs and about 0.5 hours of inference;
- the student reportedly reached about `0.962 public / 0.951 private`, slightly
  above its teacher.

The final three-model rank blend used fixed weights. Gold-optimized per-finding
weights improved the Gold panel but lost public score, so fixed weights were
kept.

## 235th place — report/image labels

Link: [Silver Medal solution](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/751888)

A practical smaller-scale example of deriving labels from reports and images,
then training a much simpler image reader. It supports the same high-level
conclusion: the first priority is label extraction and image-aware validation,
not a more exotic backbone.

## Discussion threads worth rereading

- [Competition overview and finding definitions](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733343)
- [Commercial LLM API rules](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733965)
- [External knee-MRI dataset rules](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/743416)
- [LLM report extraction benchmark](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/747658)
- [“Not addressed” is a label too](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733932)
- [Best single-model score thread](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304)
- [Tricks for the competition](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/745861)

## Cross-write-up synthesis

The independent top solutions converge on five priorities:

1. image-aware, finding-specific soft labels;
2. physical geometry and anatomical localization;
3. multiple genuinely different readers;
4. conservative blending with fixed or OOF-selected weights;
5. an inference path that can survive hidden-test I/O and runtime variation.
