# Final Submissions

This directory preserves the available final-wave scoring source and receipt
record. Each candidate directory contains:

- the notebook source (`.ipynb`);
- the Kaggle kernel metadata;
- the candidate manifest;
- selected dev receipts and prediction files under `receipts/`.

The directories are archival snapshots. They are not guaranteed to run without
the private/public Kaggle datasets named in their manifests.
In the status column, `complete` means Kaggle completed the scoring rerun; it
does not imply that the clone contains all data or weights used by that run.

## Final-wave table

| Directory | Kernel | Ref | Public | Private | Status |
|---|---|---:|---:|---:|---|
| `2026-10-22_r150` | `rsna-knee-newtable-a5eff30-r150` | 57530094 | .959 | .945 | complete |
| `2026-10-22_allgold` | `rsna-knee-a5eff30-adapted20v2-soup75-r384allgold` | 57525829 | .959 | .945 | complete |
| `2026-10-22_allproxy` | `rsna-knee-a5eff30-adapted20v2-soup75-r384allproxy` | 57525824 | .959 | .945 | complete |
| `2026-10-22_mm08` | `rsna-knee-a5eff30-coatfull-stable11-mm08` | 57514882 | .959 | .945 | complete |
| `2026-10-21_a5eff30_only` | `rsna-knee-newtable-a5eff30-only` | 57481279 | .959 | .945 | complete |
| `2026-10-21_a5eff20_only` | `rsna-knee-newtable-a5eff20-only` | 57493876 | .959 | .945 | complete |

## Kaggle links

- [A5eff30-only V1](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-newtable-a5eff30-only)
- [A5eff20-only V1](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-newtable-a5eff20-only)
- [mm08 V1](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-a5eff30-coatfull-stable11-mm08)
- [allgold V6](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-adapted20-v2-soup75-r384-all-gold)
- [allproxy V4](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-adapted20-v2-soup75-r384-all-proxy)
- [R150 V2](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-newtable-a5eff30-r150)

The Kaggle entry links identify the owning kernels, while the archived
notebook, metadata, and SHA256 values identify the exact source snapshot kept
here. A kernel page may later point to a different version.

## The two last chronological scorings

The final two submissions by submission order were:

```text
57525829  allgold V6
57530094  R150 V2
```

`allproxy` was submitted essentially simultaneously with `allgold`; all final
wave candidates are documented here to avoid a name/timestamp ambiguity. Six
completed scoring candidates have source snapshots; Baker12 is represented by
its scoring reference in
[`../results/final_submission_receipts.csv`](../results/final_submission_receipts.csv)
and the historical reports under `../experiments/`.

## Timeout record

`rsna-knee-newtable-a5eff30-baker12` Version 1, ref `57509367`, is documented as
`COMPLETE` with no score. Kaggle’s error says the notebook exceeded the allowed
runtime. It is not counted as a successful candidate.

Kernel entry:
[rsna-knee-newtable-a5eff30-baker12](https://www.kaggle.com/code/intoxicatinglips/rsna-knee-newtable-a5eff30-baker12)

## What is deliberately absent

- raw competition DICOMs;
- trained checkpoint files;
- private raw labels;
- Kaggle tokens and cookies;
- full hidden-rerun output files that were never downloadable.

See `../NOTICE.md`.
