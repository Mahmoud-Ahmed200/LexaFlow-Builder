"""Run a local, static workflow inventory: python -m builder.inventory."""

import argparse
import json
import logging
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from builder.reader import read_files
from builder.validator import LIMITATIONS, validate


def duplicate_key(record: dict, strategy: str = "raw_sha256") -> str | None:
    """Extension point; canonical and near-duplicate strategies are not implemented."""
    if strategy != "raw_sha256":
        raise NotImplementedError(strategy)
    return record["sha256"]


def inventory(
    root: Path, max_bytes: int = 10_000_000, catalog: dict[str, str] | None = None
) -> tuple[list[dict], dict]:
    root = root.resolve()
    if not root.is_dir() or max_bytes <= 0:
        raise ValueError("Input must be a directory and max_bytes must be positive")
    records = []
    for path, digest, status, value in read_files(root, max_bytes):
        record = dict(
            schema_version=1,
            source_path=path,
            sha256=digest,
            parsing_status=status,
            metadata=None,
            provenance=dict(
                source_id=None,
                source_url=None,
                license=None,
                revision=None,
                retrieved_at=None,
                n8n_version=None,
            ),
            raw_duplicate_group=None,
            limitations=LIMITATIONS,
        )
        record.update(validate(None, catalog))
        record.update(
            validate(value, catalog)
            if status == "parsed"
            else dict(errors=[status], warnings=[])
        )
        record["validation_status"] = (
            "not_checked"
            if status != "parsed"
            else "errors"
            if record["errors"]
            else "warnings"
            if record["warnings"]
            else "structurally_valid"
        )
        records.append(record)
    groups: dict[str, list[str]] = {}
    for record in records:
        key = duplicate_key(record)
        if key:
            groups.setdefault(key, []).append(record["source_path"])
    duplicates = {k: v for k, v in sorted(groups.items()) if len(v) > 1}
    for record in records:
        if record["sha256"] in duplicates:
            record["raw_duplicate_group"] = "sha256:" + record["sha256"]
    summary = dict(
        schema_version=1,
        tool_version=version("lexaflow"),
        configuration=dict(
            max_bytes=max_bytes,
            catalog=catalog,
            target_n8n_version=None,
            duplicate_strategy="raw_sha256",
        ),
        files_scanned=sum(r["parsing_status"] != "directory_error" for r in records),
        records=len(records),
        parsed_successfully=sum(r["parsing_status"] == "parsed" for r in records),
        structural_errors=sum(
            r["parsing_status"] == "parsed" and bool(r["errors"]) for r in records
        ),
        files_with_warnings=sum(bool(r["warnings"]) for r in records),
        distinct_original_files=len(groups),
        exact_duplicate_groups=duplicates,
        unhashed_records=sum(r["sha256"] is None for r in records),
        limitations=LIMITATIONS,
    )
    for metric in ("node_types", "trigger_types", "unknown_types"):
        counts: Counter = Counter()
        for record in records:
            counts.update(record.get(metric, {}))
        summary[metric] = dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))
    summary["node_count_distribution"] = dict(
        sorted(
            Counter(
                str(r["node_count"]) for r in records if r.get("node_count") is not None
            ).items()
        )
    )
    versions: Counter = Counter()
    for record in records:
        for item in record.get("node_versions", []):
            versions[(item["type"], item["typeVersion"])] += item["count"]
    summary["node_versions"] = [
        dict(type=k, typeVersion=v, count=c)
        for (k, v), c in sorted(versions.items(), key=lambda x: str(x[0]))
    ]
    summary["connections"] = sum(r.get("connection_count", 0) for r in records)
    summary["output_slots"] = sum(len(r.get("branches", [])) for r in records)
    summary["nonempty_output_slots"] = sum(
        bool(b["size"]) for r in records for b in r.get("branches", [])
    )
    summary["fanout_slots"] = sum(
        (b["size"] or 0) > 1 for r in records for b in r.get("branches", [])
    )
    summary["discovery_errors"] = [
        r["source_path"] for r in records if r["parsing_status"] == "directory_error"
    ]
    return records, summary


def write_outputs(output: Path, records: list[dict], summary: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)

    def dump(value: object) -> str:
        return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)

    (output / "inventory.jsonl").write_text(
        "".join(dump(r) + "\n" for r in records), encoding="utf-8"
    )
    (output / "summary.json").write_text(dump(summary) + "\n", encoding="utf-8")
    # No workflow names, parameters, credentials, paths or descriptions in Markdown.
    lines = [
        "# Static workflow inventory",
        "",
        "Synthetic inputs are not benchmark evidence.",
        "",
    ]
    for key in (
        "files_scanned",
        "parsed_successfully",
        "structural_errors",
        "files_with_warnings",
        "distinct_original_files",
        "connections",
        "output_slots",
        "nonempty_output_slots",
        "fanout_slots",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines += ["", *LIMITATIONS]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-bytes", type=int, default=10_000_000)
    parser.add_argument(
        "--catalog", type=Path, help="JSON object mapping node type to role"
    )
    args = parser.parse_args()
    try:
        root, output = args.input.resolve(), args.output.resolve()
        if output.is_relative_to(root) or root.is_relative_to(output):
            raise ValueError("Output and input directories must be disjoint")
        catalog = None
        if args.catalog:
            catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
            if not isinstance(catalog, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in catalog.items()
            ):
                raise ValueError("Catalog must map node types to role strings")
        records, summary = inventory(root, args.max_bytes, catalog)
        write_outputs(output, records, summary)
    except (OSError, ValueError):
        logging.error("Inventory failed: check input, output and catalog configuration")
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
