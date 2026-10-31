"""Test whether Baker's A5 dose .14 beats the online-validated .12 candidate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_a5eff30_increment_axes as I  # noqa: E402
import audit_newtable_double_a5eff as DA  # noqa: E402
import audit_newtable_reader_transfer as T  # noqa: E402
import audit_r225_double35_a5eff20 as R  # noqa: E402
import audit_r225_reader_column_ablation as C  # noqa: E402
import coherent_study_gate as G  # noqa: E402
import rank_band_consensus as RB  # noqa: E402


LAB = list(RB.LAB)
BASE_DOSE = 0.12
CANDIDATE_DOSE = 0.14
REPLICATES = 2500
SEED = 20261414


def main() -> int:
    gold, gold_surface, gold_ids = C.gold_surfaces()
    proxy_surface, proxy_truth, proxy_ids, folds = C.proxy_surfaces()
    anchor_table = {
        label: float(RB.READER_WEIGHT[label])
        for label in LAB
    }
    gold_anchor = C.apply(gold_surface, anchor_table)
    proxy_anchor = C.apply(proxy_surface, anchor_table)
    aligned = {
        name: DA.align_ranks(
            gold_path,
            proxy_path,
            gold_ids.tolist(),
            proxy_ids.tolist(),
            folds,
        )
        for name, (gold_path, proxy_path) in R.A5_SURFACES.items()
    }

    rows = {}
    bootstrap = {}
    for surface_index, surface_name in enumerate(R.A5_SURFACES):
        gold_rank, gold_valid, proxy_rank, proxy_valid = aligned[
            surface_name
        ]
        for reader_index, reader_name in enumerate(gold_anchor):
            key = f"{surface_name}:{reader_name}"
            base_gold = I.blend_multi(
                gold_anchor[reader_name],
                gold_rank,
                gold_valid,
                {"Effusion": 0.30, "Baker's": BASE_DOSE},
            )
            candidate_gold = I.blend_multi(
                gold_anchor[reader_name],
                gold_rank,
                gold_valid,
                {"Effusion": 0.30, "Baker's": CANDIDATE_DOSE},
            )
            base_proxy = I.blend_multi(
                proxy_anchor[reader_name],
                proxy_rank,
                proxy_valid,
                {"Effusion": 0.30, "Baker's": BASE_DOSE},
            )
            candidate_proxy = I.blend_multi(
                proxy_anchor[reader_name],
                proxy_rank,
                proxy_valid,
                {"Effusion": 0.30, "Baker's": CANDIDATE_DOSE},
            )
            fold_rows = T.report_fold_deltas(
                proxy_truth,
                base_proxy,
                candidate_proxy,
                folds,
            )
            rows[key] = {
                "gold_delta": float(
                    G.soft_macro_auc(gold["truth"], candidate_gold)
                    - G.soft_macro_auc(gold["truth"], base_gold)
                ),
                "proxy_delta": float(
                    G.soft_macro_auc(proxy_truth, candidate_proxy)
                    - G.soft_macro_auc(proxy_truth, base_proxy)
                ),
                "folds": fold_rows,
                "positive_folds": sum(
                    row["delta"] > 0 for row in fold_rows
                ),
            }
            seed_offset = surface_index * 100 + reader_index
            bootstrap[key] = {
                "gold": R.bootstrap_delta(
                    gold["truth"],
                    base_gold,
                    candidate_gold,
                    SEED + seed_offset,
                ),
                "proxy": R.bootstrap_delta(
                    proxy_truth,
                    base_proxy,
                    candidate_proxy,
                    SEED + 10_000 + seed_offset,
                ),
            }

    checks = {
        "gold_nondegrading_all_six": all(
            row["gold_delta"] >= -1e-15 for row in rows.values()
        ),
        "proxy_positive_all_six": all(
            row["proxy_delta"] > 0 for row in rows.values()
        ),
        "proxy_positive_folds_5_of_5_all_six": all(
            row["positive_folds"] == 5 for row in rows.values()
        ),
        "proxy_bootstrap_ci_positive_all_six": all(
            result["proxy"]["ci95"][0] > 0
            for result in bootstrap.values()
        ),
    }
    decision = (
        "BUILD_A5EFF30_BAKER14"
        if all(checks.values())
        else "KEEP_BAKER12"
    )
    payload = {
        "created_cst": pd.Timestamp.now(
            tz="Asia/Shanghai"
        ).isoformat(),
        "parent": "A5eff30+Baker12",
        "candidate": "A5eff30+Baker14",
        "base_dose": BASE_DOSE,
        "candidate_dose": CANDIDATE_DOSE,
        "replicates": REPLICATES,
        "rows": rows,
        "bootstrap_14_vs_12": bootstrap,
        "checks": checks,
        "decision": decision,
        "evidence_boundary": (
            "Baker14 is a zero-extra-forward dose increment on the "
            "online-validated Baker12 host. It is adjacent to the first "
            "locally observed Gold break at .15 and therefore remains a "
            "single-variable challenger, not a replacement anchor."
        ),
    }
    out = ROOT / "reports/a5eff30_baker14_vs_12_2026-10-22.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("wrote", out)
    return 0 if decision.startswith("BUILD_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
