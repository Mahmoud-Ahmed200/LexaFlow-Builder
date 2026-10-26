"""Synthetic inventory regression tests; workflows are never executed."""

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from builder.inventory import inventory, write_outputs
from builder.validator import validate


def workflow() -> dict:
    nodes = [
        dict(
            id=str(i),
            name=f"N{i}",
            type="n8n-nodes-base.set",
            typeVersion=1,
            parameters={},
            position=[i, 0],
        )
        for i in range(3)
    ]
    return dict(
        name="Synthetic",
        nodes=nodes,
        connections={"N0": {"main": [[dict(node="N1", type="main", index=0)]]}},
    )


def test_batch_duplicates_privacy_and_determinism(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    w = workflow()
    w["nodes"][0]["parameters"] = {"apiKey": "SECRET_SENTINEL"}
    w["nodes"][0]["credentials"] = {"service": {"name": "CREDENTIAL_SENTINEL"}}
    compact = json.dumps(w)
    for name, text in [
        ("a", compact),
        ("b", compact),
        ("c", json.dumps(w, indent=2)),
        ("d", "{bad"),
        ("e", "[]"),
        ("f", "NaN"),
    ]:
        (root / f"{name}.json").write_text(text, encoding="utf-8")
    records, summary = inventory(root)
    assert summary["files_scanned"] == 6
    assert summary["parsed_successfully"] == 4
    assert summary["distinct_original_files"] == 6 - 1
    assert len(summary["exact_duplicate_groups"]) == 1
    assert records[0]["raw_duplicate_group"] == records[1]["raw_duplicate_group"]
    assert records[2]["raw_duplicate_group"] is None
    before = (root / "a.json").read_bytes()
    out = tmp_path / "out"
    write_outputs(out, records, summary)
    first = {p.name: p.read_bytes() for p in out.iterdir()}
    write_outputs(out, *inventory(root))
    assert first == {p.name: p.read_bytes() for p in out.iterdir()}
    assert all(b"SENTINEL" not in data for data in first.values())
    assert (root / "a.json").read_bytes() == before
    assert inventory(root, max_bytes=2)[1]["unhashed_records"] > 0


def test_empty(tmp_path: Path) -> None:
    records, summary = inventory(tmp_path)
    assert records == [] and summary["files_scanned"] == 0
    assert validate({"nodes": [], "connections": {}})["warnings"] == ["empty_workflow"]


def test_detailed_report_retains_sensitive_structural_labels(tmp_path):
    root = tmp_path / "input"
    root.mkdir()
    w = workflow()
    w["name"] = "PRIVATE_WORKFLOW"
    w["nodes"][0]["name"] = "PRIVATE_NODE"
    w["connections"] = {
        "PRIVATE_NODE": {
            "PRIVATE_CHANNEL": [[dict(node="N1", type="PRIVATE_INPUT", index=0)]]
        }
    }
    w["nodes"][0]["parameters"] = {"token": "PRIVATE_SECRET"}
    w["nodes"][0]["credentials"] = {"service": "PRIVATE_CREDENTIAL"}
    (root / "PRIVATE_PATH.json").write_text(json.dumps(w))
    write_outputs(tmp_path / "out", *inventory(root))
    detailed = (tmp_path / "out" / "inventory.jsonl").read_text()
    markdown = (tmp_path / "out" / "report.md").read_text()
    for label in ("WORKFLOW", "NODE", "CHANNEL", "INPUT", "PATH"):
        assert "PRIVATE_" + label in detailed
        assert "PRIVATE_" + label not in markdown
    assert "PRIVATE_SECRET" not in detailed
    assert "PRIVATE_CREDENTIAL" not in detailed


@pytest.mark.parametrize(
    "module_name",
    ["builder", "builder.reader", "builder.validator", "builder.inventory"],
)
def test_package_import(module_name: str) -> None:
    assert importlib.import_module(module_name).__name__ == module_name


def test_synthetic_fixture_is_readable() -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "manual_trigger.json"
    workflow = json.loads(fixture.read_text(encoding="utf-8"))

    assert workflow["name"] == "Synthetic manual trigger"
    assert len(workflow["nodes"]) == 1
    assert workflow["nodes"][0]["type"] == "n8n-nodes-base.manualTrigger"
    assert workflow["connections"] == {}
    assert workflow["active"] is False


def test_cli(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "builder.inventory",
            "--input",
            "tests/fixtures",
            "--output",
            str(tmp_path / "out"),
            "--catalog",
            "configs/inventory-catalog.json",
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out" / "summary.json").is_file()
    rejected = subprocess.run(
        [
            sys.executable,
            "-m",
            "builder.inventory",
            "--input",
            str(tmp_path),
            "--output",
            str(tmp_path / "nested"),
        ],
        capture_output=True,
        check=False,
    )
    assert rejected.returncode == 2
