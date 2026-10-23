# LexaFlow-Builder

LexaFlow is a university graduation research project exploring LLM-based generation,
testing, diagnosis, and repair of n8n automation workflows. Only **Builder** is in
scope today; Tester and Repairer are reserved packages with no implementation.

Builder will compare direct n8n JSON generation, compact intermediate representations
with deterministic compilation, and hierarchical generation. These are research
hypotheses; no approach has been shown superior by this project.

## Current scope

Milestone 1 provides a static local workflow inventory with structural validation,
original-byte duplicate detection, and reproducible reports. No collectors or generators
are implemented.
Dataset collection requires separate approval. No datasets or ML libraries are included.

## Research objectives

Builder aims to generate workflows that are syntactically valid, structurally correct,
semantically aligned with requirements, and suitable for execution. Planned work includes
dataset profiling, workflow similarity and duplicate detection, targeted collection and
normalization, future model experiments, and generation evaluation.

Evaluation will consider syntax and schema validity, node and parameter correctness,
graph structure and data flow, semantic alignment, performance across workflow
complexities, and execution success where an evaluation environment supports it.
Training and fine-tuning remain deferred until the model experimentation phase.

## Development setup

Use Python 3.11 or newer. From the repository root on Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

On Linux/macOS use `python3 -m venv .venv` and `.venv/bin/python` for the
remaining commands. Editable installation exposes `src/lexaflow` as `lexaflow`.
Runtime dependencies are currently empty. Development dependency ranges are in
`pyproject.toml`; before experiments, record exact environment versions with
`python -m pip freeze` alongside the experiment configuration and random seed.

## Repository layout

- `src/lexaflow/builder/`: dataset processing and future Builder components.
- `src/lexaflow/{tester,repairer,shared}/`: reserved modules and shared utilities.
- `configs/`: dataset, candidate node catalog, and evaluation examples.
- `data/`: raw sources, manifests, cleaned data, pairs, splits, and gold benchmark.
- `docs/`: project context, pending original research documents, decisions, experiments.
- `scripts/`, `tests/`, `notebooks/`: future commands, checks, and exploration.
- `reports/`, `artifacts/`, `infrastructure/docker/`: outputs and future infrastructure.

## Data handling and next decisions

Never modify raw data or execute workflow code or expressions while parsing. Preserve
source URLs, IDs, revisions, timestamps, hashes, licenses, and permitted-use records.
Keep original, synthetic, and human-reviewed descriptions distinguishable. Keep
related workflows in the same split and reserve an independently verified benchmark.
Data and generated outputs are ignored by Git; only empty placeholders are tracked.
The synthetic fixture in `tests/fixtures/` is intentionally tracked.

Select the target n8n version, verify source identities and licenses, review the node
catalog, and define evaluation and split policies before the next phase. YAML files
are examples only: no configuration loader or n8n compatibility validation exists yet.
The inventory checks JSON and structural shape, not n8n importability, execution
success, or behavioral correctness.

## Local inventory

```powershell
.\.venv\Scripts\python.exe -m lexaflow.builder.data.inventory --input tests/fixtures --output reports/inventory-demo --catalog configs/inventory-catalog.json
```

Outputs are `inventory.jsonl`, `summary.json`, and `report.md`. The optional JSON
role catalog configures type recognition; the default read limit is 10 MB per file.
Detailed `inventory.jsonl` reports are potentially sensitive: workflow names, node
names, paths, and connection labels can contain personal information. Review and
redact a copy before sharing; JSON output is not anonymized.
See [scope, schema, metrics, and limitations](docs/inventory.md) and the
[Milestone 1 report](docs/experiments/milestone-1.md). Existing YAML files remain
planning examples; the inventory CLI loads the JSON role catalog.

See [project overview](docs/project-overview.md), [research plan](docs/research-plan.md),
and [architecture](docs/architecture.md). Follow the root `AGENTS.md` instructions.
