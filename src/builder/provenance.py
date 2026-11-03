"""Milestone 2 local provenance and quality audit; no external collection."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from builder.reader import read_files
from builder.validator import validate

SCHEMA_VERSION = 1


def audit(
    root: Path,
    output: Path,
    *,
    source_id: str,
    source_url: str,
    source_revision: str,
    license_name: str,
    permitted_use: str,
    max_bytes: int = 10_000_000,
) -> dict:
    """Write a local, metadata-only JSONL audit; do not copy raw workflows."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("input must be a directory")
    output = output.resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError("output must be outside the raw input directory")
    if not all((source_id, source_url, source_revision, license_name, permitted_use)):
        raise ValueError("source provenance fields are required")

    records = []
    seen = {}
    timestamp = datetime.now(timezone.utc).isoformat()
    for path, digest, status, value in read_files(root, max_bytes):
        check = validate(value) if status == "parsed" else None
        errors = check["errors"] if check else []
        duplicate_of = seen.get(digest) if digest else None
        if digest and digest not in seen:
            seen[digest] = path
        quality = "rejected" if status != "parsed" or errors else "review_required"
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "relative_path": path,
                "source_id": source_id,
                "source_url": source_url,
                "source_revision": source_revision,
                "license": license_name,
                "permitted_use": permitted_use,
                "collected_at": None,
                "audited_at": timestamp,
                "content_sha256": digest,
                "parse_status": status,
                "structural_errors": errors,
                "duplicate_of": duplicate_of,
                "quality_status": quality,
                "execution_verified": False,
            }
        )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "files": len(records),
        "parsed": sum(r["parse_status"] == "parsed" for r in records),
        "rejected": sum(r["quality_status"] == "rejected" for r in records),
        "review_required": sum(r["quality_status"] == "review_required" for r in records),
        "duplicate_files": sum(r["duplicate_of"] is not None for r in records),
        "execution_verified": 0,
    }
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "manifest.jsonl"
    manifest.write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
        encoding="utf-8",
    )
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit local n8n workflow provenance")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--permitted-use", required=True)
    parser.add_argument("--max-bytes", type=int, default=10_000_000)
    args = parser.parse_args()
    summary = audit(
        args.input,
        args.output,
        source_id=args.source_id,
        source_url=args.source_url,
        source_revision=args.source_revision,
        license_name=args.license,
        permitted_use=args.permitted_use,
        max_bytes=args.max_bytes,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
