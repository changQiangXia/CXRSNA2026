"""Static audit for A5eff30-only plus the R150 reader table."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARENT_SLUG = "rsna-knee-newtable-a5eff30-only"
CANDIDATE_SLUG = "rsna-knee-newtable-a5eff30-r150"
PARENT = ROOT / "kaggle_kernels" / PARENT_SLUG
CANDIDATE = ROOT / "kaggle_kernels" / CANDIDATE_SLUG
OUT = ROOT / "reports/a5eff30_r150_candidate_audit_2026-10-22.json"
SCALE = 1.50


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(source: str) -> dict[str, float]:
    values = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith("OWN_W_PER_TARGET = "):
            continue
        literal = stripped[len("OWN_W_PER_TARGET = ") :]
        literal = literal.split("  #", 1)[0].strip()
        parsed = ast.literal_eval(literal)
        if isinstance(parsed, dict):
            values.append(parsed)
    if len(values) != 1:
        raise RuntimeError(f"expected one reader table, got {len(values)}")
    return {str(key): float(value) for key, value in values[0].items()}


def compile_cell(source: str, filename: str) -> None:
    """Compile Python cells after removing notebook-only magic lines."""
    lines = source.splitlines(keepends=True)
    while lines and lines[0].lstrip().startswith(("%", "!")):
        lines.pop(0)
    compile("".join(lines), filename, "exec")


def main() -> int:
    parent_meta = json.loads(
        (PARENT / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    candidate_meta = json.loads(
        (CANDIDATE / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    parent_nb = json.loads(
        (PARENT / parent_meta["code_file"]).read_text(encoding="utf-8")
    )
    candidate_nb = json.loads(
        (CANDIDATE / candidate_meta["code_file"]).read_text(
            encoding="utf-8"
        )
    )
    manifest = json.loads(
        (CANDIDATE / "candidate_manifest.json").read_text(encoding="utf-8")
    )

    changed = [
        index
        for index, (before, after) in enumerate(
            zip(parent_nb["cells"], candidate_nb["cells"])
        )
        if before != after
    ]
    parent_table = table(
        "".join(parent_nb["cells"][18].get("source", []))
    )
    candidate_table = table(
        "".join(candidate_nb["cells"][18].get("source", []))
    )
    expected = {
        key: round(value * SCALE, 12)
        for key, value in parent_table.items()
    }

    source_checks = {}
    for index, cell in enumerate(candidate_nb["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        try:
            compile_cell(
                source,
                f"{candidate_meta['code_file']}:cell-{index}",
            )
            source_checks[index] = "PASS"
        except SyntaxError as exc:
            source_checks[index] = f"FAIL {exc}"

    parent_notebook_sha = sha256(PARENT / parent_meta["code_file"])
    parent_metadata_sha = sha256(PARENT / "kernel-metadata.json")
    a5_cell = "".join(candidate_nb["cells"][-1].get("source", []))
    checks = {
        "parent_and_candidate_have_21_cells": (
            len(parent_nb["cells"]) == 21
            and len(candidate_nb["cells"]) == 21
        ),
        "only_reader_cell_changed": changed == [18],
        "reader_table_has_12_unique_labels": (
            len(parent_table) == 12 and len(candidate_table) == 12
        ),
        "reader_table_is_exact_1p50_scale": candidate_table == expected,
        "own_weight_fallback_unchanged": (
            "OWN_W = 0.15"
            in "".join(candidate_nb["cells"][18].get("source", []))
        ),
        "a5_effusion_cell_unchanged": (
            candidate_nb["cells"][-1] == parent_nb["cells"][-1]
        ),
        "a5_effusion_30_present": (
            '"Effusion": 0.30' in a5_cell
            and "_a5_labels = (\"Effusion\",)" in a5_cell
        ),
        "metadata_id_correct": (
            candidate_meta.get("id")
            == f"intoxicatinglips/{CANDIDATE_SLUG}"
        ),
        "metadata_title_correct": (
            candidate_meta.get("title")
            == "RSNA Knee newtable A5eff30 R150"
        ),
        "metadata_private_gpu_offline": (
            bool(candidate_meta.get("is_private"))
            and bool(candidate_meta.get("enable_gpu"))
            and not bool(candidate_meta.get("enable_internet"))
        ),
        "competition_mount_unchanged": (
            candidate_meta.get("competition_sources")
            == parent_meta.get("competition_sources")
        ),
        "dataset_mounts_unchanged": (
            candidate_meta.get("dataset_sources")
            == parent_meta.get("dataset_sources")
        ),
        "a5_private_dataset_mounted": (
            "intoxicatinglips/rsna-knee-a5-private-v1"
            in candidate_meta.get("dataset_sources", [])
        ),
        "all_code_cells_compile": all(
            value == "PASS" for value in source_checks.values()
        ),
        "module_sources_empty": (
            not candidate_meta.get("kernel_sources")
            and not candidate_meta.get("model_sources")
        ),
        "parent_notebook_hash_pinned": (
            manifest["parent"]["notebook_sha256"]
            == parent_notebook_sha
        ),
        "parent_metadata_hash_pinned": (
            manifest["parent"]["metadata_sha256"]
            == parent_metadata_sha
        ),
        "candidate_notebook_hash_pinned": (
            manifest["notebook_sha256"]
            == sha256(CANDIDATE / candidate_meta["code_file"])
        ),
        "candidate_metadata_hash_pinned": (
            manifest["metadata_sha256"]
            == sha256(CANDIDATE / "kernel-metadata.json")
        ),
        "dev_state_consistent": (
            manifest.get("dev_eligible") is True
            and manifest.get("dev_approved") is True
            and manifest.get("dev_pushed") is True
            and int(manifest.get("dev_push", {}).get("version", 0)) >= 1
        ),
        "scoring_state_consistent": (
            (
                manifest.get("scoring_submitted") is False
                and manifest.get("scoring_submission") is None
            )
            or (
                manifest.get("scoring_submitted") is True
                and manifest.get("scoring_submission", {}).get("status")
                in {"PENDING", "COMPLETE"}
                and int(
                    manifest.get("scoring_submission", {}).get(
                        "kernel_version", 0
                    )
                )
                == int(manifest.get("dev_push", {}).get("version", -1))
            )
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "candidate": f"intoxicatinglips/{CANDIDATE_SLUG}",
        "status": status,
        "checks": checks,
        "changed_cells": changed,
        "parent_reader_weights": parent_table,
        "candidate_reader_weights": candidate_table,
        "code_cell_compile": source_checks,
        "hashes": {
            "parent_notebook_sha256": parent_notebook_sha,
            "parent_metadata_sha256": parent_metadata_sha,
            "candidate_notebook_sha256": sha256(
                CANDIDATE / candidate_meta["code_file"]
            ),
            "candidate_metadata_sha256": sha256(
                CANDIDATE / "kernel-metadata.json"
            ),
        },
        "evidence_boundary": (
            "Static audit only; no dev execution or hidden score is implied."
        ),
    }
    OUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
