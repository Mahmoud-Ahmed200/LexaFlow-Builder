# LexaFlow

LexaFlow is a graduation research project studying LLM-based n8n workflow generation.
Only Builder is implemented. Tester and Repairer remain future research modules.
Direct JSON, IR compilation, and hierarchical generation are experimental alternatives;
no approach is assumed superior.

## Current scope

The local inventory recursively reads workflow JSON, checks structural shape and graph
references, identifies original-byte duplicates, and writes reproducible reports.
It never executes workflows or expressions. The target n8n version remains unresolved.
Dataset collection, training, import/execution testing and generation are deferred.

## Development

Use Python 3.11 or newer. From the repository root in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m ruff format --check src tests
```

On Linux/macOS create the environment with `python3 -m venv .venv` and use
`.venv/bin/python`. Reinstall editable after the package-layout migration: Python
imports now use `builder`, while the installed distribution is still named `lexaflow`.
Old `lexaflow.builder.data` imports are no longer supported. Runtime dependencies
remain empty; development dependencies are pytest and Ruff. Record exact installed
versions and experiment seeds before experiments.

## Repository layout

```text
src/builder/
  __init__.py
  reader.py
  validator.py
  inventory.py
data/raw/
configs/inventory-catalog.json
tests/
  fixtures/
  test_reader.py
  test_validator.py
  test_inventory.py
docs/
  architecture.md
  milestones.md
notebooks/dataset_exploration.ipynb
reports/
```

The root also retains `pyproject.toml`, `README.md`, `.gitignore`, `AGENTS.md` and
`.env.example`. Research plans, roadmap, inventory contract, milestone evidence and
former YAML planning examples are preserved in [milestones.md](docs/milestones.md).
The [architecture](docs/architecture.md) describes the broader candidate system;
its future components are not implemented by the inventory.

## Run an inventory

```powershell
.\.venv\Scripts\python.exe -m builder.inventory --input tests/fixtures --output reports/inventory-demo --catalog configs/inventory-catalog.json
```

Outputs: `inventory.jsonl`, `summary.json`, and `report.md`. The optional JSON catalog
maps node types to roles; unknown types warn rather than establishing incompatibility.
`--max-bytes` defaults to 10000000. Input and output directories must be disjoint.
The notebook is an unexecuted starting point for local exploration.

**Detailed JSONL reports are potentially sensitive:** workflow names, node names,
paths and connection labels can contain personal information. They are not anonymized;
review/redact a copy before sharing. Parameters and credential values are omitted.

Never modify raw data. Preserve provenance, original-byte hashes, licensing and
permitted-use information; do not infer them from workflow JSON. Do not execute
untrusted content. Keep related variants together in future dataset splits and reserve
an independently verified benchmark. JSON/structural validity does not establish
importability, execution success or behavioral correctness. Select the n8n version,
verify catalog coverage and define provenance requirements before the next milestone.
