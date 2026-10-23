"""Read synthetic JSON only; this does not validate n8n compatibility."""

import json
from pathlib import Path


def test_synthetic_fixture_is_readable() -> None:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "manual_trigger.json"
    workflow = json.loads(fixture.read_text(encoding="utf-8"))

    assert workflow["name"] == "Synthetic manual trigger"
    assert len(workflow["nodes"]) == 1
    assert workflow["nodes"][0]["type"] == "n8n-nodes-base.manualTrigger"
    assert workflow["connections"] == {}
    assert workflow["active"] is False
