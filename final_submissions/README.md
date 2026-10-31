# Final Submissions

This directory preserves the complete final-wave scoring record. Each candidate
directory contains:

- the notebook source (`.ipynb`);
- the Kaggle kernel metadata;
- the candidate manifest;
- selected dev receipts and prediction files under `receipts/`.

The directories are archival snapshots. They are not guaranteed to run without
the private/public Kaggle datasets named in their manifests.

## Final-wave table

| Directory | Kernel | Ref | Public | Private | Status |
|---|---|---:|---:|---:|---|
| `2026-10-22_r150` | `rsna-knee-newtable-a5eff30-r150` | 57530094 | .959 | .945 | complete |
| `2026-10-22_allgold` | `rsna-knee-a5eff30-adapted20v2-soup75-r384allgold` | 57525829 | .959 | .945 | complete |
| `2026-10-22_allproxy` | `rsna-knee-a5eff30-adapted20v2-soup75-r384allproxy` | 57525824 | .959 | .945 | complete |
| `2026-10-22_mm08` | `rsna-knee-a5eff30-coatfull-stable11-mm08` | 57514882 | .959 | .945 | complete |
| `2026-10-21_a5eff30_only` | `rsna-knee-newtable-a5eff30-only` | 57481279 | .959 | .945 | complete |
| `2026-10-21_a5eff20_only` | `rsna-knee-newtable-a5eff20-only` | 57493876 | .959 | .945 | complete |

## The two last chronological scorings

The final two submissions by submission order were:

```text
57525829  allgold V6
57530094  R150 V2
```

`allproxy` was submitted essentially simultaneously with `allgold`; all final
wave candidates are retained here to avoid a name/timestamp ambiguity.

## Timeout record

`rsna-knee-newtable-a5eff30-baker12` Version 1, ref `57509367`, is documented as
`COMPLETE` with no score. Kaggle’s error says the notebook exceeded the allowed
runtime. It is not counted as a successful candidate.

## What is deliberately absent

- raw competition DICOMs;
- trained checkpoint files;
- private raw labels;
- Kaggle tokens and cookies;
- full hidden-rerun output files that were never downloadable.

See `../NOTICE.md`.
