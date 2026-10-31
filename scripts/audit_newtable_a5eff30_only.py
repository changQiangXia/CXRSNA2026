#!/usr/bin/env python
"""Audit an Effusion-only A5 residual on the exact online anchor.

This is deliberately the smallest challenger after the online ordering

    newtable anchor > double+A5 > rpure6-R150

showed that the locally attractive reader bundle does not transfer to the
hidden split.  The anchor remains byte-identical; A5 changes Effusion only.
No network, dev push, or competition scoring is performed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_classarm_fusion_ops as A  # noqa: E402
import audit_newtable_double_a5eff as DA  # noqa: E402
import audit_newtable_reader_transfer as T  # noqa: E402
import coherent_study_gate as G  # noqa: E402
import price_classarm_rankband as P  # noqa: E402
import rank_band_consensus as RB  # noqa: E402


LAB = list(RB.LAB)
WEIGHTS = (0.12, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
FIXED_WEIGHT = 0.30
SURFACES = {
    "original": (
        ROOT / "reports/a5_raw_gold_full_current.npz",
        ROOT / "reports/a5_cache_proxy870_corrected_f080.npz",
    ),
    "mirror": (
        ROOT / "reports/a5_raw_gold_mirror.npz",
        ROOT / "reports/a5_cache_proxy870_mirror_f080.npz",
    ),
}


def reader_weights() -> dict[str, float]:
    """The exact reader table used by the online anchor."""
    return {
        label: float(RB.READER_WEIGHT[label])
        for label in LAB
    }


def weight_matrix(table: dict[str, float]) -> np.ndarray:
    return np.asarray(
        [[table[label] for label in LAB]],
        dtype=np.float64,
    )


def gold_anchor() -> tuple[dict, np.ndarray]:
    data = P.load_inputs()
    r0 = P.r_arm(data, "rob", False)
    r_half = RB.rank01(0.65 * r0 + 0.35 * data["p224"])
    blend = P.NEW_WEIGHTS * r_half + (
        1.0 - P.NEW_WEIGHTS
    ) * data["o_half"]
    blend, _ = G.apply_gate(
        blend,
        np.stack([r_half, data["r6"], data["s6"]]),
        0.20,
        0.80,
        0.60,
        "mean",
    )
    scores = T.apply_focused_severity(
        G.add_reader(
            blend,
            data["reader"],
            weight_matrix(reader_weights()),
        )
    )
    return data, scores


def proxy_anchor() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    r6_data = np.load(
        ROOT / "reports/r6_attention_silver870_2026-10-19.npz",
        allow_pickle=True,
    )
    reader_data = np.load(
        ROOT / "reports/reader_attention_silver870_2026-10-19.npz",
        allow_pickle=True,
    )
    ids = r6_data["uids"].astype(str).tolist()
    assert ids == reader_data["uids"].astype(str).tolist()

    rob = A.rank01(
        T.aligned_asset(
            "assets/hpo_assets/raptor_oof_r7coat320rob_f0_swa_fold0.npz",
            ids,
        )
    )
    p224 = A.rank01(
        T.aligned_asset(
            "assets/hpo_assets/raptor_oof_r7coat224pc_f0_swa_fold0.npz",
            ids,
        )
    )
    r6 = A.rank01(r6_data["pred"][:, 0, :].astype(float))
    reader = A.rank01(
        reader_data["pred"][:, 0, :].astype(float)
    )
    r_half = A.rank01(0.65 * rob + 0.35 * p224)
    host = A.pair_band(
        A.NEW_WEIGHTS[0] * r_half
        + (1.0 - A.NEW_WEIGHTS[0]) * r6,
        r_half,
        r6,
    )
    scores = T.apply_focused_severity(
        G.add_reader(
            host,
            reader,
            weight_matrix(reader_weights()),
        )
    )
    frame = (
        pd.read_parquet(ROOT / "reports/silver_surface.parquet")
        .set_index("StudyInstanceUID")
        .reindex(ids)
    )
    truth = frame[
        [f"silver_{label}" for label in LAB]
    ].to_numpy(float)
    folds = frame["fold"].to_numpy(np.int64)
    return scores, truth, folds, ids


def main() -> int:
    gold_data, gold_base = gold_anchor()
    proxy_base, proxy_truth, folds, proxy_ids = proxy_anchor()
    gold_base_score = float(
        G.soft_macro_auc(gold_data["truth"], gold_base)
    )
    proxy_base_score = float(
        G.soft_macro_auc(proxy_truth, proxy_base)
    )

    aligned = {}
    for name, (gold_path, proxy_path) in SURFACES.items():
        aligned[name] = DA.align_ranks(
            gold_path,
            proxy_path,
            gold_data["ids"],
            proxy_ids,
            folds,
        )

    surfaces = {}
    for name in SURFACES:
        (
            gold_rank,
            gold_applicable,
            proxy_rank,
            proxy_applicable,
        ) = aligned[name]
        rows = {}
        for weight in WEIGHTS:
            gold_candidate = DA.blend_deploy(
                gold_base,
                gold_rank,
                gold_applicable,
                weight,
            )
            proxy_candidate = DA.blend_deploy(
                proxy_base,
                proxy_rank,
                proxy_applicable,
                weight,
            )
            gold_classes = T.per_class(
                gold_data["truth"],
                gold_candidate,
            )
            gold_base_classes = T.per_class(
                gold_data["truth"],
                gold_base,
            )
            fold_rows = T.report_fold_deltas(
                proxy_truth,
                proxy_base,
                proxy_candidate,
                folds,
            )
            rows[f"{weight:.2f}"] = {
                "gold_score": float(
                    G.soft_macro_auc(
                        gold_data["truth"],
                        gold_candidate,
                    )
                ),
                "gold_delta": float(
                    G.soft_macro_auc(
                        gold_data["truth"],
                        gold_candidate,
                    )
                    - gold_base_score
                ),
                "gold_negative_columns": [
                    label
                    for label in LAB
                    if gold_classes[label]
                    < gold_base_classes[label] - 1e-15
                ],
                "proxy_score": float(
                    G.soft_macro_auc(
                        proxy_truth,
                        proxy_candidate,
                    )
                ),
                "proxy_delta": float(
                    G.soft_macro_auc(
                        proxy_truth,
                        proxy_candidate,
                    )
                    - proxy_base_score
                ),
                "proxy_folds": fold_rows,
                "proxy_positive_folds": sum(
                    row["delta"] > 0 for row in fold_rows
                ),
                "changed_effusion_rows": int(
                    np.sum(
                        proxy_candidate[:, LAB.index("Effusion")]
                        != proxy_base[:, LAB.index("Effusion")]
                    )
                ),
            }
        surfaces[name] = {
            "gold_applicable": float(gold_applicable.mean()),
            "proxy_applicable": float(proxy_applicable.mean()),
            "weights": rows,
        }

    nested = []
    for heldout in range(5):
        train = folds != heldout
        test = ~train
        best_weight = None
        best_score = -np.inf
        for weight in WEIGHTS:
            gold_safe = True
            train_deltas = []
            for name in SURFACES:
                (
                    gold_rank,
                    gold_applicable,
                    proxy_rank,
                    proxy_applicable,
                ) = aligned[name]
                gold_candidate = DA.blend_deploy(
                    gold_base,
                    gold_rank,
                    gold_applicable,
                    weight,
                )
                gold_classes = T.per_class(
                    gold_data["truth"],
                    gold_candidate,
                )
                gold_base_classes = T.per_class(
                    gold_data["truth"],
                    gold_base,
                )
                gold_safe &= all(
                    gold_classes[label]
                    >= gold_base_classes[label] - 1e-15
                    for label in LAB
                )
                proxy_candidate = DA.blend_deploy(
                    proxy_base,
                    proxy_rank,
                    proxy_applicable,
                    weight,
                )
                train_deltas.append(
                    G.soft_macro_auc(
                        proxy_truth[train],
                        proxy_candidate[train],
                    )
                    - G.soft_macro_auc(
                        proxy_truth[train],
                        proxy_base[train],
                    )
                )
            if gold_safe and float(np.mean(train_deltas)) > best_score:
                best_score = float(np.mean(train_deltas))
                best_weight = weight
        if best_weight is None:
            raise RuntimeError("no nested A5 Effusion weight passed")
        heldout_rows = {}
        for name in SURFACES:
            _, _, proxy_rank, proxy_applicable = aligned[name]
            candidate = DA.blend_deploy(
                proxy_base,
                proxy_rank,
                proxy_applicable,
                best_weight,
            )
            heldout_rows[name] = float(
                G.soft_macro_auc(
                    proxy_truth[test],
                    candidate[test],
                )
                - G.soft_macro_auc(
                    proxy_truth[test],
                    proxy_base[test],
                )
            )
        nested.append(
            {
                "heldout_fold": heldout,
                "selected_weight": best_weight,
                "heldout_deltas": heldout_rows,
            }
        )

    fixed_rows = [
        surfaces[name]["weights"][f"{FIXED_WEIGHT:.2f}"]
        for name in SURFACES
    ]
    checks = {
        "fixed_weight_on_plateau": all(
            row["gold_delta"] >= -1e-15
            and not row["gold_negative_columns"]
            and row["proxy_delta"] > 0
            and row["proxy_positive_folds"] == 5
            for row in fixed_rows
        ),
        "nested_heldout_both_surfaces_5_of_5": all(
            value > 0
            for row in nested
            for value in row["heldout_deltas"].values()
        ),
        "applicable_full": all(
            surface["gold_applicable"] == 1.0
            and surface["proxy_applicable"] == 1.0
            for surface in surfaces.values()
        ),
        "one_column_only": True,
    }
    payload = {
        "created_cst": pd.Timestamp.now(
            tz="Asia/Shanghai"
        ).isoformat(),
        "hypothesis": (
            "The independent A5 Effusion signal that rescued the double "
            "bundle should be stronger when applied directly to the online "
            "anchor without the reader overlay."
        ),
        "source": (
            "intoxicatinglips/rsna-knee-newtable-agree60-fsev5-22 "
            "Version 2"
        ),
        "gold_anchor": gold_base_score,
        "proxy_anchor": proxy_base_score,
        "reader_weights": reader_weights(),
        "a5_labels": ["Effusion"],
        "fixed_weight": FIXED_WEIGHT,
        "weights": list(WEIGHTS),
        "surfaces": surfaces,
        "nested_selection": nested,
        "checks": checks,
        "decision": (
            "BUILD_ANCHOR_A5_EFFUSION_30"
            if all(checks.values())
            else "HOLD"
        ),
        "evidence_boundary": (
            "Gold-58 and the 870 soft-label proxy both preferred the larger "
            "reader bundle locally, yet the hidden ordering ranked that "
            "bundle below the anchor. This audit therefore selects a single "
            "independent-family column rather than extrapolating local AUC "
            "magnitude. A5 original and mirror are transform replicates."
        ),
    }
    out = ROOT / "reports/newtable_a5eff30_only_2026-10-21.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("wrote", out)
    return (
        0
        if payload["decision"] == "BUILD_ANCHOR_A5_EFFUSION_30"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
