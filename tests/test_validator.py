"""Synthetic inventory regression tests; workflows are never executed."""

import copy

import pytest

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


def test_linear_and_fanout() -> None:
    w = workflow()
    assert not validate(w)["errors"]
    w["connections"]["N0"]["main"][0].append(dict(node="N2", type="main", index=0))
    assert validate(w)["branches"][0]["size"] == 2


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
