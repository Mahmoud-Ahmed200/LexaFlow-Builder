"""Synthetic inventory regression tests; workflows are never executed."""

import json
from pathlib import Path

import pytest

from builder.inventory import inventory


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


def test_read_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builder.inventory.version", lambda _: "0.1.0")
    (tmp_path / "file.json").write_text("{}")

    def denied(*args, **kwargs):
        raise PermissionError()

    monkeypatch.setattr(Path, "open", denied)
    assert inventory(tmp_path)[0][0]["parsing_status"] == "read_error"


def test_discovery_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_walk(root, followlinks, onerror):
        onerror(PermissionError(13, "denied", str(root / "blocked")))
        return iter([])

    monkeypatch.setattr("builder.reader.os.walk", failing_walk)
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

    monkeypatch.setattr("builder.reader.os.walk", failing_walk)
    records, summary = inventory(tmp_path)
    assert summary["files_scanned"] == summary["parsed_successfully"] == 1
    assert summary["discovery_errors"] == ["."]
    assert records[-1]["source_path"] == "."
    assert "PRIVATE" not in json.dumps(records)
