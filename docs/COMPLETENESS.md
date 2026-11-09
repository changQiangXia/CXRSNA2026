# Archive Scope and Completeness

This document defines what a fresh `git clone` can and cannot reconstruct.

## Included

- Competition card, rules, metric, and leaderboard context.
- The chronological exploration narrative and detailed experiment ledger.
- Time-stamped working reports covering the major accepted and rejected paths.
- Final-wave notebooks, kernel metadata, candidate manifests, and selected
  dev receipts for six scored candidates.
- Public write-up summaries, links, topic index, and the NVIDIA-guided
  cross-solution analysis.
- Public leaderboard snapshot and final submission receipts.
- Private dataset handles and direct Kaggle links used by the final notebooks.
- Attribution, sharing constraints, and reusable scripts included for
  provenance and audit.

## Intentionally omitted

- Raw DICOM files and competition data.
- Study-level labels, generated label tables, and private feature stores.
- Model checkpoints and weights.
- Kaggle tokens, cookies, private credentials, and signed URLs.
- Full local logs, caches, virtual environments, and intermediate arrays.
- Hidden-rerun outputs that Kaggle does not expose for download.
- Reports and artifacts that remained local, generated, or redundant with the
  curated public record.

## Status and precision caveats

- Files under `experiments/` are time-stamped working snapshots. Words such as
  “current”, `PENDING`, or “not submitted” describe the timestamp at the top of
  that file. Later outcomes are consolidated in
  [`final_submissions/README.md`](../final_submissions/README.md) and
  [`ARCHIVE_MANIFEST.json`](../ARCHIVE_MANIFEST.json).
- Leaderboard scores are preserved at the displayed three-decimal precision.
  Exact hidden full-precision scores and the internal ordering of tied
  candidates are not present in the preserved public records.
- Scores quoted in `public_intel/` are author-reported claims. A fresh query or
  an independent reproduction may produce a different displayed value.

## What this means for a future clone

A fresh clone gives a curated **decision and source archive**, not a
byte-for-byte copy of the local competition workstation. The experiment ledger
and candidate manifests are indexes into the original workspace. A referenced
`reports/...`, `tools/...`, `data/...`, `logs/...`, or checkpoint path that is
not present was not part of this archive. It may have been an intermediate
artifact, a generated file, or an intentionally excluded asset.

The archived final notebooks are source snapshots. Running them requires the
competition data, public datasets, private artifacts, and Kaggle environment
described by their `kernel-metadata.json` files. The private dataset links are
listed in [PRIVATE_ASSETS.md](PRIVATE_ASSETS.md).
Those metadata files record submission-time dataset handles, not the dataset
bytes. Third-party datasets may later be revised, deleted, or placed behind
different access controls.

## Reproducibility boundary

The repository supports:

- understanding the available decision sequence;
- auditing the final candidate designs and scoring references;
- locating the public evidence and external write-ups;
- reattaching authorized assets and rerunning a candidate in a compatible
  Kaggle environment;
- continuing a similar project with the documented validation and runtime
  rules.

It does not support:

- reproducing every intermediate experiment from this repository alone;
- redistributing competition data or private weights;
- recovering a hidden-rerun prediction file or exact full-precision score that
  was never published;
- treating archived notebooks as a standalone installable package;
- assuming that every local path or audit report referenced by a historical
  note is present in the clone.
