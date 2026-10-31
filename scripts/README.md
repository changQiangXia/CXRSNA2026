# Reproducibility Scripts

The scripts included here are the audit/build scripts for the final A5 and
post-processing candidates. They depend on the original local project layout and
are included for provenance.

- `build_newtable_a5eff30_only.py`: builds the A5 Effusion `.30` anchor.
- `audit_newtable_a5eff30_only.py`: checks the anchor's A5 cell and mounts.
- `build_newtable_a5eff30_r150.py`: builds the reader R150 candidate.
- `audit_a5eff30_r150.py`: computes the local combined pricing.
- `audit_newtable_a5eff30_r150_candidate.py`: static candidate audit.
- `audit_a5eff30_baker14.py`: documents the rejected `.14` dose escalation.

These are not a standalone package. Read the candidate manifests and the
`experiments/` documents before running them.
