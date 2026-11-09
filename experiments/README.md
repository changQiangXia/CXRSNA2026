# Experiment Archive

`EXPERIMENT_LEDGER.csv` is the original chronological ledger from the competition.
It contains hypotheses, changes, local metrics, online observations, decisions,
and artifact paths. It is the detailed audit trail for the work performed, not a
claim that every local artifact was committed.

The reports in this directory are time-stamped working snapshots. Statements
such as “current”, `PENDING`, or “not submitted” describe only the timestamp at
the top of that report. For final submission status, use
[`../final_submissions/README.md`](../final_submissions/README.md) and
[`../ARCHIVE_MANIFEST.json`](../ARCHIVE_MANIFEST.json).

Supporting documents:

- `FINAL_DECISION.md`: final post-processing choice and rejected alternatives.
- `POSTPROCESSING.md`: evidence map for rank residuals, reader doses, gates,
  fallbacks, and failure modes.
- `CLIMB_943_to_958.md`: the main public/ensemble climb.
- `RUNTIME_RISK.md`: why several late candidates timed out.
- `PUBLIC_INTEL_CROSSCHECK.md`: offline discussion/notebook cross-check.
- `EARLY_CV_EVIDENCE.md`: early validation and local-measurement notes.

The ledger may contain local paths and private artifact handles. It is retained
for auditability, not as a drop-in executable environment. A referenced local
report, tool, dataset, checkpoint, or log that is absent from the clone falls
outside the archived scope; see
[`../docs/COMPLETENESS.md`](../docs/COMPLETENESS.md).
