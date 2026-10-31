# What To Do Better Next Time

This is the highest-value section of the archive. The lessons are based on
observed public and hidden results, not only on local proxy scores.

## 1. Spend the first budget on the validation system

The 58 gold studies were repeatedly used for label design, weight search, gate
selection, and candidate screening. That made the panel optimistic and made
differences below roughly `0.02` unreliable for per-finding decisions.

Next time:

- freeze a pure holdout before looking at labels;
- use repeated grouped folds on the largest available weak-label surface;
- write the minimum detectable effect and kill rule before each experiment;
- record both panel direction and real LB direction, but never pretend they are
  the same measurement.

## 2. Treat labels as the primary model

Every large public write-up found the same leverage:

- one report-reading LLM is a weak teacher;
- image-aware multimodal annotation is materially better;
- continuous probabilities beat six-bin or hard labels;
- report silence must not be treated as a negative;
- site/hospital habits create structured label noise.

Next time, build a label-quality evaluation harness before training a new
backbone. A strong model trained on the wrong target definition cannot recover
the missing information.

## 3. Model the anatomy, not only the image

The strongest solutions used one or more of:

- physical geometry and slice-order normalization;
- knee-centred native crops;
- bone landmarks and compartment crops;
- ROI/region pooling;
- lesion or anatomy boxes as training-only auxiliary targets;
- side/laterality normalization.

The recurring failure mode was a close-up without global context. The successful
pattern preserved both.

## 4. Prefer independent information over correlated ensemble members

Adding two similar checkpoints rarely helped. Helpful diversity came from:

- different views or planes;
- different anatomical crops;
- different label recipes;
- different backbones when disagreement was real;
- a genuinely independent public model family.

Always measure rank correlation and marginal blend gain, not just the member’s
solo score.

## 5. Do inference engineering early

Late timeout risk was not a deployment detail; it was a candidate-selection
constraint. The archive contains several locally strong submissions that
received no score because the hidden rerun exceeded the runtime limit.

Next time:

- budget every model forward before choosing the ensemble;
- preserve a fallback submission at each checkpoint;
- run a hidden-scale timing smoke test early;
- prefer fewer independent members over one more marginal residual;
- make each stage able to skip safely without corrupting the final CSV.

## 6. Use rank-space surgery for AUC

For macro AUC, probability calibration does not change the metric. The useful
operations were:

- percentile-rank blending;
- per-target residual doses;
- pair-level fixed/broken analysis;
- exact fallback to the anchor;
- small changes with a mechanism and a stable fold direction.

Do not fit a flexible stacker on a repeated 58-study panel. If a change cannot
be explained as a small number of rank inversions, it is probably overfit.

## 7. Public code is leverage, not strategy

Public assets accelerated the starting point, but the final gap was made by:

- better supervision;
- geometry and anatomy;
- rigorous ablations;
- understanding why the public blend path worked.

The archive therefore preserves both the public references and the negative
results from the solo entry.

## 8. The next competition checklist

1. Build a competition card before writing a model.
2. Reproduce the metric and submission schema.
3. Create one reproducible OOF/proxy surface and one small gold panel.
4. Build a fast image-only baseline.
5. Create labels with language-aware and image-aware readers.
6. Add one anatomical input mechanism at a time.
7. Learn the runtime budget before building a large ensemble.
8. Use paired bootstrap and shuffled/label-noise controls.
9. Keep a fail-open submission path.
10. Reserve the last submissions for the candidates that have hidden evidence,
    not for local proxy experiments.
