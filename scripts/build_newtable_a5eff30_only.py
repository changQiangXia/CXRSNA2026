#!/usr/bin/env python
"""Append the audited Effusion-only A5 residual to the exact anchor."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SLUG = "rsna-knee-newtable-agree60-fsev5-22"
OUTPUT_SLUG = "rsna-knee-newtable-a5eff30-only"
SOURCE = ROOT / "kaggle_kernels" / SOURCE_SLUG
OUTPUT = ROOT / "kaggle_kernels" / OUTPUT_SLUG
CELL = ROOT / "kaggle_cells/a5_residual.py"
AUDIT = ROOT / "reports/newtable_a5eff30_only_2026-10-21.json"
EXTRA_DATASETS = (
    "intoxicatinglips/rsna-knee-a5-private-v1",
    "mattiaangeli/knee-mri-fold-weights",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("decision") != "BUILD_ANCHOR_A5_EFFUSION_30":
        raise SystemExit("A5 Effusion audit did not authorize build")
    if not all(audit.get("checks", {}).values()):
        raise SystemExit("A5 Effusion audit checks failed")

    source_meta = json.loads(
        (SOURCE / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    source_notebook = json.loads(
        (SOURCE / source_meta["code_file"]).read_text(encoding="utf-8")
    )
    if len(source_notebook["cells"]) != 20:
        raise SystemExit("unexpected anchor cell count")
    if "[a5-residual-v1]" in "\n".join(
        "".join(cell.get("source", []))
        for cell in source_notebook["cells"]
    ):
        raise SystemExit("source already contains A5 residual")

    source_cell = CELL.read_text(encoding="utf-8").rstrip() + "\n"
    old_labels = '_a5_labels = ("Medial Meniscus", "Lateral OA")'
    new_labels = '_a5_labels = ("Effusion",)'
    old_dose = (
        '_a5_dose = {\n'
        '    "Medial Meniscus": 0.08,\n'
        '    "Lateral OA": 0.08,\n'
        '}'
    )
    new_dose = '_a5_dose = {\n    "Effusion": 0.30,\n}'
    if source_cell.count(old_labels) != 1:
        raise SystemExit("A5 label tuple drifted")
    if source_cell.count(old_dose) != 1:
        raise SystemExit("A5 dose block drifted")
    source_cell = source_cell.replace(old_labels, new_labels)
    source_cell = source_cell.replace(old_dose, new_dose)
    source_cell = source_cell.replace(
        "on three weakly covered findings",
        "on Effusion",
    )
    if '"Effusion": 0.30' not in source_cell:
        raise SystemExit("Effusion dose missing after patch")
    if "_a5_column = _a5_all_labels.index(_a5_label)" not in source_cell:
        raise SystemExit("A5 label-to-column mapping is missing")

    notebook = copy.deepcopy(source_notebook)
    notebook["cells"].append(
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "frozen-anchor-a5-effusion-v1",
            "metadata": {"_kg_hide-input": True},
            "outputs": [],
            "source": source_cell.splitlines(keepends=True),
        }
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    code_file = f"{OUTPUT_SLUG}.ipynb"
    notebook_path = OUTPUT / code_file
    metadata_path = OUTPUT / "kernel-metadata.json"
    notebook_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    metadata = copy.deepcopy(source_meta)
    metadata["id"] = f"intoxicatinglips/{OUTPUT_SLUG}"
    metadata["title"] = "RSNA Knee newtable A5eff30 only"
    metadata["code_file"] = code_file
    sources = list(metadata.get("dataset_sources", []))
    for dataset in EXTRA_DATASETS:
        if dataset not in sources:
            sources.append(dataset)
    metadata["dataset_sources"] = sources
    metadata_path.write_text(
        json.dumps(metadata, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for path in SOURCE.iterdir():
        if path.name in {
            "kernel-metadata.json",
            source_meta["code_file"],
            "candidate_manifest.json",
        }:
            continue
        target = OUTPUT / path.name
        if path.is_dir():
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)

    if len(notebook["cells"]) != len(source_notebook["cells"]) + 1:
        raise SystemExit("unexpected appended-cell count")
    if notebook["cells"][:-1] != source_notebook["cells"]:
        raise SystemExit("base cells changed")
    compile(source_cell, code_file, "exec")
    if not (
        metadata["is_private"]
        and metadata["enable_gpu"]
        and not metadata["enable_internet"]
    ):
        raise SystemExit("private GPU/offline metadata invariant failed")

    original = audit["surfaces"]["original"]["weights"]["0.30"]
    mirror = audit["surfaces"]["mirror"]["weights"]["0.30"]
    manifest = {
        "id": metadata["id"],
        "title": metadata["title"],
        "notebook_sha256": sha256(notebook_path),
        "metadata_sha256": sha256(metadata_path),
        "source": f"kaggle_kernels/{SOURCE_SLUG}",
        "source_online_anchor": {
            "kernel": SOURCE_SLUG,
            "version": 2,
            "displayed_lb": "0.959",
            "online_order": (
                "ranked above double+A5 and rpure6-R150 in the same band"
            ),
        },
        "change": (
            "append one fail-open A5 residual cell; only Effusion at .30; "
            "all 20 anchor cells byte-identical"
        ),
        "a5_labels": ["Effusion"],
        "a5_weight": 0.30,
        "a5_column_mapping": "Effusion -> model output index 7",
        "evidence_vs_anchor": {
            "original_gold_delta": original["gold_delta"],
            "original_proxy_delta": original["proxy_delta"],
            "original_positive_folds": original[
                "proxy_positive_folds"
            ],
            "mirror_gold_delta": mirror["gold_delta"],
            "mirror_proxy_delta": mirror["proxy_delta"],
            "mirror_positive_folds": mirror["proxy_positive_folds"],
            "nested_heldout_both_surfaces_5_of_5": True,
        },
        "online_probe_rationale": (
            "The full reader bundle remained below the anchor online. "
            "A5 Effusion is the only added independent-family signal, so it "
            "is isolated on the anchor instead of blending the two correlated "
            "final submissions."
        ),
        "audit": "reports/newtable_a5eff30_only_2026-10-21.json",
        "static_preflight": (
            "reports/newtable_a5eff30_only_static_preflight_2026-10-21.json"
        ),
        "a5safe2_overlay": "not used",
        "risk": (
            "adds five A5 forwards; fail-open time budget and coverage gate "
            "preserve the exact anchor if unavailable or late"
        ),
        "status": "static-ready; not dev-pushed and not scored",
    }
    (OUTPUT / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
