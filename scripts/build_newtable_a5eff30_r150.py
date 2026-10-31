#!/usr/bin/env python
"""Clone A5eff30-only and apply the audited R150 reader table."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SLUG = "rsna-knee-newtable-a5eff30-only"
OUTPUT_SLUG = "rsna-knee-newtable-a5eff30-r150"
SOURCE = ROOT / "kaggle_kernels" / SOURCE_SLUG
OUTPUT = ROOT / "kaggle_kernels" / OUTPUT_SLUG
EVIDENCE = ROOT / "reports/a5eff30_r150_2026-10-22.json"
SCALE = 1.50


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scaled_table(source: str) -> tuple[str, dict[str, float], dict[str, float]]:
    marker = "OWN_W_PER_TARGET = "
    positions = [
        index
        for index, line in enumerate(source.splitlines())
        if line.lstrip().startswith(marker)
    ]
    if len(positions) != 1:
        raise SystemExit("expected exactly one OWN_W_PER_TARGET assignment")
    line_index = positions[0]
    lines = source.splitlines(keepends=True)
    original_line = lines[line_index]
    indent = original_line[: len(original_line) - len(original_line.lstrip())]
    code, separator, comment = original_line.partition("  #")
    literal_start = code.index(marker) + len(marker)
    literal = code[literal_start:].strip()
    old = ast.literal_eval(literal)
    if not isinstance(old, dict) or len(old) != 12:
        raise SystemExit("unexpected OWN_W_PER_TARGET table")
    new = {
        label: round(float(weight) * SCALE, 12)
        for label, weight in old.items()
    }
    replacement = indent + marker + json.dumps(
        new,
        ensure_ascii=False,
        separators=(", ", ": "),
    )
    if separator:
        replacement += "  #" + comment
    else:
        replacement += "\n"
    lines[line_index] = replacement
    return "".join(lines), old, new


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if evidence.get("decision") != "BUILD_A5EFF30_R150":
        raise SystemExit("combined A5/R150 audit did not authorize build")
    if not all(evidence.get("checks", {}).values()):
        raise SystemExit("combined A5/R150 audit checks failed")
    if OUTPUT.exists():
        raise SystemExit(f"output already exists: {OUTPUT}")

    source_meta_path = SOURCE / "kernel-metadata.json"
    source_meta = json.loads(source_meta_path.read_text(encoding="utf-8"))
    source_code_path = SOURCE / source_meta["code_file"]
    source_notebook = json.loads(
        source_code_path.read_text(encoding="utf-8")
    )
    if len(source_notebook["cells"]) != 21:
        raise SystemExit("unexpected A5eff30-only cell count")

    target_index = None
    for index, cell in enumerate(source_notebook["cells"]):
        source = "".join(cell.get("source", []))
        if "OWN_W_PER_TARGET = " in source:
            target_index = index
    if target_index is None:
        raise SystemExit("reader table cell not found")

    notebook = copy.deepcopy(source_notebook)
    target = notebook["cells"][target_index]
    patched_source, old_table, new_table = scaled_table(
        "".join(target.get("source", []))
    )
    compile(patched_source, f"{OUTPUT_SLUG}.ipynb:cell-{target_index}", "exec")
    target["source"] = patched_source.splitlines(keepends=True)
    target["execution_count"] = None
    target["outputs"] = []

    changed = [
        index
        for index, (before, after) in enumerate(
            zip(source_notebook["cells"], notebook["cells"])
        )
        if before != after
    ]
    if changed != [target_index]:
        raise SystemExit(f"unexpected changed cells: {changed}")

    OUTPUT.mkdir(parents=True)
    for path in SOURCE.iterdir():
        if path.name in {
            source_meta["code_file"],
            "kernel-metadata.json",
            "candidate_manifest.json",
        }:
            continue
        target_path = OUTPUT / path.name
        if path.is_dir():
            shutil.copytree(path, target_path)
        else:
            shutil.copy2(path, target_path)

    code_file = f"{OUTPUT_SLUG}.ipynb"
    notebook_path = OUTPUT / code_file
    notebook_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    metadata = copy.deepcopy(source_meta)
    metadata["id"] = f"intoxicatinglips/{OUTPUT_SLUG}"
    metadata["title"] = "RSNA Knee newtable A5eff30 R150"
    metadata["code_file"] = code_file
    metadata_path = OUTPUT / "kernel-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if not (
        metadata["is_private"]
        and metadata["enable_gpu"]
        and not metadata["enable_internet"]
    ):
        raise SystemExit("private GPU/offline invariant failed")

    original = evidence["rows"]["original"]
    mirror = evidence["rows"]["mirror"]
    manifest = {
        "id": metadata["id"],
        "title": metadata["title"],
        "notebook_sha256": sha256(notebook_path),
        "metadata_sha256": sha256(metadata_path),
        "parent": {
            "kernel": SOURCE_SLUG,
            "version": 1,
            "online_score": 0.959,
            "online_position": "highest among our completed submissions",
            "notebook_sha256": sha256(source_code_path),
            "metadata_sha256": sha256(source_meta_path),
        },
        "change": (
            "preserve all 21 A5eff30-only cells except cell 18; "
            "multiply the twelve OWN_W_PER_TARGET reader weights by 1.50"
        ),
        "changed_cells": changed,
        "reader_scale": SCALE,
        "old_reader_weights": old_table,
        "new_reader_weights": new_table,
        "a5_residual": {
            "labels": ["Effusion"],
            "dose": 0.30,
            "cell_unchanged": True,
        },
        "evidence_vs_a5eff30": {
            "original_gold_delta": original["gold_delta_vs_a5"],
            "original_proxy_delta": original["proxy_delta_vs_a5"],
            "original_positive_folds": original[
                "proxy_positive_folds_vs_a5"
            ],
            "mirror_gold_delta": mirror["gold_delta_vs_a5"],
            "mirror_proxy_delta": mirror["proxy_delta_vs_a5"],
            "mirror_positive_folds": mirror[
                "proxy_positive_folds_vs_a5"
            ],
            "gold_negative_columns": [],
            "proxy_bootstrap_ci_positive": True,
        },
        "evidence": (
            "R150 was online-positive on another parent; combined migration "
            "is locally positive on both deployed A5 surfaces and all folds"
        ),
        "runtime": (
            "no additional model family or forward pass; same 21-cell "
            "A5eff30-only execution chain"
        ),
        "audit": "reports/a5eff30_r150_candidate_audit_2026-10-22.json",
        "local_evidence": str(EVIDENCE.relative_to(ROOT)),
        "dev_eligible": True,
        "dev_approved": False,
        "dev_pushed": False,
        "scoring_submitted": False,
        "status": "static-ready; dev approval required",
    }
    (OUTPUT / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
