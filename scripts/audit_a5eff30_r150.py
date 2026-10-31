"""Price reader R150 and A5 Effusion .30 together on the .959 anchor."""
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
READER_SCALE = 1.50
A5_WEIGHT = 0.30
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


def gold_host(scale: float) -> tuple[dict, np.ndarray]:
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
    host = G.add_reader(
        blend,
        data["reader"],
        P.READER_WEIGHTS * scale,
    )
    return data, T.apply_focused_severity(host)


def proxy_host(scale: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
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
    weight = A.NEW_WEIGHTS[0]
    blend = A.pair_band(
        weight * r_half + (1.0 - weight) * r6,
        r_half,
        r6,
    )
    host = G.add_reader(
        blend,
        reader,
        P.READER_WEIGHTS * scale,
    )
    scores = T.apply_focused_severity(host)
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


def score(truth: np.ndarray, pred: np.ndarray) -> float:
    return float(G.soft_macro_auc(truth, pred))


def main() -> int:
    gold_data, gold_r100 = gold_host(1.0)
    _, gold_r150 = gold_host(READER_SCALE)
    proxy_r100, proxy_truth, folds, proxy_ids = proxy_host(1.0)
    proxy_r150, _, _, _ = proxy_host(READER_SCALE)
    assert len(proxy_truth) == len(proxy_r100) == len(proxy_r150)

    aligned = {
        name: DA.align_ranks(
            gold_path,
            proxy_path,
            gold_data["ids"],
            proxy_ids,
            folds,
        )
        for name, (gold_path, proxy_path) in SURFACES.items()
    }

    rows = {}
    outputs = {}
    for name, (
        gold_rank,
        gold_applicable,
        proxy_rank,
        proxy_applicable,
    ) in aligned.items():
        a5_gold = DA.blend_deploy(
            gold_r100,
            gold_rank,
            gold_applicable,
            A5_WEIGHT,
        )
        combined_gold = DA.blend_deploy(
            gold_r150,
            gold_rank,
            gold_applicable,
            A5_WEIGHT,
        )
        r150_gold = gold_r150
        a5_proxy = DA.blend_deploy(
            proxy_r100,
            proxy_rank,
            proxy_applicable,
            A5_WEIGHT,
        )
        combined_proxy = DA.blend_deploy(
            proxy_r150,
            proxy_rank,
            proxy_applicable,
            A5_WEIGHT,
        )
        r150_proxy = proxy_r150
        outputs[name] = {
            "a5": {"gold": a5_gold, "proxy": a5_proxy},
            "combined": {"gold": combined_gold, "proxy": combined_proxy},
            "r150": {"gold": r150_gold, "proxy": r150_proxy},
        }
        combined_gold_classes = T.per_class(
            gold_data["truth"],
            combined_gold,
        )
        a5_gold_classes = T.per_class(
            gold_data["truth"],
            a5_gold,
        )
        fold_rows = T.report_fold_deltas(
            proxy_truth,
            a5_proxy,
            combined_proxy,
            folds,
        )
        rows[name] = {
            "gold_delta_vs_a5": score(
                gold_data["truth"],
                combined_gold,
            )
            - score(gold_data["truth"], a5_gold),
            "gold_negative_columns_vs_a5": [
                label
                for label in LAB
                if combined_gold_classes[label]
                < a5_gold_classes[label] - 1e-15
            ],
            "proxy_delta_vs_a5": score(proxy_truth, combined_proxy)
            - score(proxy_truth, a5_proxy),
            "proxy_folds_vs_a5": fold_rows,
            "proxy_positive_folds_vs_a5": sum(
                row["delta"] > 0 for row in fold_rows
            ),
            "gold_delta_vs_r150": score(
                gold_data["truth"],
                combined_gold,
            )
            - score(gold_data["truth"], r150_gold),
            "proxy_delta_vs_r150": score(
                proxy_truth,
                combined_proxy,
            )
            - score(proxy_truth, r150_proxy),
            "gold_applicable": float(gold_applicable.mean()),
            "proxy_applicable": float(proxy_applicable.mean()),
        }

    bootstrap = {}
    for index, name in enumerate(SURFACES):
        bootstrap[name] = {
            "vs_a5_gold": T.paired_bootstrap(
                gold_data["truth"],
                outputs[name]["a5"]["gold"],
                outputs[name]["combined"]["gold"],
                2500,
                20261501 + index,
            ),
            "vs_a5_proxy": T.paired_bootstrap(
                proxy_truth,
                outputs[name]["a5"]["proxy"],
                outputs[name]["combined"]["proxy"],
                2500,
                20262001 + index,
            ),
            "vs_r150_gold": T.paired_bootstrap(
                gold_data["truth"],
                outputs[name]["r150"]["gold"],
                outputs[name]["combined"]["gold"],
                2500,
                20262501 + index,
            ),
            "vs_r150_proxy": T.paired_bootstrap(
                proxy_truth,
                outputs[name]["r150"]["proxy"],
                outputs[name]["combined"]["proxy"],
                2500,
                20263001 + index,
            ),
        }

    checks = {
        "gold_nondegrading_all_surfaces": all(
            row["gold_delta_vs_a5"] >= -1e-15
            and not row["gold_negative_columns_vs_a5"]
            for row in rows.values()
        ),
        "proxy_positive_all_surfaces": all(
            row["proxy_delta_vs_a5"] > 0 for row in rows.values()
        ),
        "proxy_positive_folds_5_of_5_all_surfaces": all(
            row["proxy_positive_folds_vs_a5"] == 5
            for row in rows.values()
        ),
        "bootstrap_proxy_ci_positive_all_surfaces": all(
            result["vs_a5_proxy"]["ci95"][0] > 0
            for result in bootstrap.values()
        ),
        "combined_beats_components_in_proxy": all(
            row["proxy_delta_vs_a5"] > 0
            and row["proxy_delta_vs_r150"] > 0
            for row in rows.values()
        ),
    }
    decision = (
        "BUILD_A5EFF30_R150"
        if all(checks.values())
        else "KEEP_A5EFF30_ONLY"
    )
    payload = {
        "created_cst": pd.Timestamp.now(
            tz="Asia/Shanghai"
        ).isoformat(),
        "parent": "A5eff30-only",
        "change": "reader table x1.50, then A5 Effusion .30",
        "reader_scale": READER_SCALE,
        "a5_weight": A5_WEIGHT,
        "rows": rows,
        "bootstrap": bootstrap,
        "checks": checks,
        "decision": decision,
        "evidence_boundary": (
            "Two deployed A5 surfaces and the complete 870 fold0 proxy. "
            "R150's hidden advantage was observed on another parent; "
            "this combined migration still requires dev and scoring."
        ),
    }
    out = ROOT / "reports/a5eff30_r150_2026-10-22.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("wrote", out)
    return 0 if decision.startswith("BUILD_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
