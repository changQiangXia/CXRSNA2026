# Exploration Timeline

All dates are Beijing time unless a source explicitly says otherwise.

## 2026-10-04 — First usable public stack

The first valid archive point was around **0.943**, built by combining public
strong models and the solo entry’s rank post-processing. The initial lesson was that
the competition was already an ecosystem problem: copying a strong public
notebook without understanding its blend path was not enough.

## 2026-10-05–10-08 — Fast public-model climb

The solo entry moved through roughly:

```text
0.943 -> 0.945 -> 0.949 -> 0.950
```

Key axes:

- a stronger CoAtNet/Raptor reader;
- rank-space fusion instead of probability calibration;
- FOV/window laddering;
- careful preservation of the public 384/224 checkpoint pair.

The public leaderboard reacted positively, but the hidden test’s three-decimal
display made it impossible to attribute small changes to a single numeric
cause.

## 2026-10-11–10-15 — Checkpoints, ladder, and the first self-trained leg

The stack reached **0.951**, then **0.954**, as stronger public checkpoint
families and multi-scale inference were added.

A particularly important result was the R-slot experiment:

```text
public parent -> replace part of the Raptor slot with soup5 -> about 0.957
```

This was one of the few clean online A/B results. The solo entry learned that a
self-trained leg can be useful when it is geometrically aligned and blended at
a controlled weight; the same idea failed when checkpoint geometry differed.

## 2026-10-16 — Independent compact model and rank-band

The `S6` compact model was blended into the R7/CoAtNet lineage. This produced a
large rank-order improvement and established the design principle:

> a new, partially independent information source is more valuable than
> repeatedly tuning a correlated member.

The solo entry also began using agreement gates and rank bands, but later discovered
that flexible target-specific gates often overfit the 58-study panel.

## 2026-10-17–10-19 — Public ecosystem maturity

The working score reached **0.958**, then **0.959**. The solo entry invested in:

- reader dose and per-finding weighting;
- study-severity overlays;
- rank-band consensus;
- public labels and LLM-derived supervision;
- multiple residual screens.

This phase produced many locally attractive candidates that failed to cross the
hidden line. The ledger records the repeated pattern:

```text
local proxy gain
  + no independent hidden confirmation
  + small effect size
  -> not worth another submission
```

## 2026-10-20–10-21 — A5 Effusion becomes the real anchor

The A5 model was modest in isolation but its predictions were only partially
correlated with the host reader. On Effusion, the rank residual at `0.30`
survived multiple reader/A5 surfaces and produced the highest completed online
result.

This became the anchor:

```text
rsna-knee-newtable-a5eff30-only V1
ref 57481279
public 0.959
private 0.945
```

Lower dose at `0.20` was also selected but ranked below `.30`; higher doses and
more target columns were rejected or failed nested checks.

## 2026-10-22 — Endgame and runtime variance

The solo entry tested several final challengers:

| Candidate | Result |
|---|---|
| `A5eff30 + Baker12` | Kaggle timeout, no score |
| `mm08` CoAtFull MedMen residual | complete, `0.959 / 0.945` |
| `allgold` three-child route | complete, `0.959 / 0.945` |
| `allproxy` three-child route | complete, `0.959 / 0.945` |
| final `R150` reader scaling | complete, `0.959 / 0.945` |

The timeout of Baker12 and the success of mm08 demonstrated that the shared
heavy base had substantial runtime variance. The final decision was to stop
adding model forwards and use a smaller, explainable post-processing change.

## 2026-10-31 — Final archive

The final public leaderboard snapshot showed:

```text
public score   0.959
public rank    182
private score  0.945
```

The archive includes the complete final-wave scoring candidates and the
experiment ledger so the gap between displayed public score, private score, and
local proxy can be audited directly.
