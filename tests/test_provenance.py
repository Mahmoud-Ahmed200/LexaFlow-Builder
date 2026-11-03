"""Tests for local-only provenance auditing."""

import json

import pytest

from builder.provenance import audit


PROVENANCE = {
    "source_id": "fixture",
    "source_url": "https://example.org/workflows",
    "source_revision": "revision-1",
    "license_name": "reviewed-local-fixture",
    "permitted_use": "local-testing",
}


def workflow():
    return {
        "name": "Example",
        "nodes": [
            {
                "id": "1",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 0],
                "parameters": {},
            }
        ],
        "connections": {},
    }


def test_audit_records_structure_hash_and_exact_duplicates(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    content = json.dumps(workflow())
    (raw / "a.json").write_text(content)
    (raw / "b.json").write_text(content)
    (raw / "broken.json").write_text("{")
    output = tmp_path / "reports"

    summary = audit(raw, output, **PROVENANCE)
    rows = [
        json.loads(line)
        for line in (output / "manifest.jsonl").read_text().splitlines()
    ]
    assert summary["files"] == 3
    assert summary["parsed"] == 2
    assert summary["rejected"] == 1
    assert summary["duplicate_files"] == 1
    assert rows[1]["duplicate_of"] == "a.json"
    assert rows[0]["quality_status"] == "review_required"
    assert rows[0]["execution_verified"] is False
    assert "nodes" not in rows[0]
    assert rows[2]["content_sha256"] is not None


def test_output_inside_input_is_rejected(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    with pytest.raises(ValueError, match="outside"):
        audit(raw, raw / "reports", **PROVENANCE)


def test_incomplete_provenance_is_rejected(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    with pytest.raises(ValueError, match="provenance"):
        audit(raw, tmp_path / "report", **(PROVENANCE | {"license_name": ""}))


def test_structural_errors_reject_workflow(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "missing_nodes.json").write_text('{"connections": {}}')
    out = tmp_path / "out"
    audit(raw, out, **PROVENANCE)
    record = json.loads((out / "manifest.jsonl").read_text().splitlines()[0])
    assert record["quality_status"] == "rejected"
    assert "nodes_not_array" in record["structural_errors"]
