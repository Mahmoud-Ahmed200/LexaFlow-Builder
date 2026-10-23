"""Static shape checks only; never evaluate workflow content."""

from collections import Counter
from typing import Any

LIMITATIONS = [
    "No n8n version, import, execution, behavior, expression or parameter validation.",
    "Port bounds, connection types and trigger roles require a verified catalog.",
    "Cycles are allowed; branch counts do not establish runtime complexity.",
]


def validate(value: Any, catalog: dict[str, str] | None = None) -> dict:
    result: dict = dict(
        errors=[],
        warnings=[],
        node_count=None,
        node_types={},
        node_versions=[],
        trigger_types={},
        unknown_types={},
        connection_count=0,
        branches=[],
        edges=[],
        empty_workflow=False,
        unique_ids=None,
        unique_names=None,
        disabled_count=0,
        sticky_note_count=0,
        workflow_name=None,
    )
    errors, warnings = result["errors"], result["warnings"]
    if not isinstance(value, dict):
        errors.append("root_not_object")
        return result
    result["workflow_name"] = (
        value.get("name") if isinstance(value.get("name"), str) else None
    )
    nodes = value.get("nodes")
    if not isinstance(nodes, list):
        errors.append("nodes_not_array")
        nodes = []
    else:
        result["node_count"] = len(nodes)
        result["empty_workflow"] = not nodes
        if not nodes:
            warnings.append("empty_workflow")
    names, ids, types, versions, triggers, unknown = (
        [],
        [],
        Counter(),
        Counter(),
        Counter(),
        Counter(),
    )
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"node_{i}_not_object")
            continue
        for field in ("id", "name", "type"):
            if not isinstance(node.get(field), str) or not node[field]:
                errors.append(f"node_{i}_invalid_{field}")
        if isinstance(node.get("name"), str) and node["name"]:
            names.append(node["name"])
        if isinstance(node.get("id"), str) and node["id"]:
            ids.append(node["id"])
        version = node.get("typeVersion")
        if type(version) not in (int, float) or version <= 0:
            errors.append(f"node_{i}_invalid_typeVersion")
            version = None
        position = node.get("position")
        if (
            not isinstance(position, list)
            or len(position) != 2
            or any(type(x) not in (int, float) for x in position)
        ):
            errors.append(f"node_{i}_invalid_position")
        if not isinstance(node.get("parameters"), dict):
            errors.append(f"node_{i}_invalid_parameters")
        kind = node.get("type")
        if isinstance(kind, str):
            types[kind] += 1
            versions[(kind, version)] += 1
            if catalog is not None:
                if kind not in catalog:
                    unknown[kind] += 1
                elif catalog[kind] == "trigger":
                    triggers[kind] += 1
            result["sticky_note_count"] += kind == "n8n-nodes-base.stickyNote"
        result["disabled_count"] += node.get("disabled") is True
    for field, identifiers in (("ids", ids), ("names", names)):
        duplicate = len(identifiers) != len(set(identifiers))
        complete = result["node_count"] is not None and len(identifiers) == len(nodes)
        result[f"unique_{field}"] = False if duplicate else True if complete else None
        if duplicate:
            errors.append(f"duplicate_node_{field}")
    if unknown:
        warnings.append("unknown_node_types")
    result.update(
        node_types=dict(types),
        trigger_types=dict(triggers),
        unknown_types=dict(unknown),
    )
    result["node_versions"] = [
        dict(type=k, typeVersion=v, count=c)
        for (k, v), c in sorted(versions.items(), key=lambda x: str(x[0]))
    ]
    connections = value.get("connections")
    if not isinstance(connections, dict):
        errors.append("connections_not_object")
        return result
    for source, ports in connections.items():
        if source not in names:
            errors.append("missing_connection_source")
        if not isinstance(ports, dict):
            errors.append("connection_ports_not_object")
            continue
        for port, outputs in ports.items():
            if not isinstance(outputs, list):
                errors.append("outputs_not_array")
                continue
            for output, bucket in enumerate(outputs):
                result["branches"].append(
                    dict(
                        source=source,
                        type=port,
                        output=output,
                        size=len(bucket) if isinstance(bucket, list) else None,
                    )
                )
                if bucket is None:
                    continue
                if not isinstance(bucket, list):
                    errors.append("branch_not_array_or_null")
                    continue
                for edge in bucket:
                    if (
                        not isinstance(edge, dict)
                        or not isinstance(edge.get("node"), str)
                        or not isinstance(edge.get("type"), str)
                        or type(edge.get("index")) is not int
                        or edge["index"] < 0
                    ):
                        errors.append("malformed_connection")
                        continue
                    result["connection_count"] += 1
                    result["edges"].append(
                        dict(
                            source=source,
                            source_type=port,
                            output=output,
                            destination=edge["node"],
                            destination_type=edge["type"],
                            input=edge["index"],
                        )
                    )
                    if edge["node"] not in names:
                        errors.append("missing_connection_destination")
    return result
