"""Synthetic static-inventory cases; no workflow is executed."""

import copy
import json
from pathlib import Path

import pytest

from lexaflow.builder.data.inventory import inventory, write_outputs
from lexaflow.builder.data.validators.structure import validate


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


@pytest.mark.parametrize(
    "case,code",
    [
        ("root", "root_not_object"),
        ("missing", "nodes_not_array"),
        ("source", "missing_connection_source"),
        ("destination", "missing_connection_destination"),
        ("ids", "duplicate_node_ids"),
        ("names", "duplicate_node_names"),
        ("connections", "connections_not_object"),
        ("ports", "connection_ports_not_object"),
        ("outputs", "outputs_not_array"),
        ("branch", "branch_not_array_or_null"),
        ("edge", "malformed_connection"),
        ("index", "malformed_connection"),
        ("node", "node_0_not_object"),
        ("parameters", "node_0_invalid_parameters"),
    ],
)
def test_invalid_shapes(case: str, code: str) -> None:
    w = workflow()
    if case == "root":
        w = []
    elif case == "missing":
        del w["nodes"]
    elif case == "source":
        w["connections"]["absent"] = {}
    elif case == "destination":
        w["connections"]["N0"]["main"][0][0]["node"] = "absent"
    elif case in ("ids", "names"):
        field = "id" if case == "ids" else "name"
        w["nodes"][1][field] = w["nodes"][0][field]
    elif case == "connections":
        w["connections"] = []
    elif case == "ports":
        w["connections"]["N0"] = []
    elif case == "outputs":
        w["connections"]["N0"]["main"] = {}
    elif case == "branch":
        w["connections"]["N0"]["main"] = [42]
    elif case == "edge":
        w["connections"]["N0"]["main"] = [[{}]]
    elif case == "index":
        w["connections"]["N0"]["main"][0][0]["index"] = True
    elif case == "node":
        w["nodes"][0] = None
    else:
        w["nodes"][0]["parameters"] = []
    assert code in validate(w)["errors"]


def test_branches_cycles_and_annotations() -> None:
    w = workflow()
    edge = dict(node="N2", type="main", index=2)
    w["connections"]["N0"]["main"] += [None, [edge, copy.deepcopy(edge)]]
    w["connections"]["N2"] = {"main": [[dict(node="N0", type="main", index=0)]]}
    w["nodes"][0]["type"] = "custom.trigger"
    w["nodes"][1]["disabled"] = True
    w["nodes"][2]["type"] = "n8n-nodes-base.stickyNote"
    r = validate(w, {"n8n-nodes-base.stickyNote": "annotation"})
    assert not r["errors"]
    assert r["edges"][1]["output"] == 2 and r["edges"][1]["input"] == 2
    assert r["branches"][1]["size"] is None
    assert r["sticky_note_count"] == r["disabled_count"] == 1
    assert r["unknown_types"] == {"custom.trigger": 1, "n8n-nodes-base.set": 1}
    assert not r["trigger_types"]
    assert validate(w, {"custom.trigger": "trigger"})["trigger_types"] == {
        "custom.trigger": 1
    }


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


def test_read_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("lexaflow.builder.data.inventory.version", lambda _: "0.1.0")
    (tmp_path / "file.json").write_text("{}")

    def denied(*args, **kwargs):
        raise PermissionError()

    monkeypatch.setattr(Path, "open", denied)
    assert inventory(tmp_path)[0][0]["parsing_status"] == "read_error"


def test_linear_and_fanout() -> None:
    w = workflow()
    assert not validate(w)["errors"]
    w["connections"]["N0"]["main"][0].append(dict(node="N2", type="main", index=0))
    assert validate(w)["branches"][0]["size"] == 2


def test_discovery_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_walk(root, followlinks, onerror):
        onerror(PermissionError(13, "denied", str(root / "blocked")))
        return iter([])

    monkeypatch.setattr("lexaflow.builder.data.reader.os.walk", failing_walk)
    records, summary = inventory(tmp_path)
    assert records[0]["parsing_status"] == "directory_error"
    assert summary["files_scanned"] == 0
    assert summary["discovery_errors"] == ["blocked"]


def test_unsafe_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "file.json").write_text("{}")
    monkeypatch.setattr(Path, "is_symlink", lambda self: self.name == "file.json")
    assert inventory(tmp_path)[0][0]["parsing_status"] == "unsafe_path"


def test_numeric_overflow_is_contained(tmp_path: Path) -> None:
    (tmp_path / "overflow.json").write_text('{"nodes":[],"number":1e9999}')
    assert inventory(tmp_path)[0][0]["parsing_status"] == "invalid_json"


@pytest.mark.parametrize(
    "field,metadata", [("id", "unique_ids"), ("name", "unique_names")]
)
@pytest.mark.parametrize("invalid", [None, "", 42, "missing"])
def test_incomplete_identifiers_are_not_unique(field, metadata, invalid) -> None:
    w = workflow()
    if invalid == "missing":
        del w["nodes"][0][field]
    else:
        w["nodes"][0][field] = invalid
        w["nodes"][1][field] = invalid
    result = validate(w)
    assert result[metadata] is None
    assert f"node_0_invalid_{field}" in result["errors"]
    assert f"duplicate_node_{field}s" not in result["errors"]


@pytest.mark.parametrize(
    "field,metadata", [("id", "unique_ids"), ("name", "unique_names")]
)
def test_duplicate_identifiers_with_missing_identifier(field, metadata) -> None:
    w = workflow()
    w["nodes"][1][field] = w["nodes"][0][field]
    del w["nodes"][2][field]
    result = validate(w)
    assert result[metadata] is False
    assert f"duplicate_node_{field}s" in result["errors"]
    assert f"node_2_invalid_{field}" in result["errors"]


def test_identifier_metadata_for_unavailable_nodes() -> None:
    for w in ({"connections": {}}, {"nodes": [None], "connections": {}}):
        result = validate(w)
        assert result["unique_ids"] is None and result["unique_names"] is None
    for w in (workflow(), {"nodes": [], "connections": {}}):
        result = validate(w)
        assert result["unique_ids"] is True and result["unique_names"] is True


@pytest.mark.parametrize("location", [None, "outside", "relative", "escape"])
def test_discovery_error_without_relative_filename(tmp_path, monkeypatch, location):
    filename = {
        None: None,
        "outside": str(tmp_path.parent / "PRIVATE_OUTSIDE"),
        "relative": "PRIVATE_RELATIVE",
        "escape": str(tmp_path / ".." / "PRIVATE_ESCAPE"),
    }[location]
    (tmp_path / "valid.json").write_text(json.dumps(workflow()))

    def failing_walk(root, followlinks, onerror):
        onerror(OSError(13, "PRIVATE_ERROR", filename))
        return iter([(str(root), [], ["valid.json"])])

    monkeypatch.setattr("lexaflow.builder.data.reader.os.walk", failing_walk)
    records, summary = inventory(tmp_path)
    assert summary["files_scanned"] == summary["parsed_successfully"] == 1
    assert summary["discovery_errors"] == ["."]
    assert records[-1]["source_path"] == "."
    assert "PRIVATE" not in json.dumps(records)


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
