# Milestone 1 — local static inventory

Implemented reader, structural validator, inventory aggregation, raw SHA-256 duplicate
strategy extension point, deterministic output writers and module CLI. No data was
downloaded, workflows executed, or models trained. No commits or pushes were made.
Existing research-plan, architecture and roadmap edits were preserved.

Baseline: 5 tests passed. Final verification on Python 3.12.10, pytest 8.4.2,
Ruff 0.17.2: initial implementation **28 tests passed**; after targeted review fixes,
**44 tests passed in 0.46s**, no warnings; Ruff lint and format checks passed
(30 Python files already formatted).
An intermediate test patched Path.open globally and caused an importlib metadata
warning; the test now isolates tool-version lookup and the warning is resolved.

Commands used (repository root, PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\python.exe -m lexaflow.builder.data.inventory --input tests/fixtures --output reports/inventory-demo --catalog configs/inventory-catalog.json
```

The synthetic CLI demonstration produced 2 scanned/parsed files, 0 structural-error
files, 1 warning file, 2 distinct byte hashes, no exact duplicate groups, node-count
distribution {1: 1, 3: 1}, 2 connections, 3 output slots (2 nonempty), and 1 unknown
custom node instance. Manual Trigger appeared twice, Set once, custom.synthetic once.
These are fixture observations, not real-dataset measurements or n8n compatibility
claims. Outputs are ignored under reports/inventory-demo.

Tests cover malformed/non-object JSON, absent nodes, empty input/workflows, broken
source/destination references, duplicate IDs/names, malformed connection levels,
nonnegative integer indices, fanout, multi-output/null branches, cycles, custom nodes,
disabled nodes, annotations, identical-byte and different-serialization cases, bounded
reads, simulated unreadable/unsafe paths and directory errors, credential/parameter
exclusion, unchanged source bytes, repeatability, and CLI output-root protection.

Full git diff --check flags pre-existing Markdown hard-break whitespace in the user's
research/architecture edits. Those documents were not rewritten. No additional runtime
dependencies were installed.

See ../inventory.md for the complete v1 contract, safety boundaries and metric
semantics. Main limits: no pinned n8n schema, import/execution/oracles, port compatibility,
expression resolution, operation configuration checks, semantic deduplication, or
concurrent hostile-filesystem isolation. JSON reports retain structural names/types
and relative paths; review these before sharing. Batch results are held in memory.

Proposed next milestone: agree on provenance/manifest requirements, select and verify
the target n8n version and operation catalog, then authorize a small local provenance
and quality review. External collection and execution require separate authorization.

## Targeted code review follow-up

Changed only structural identifier metadata, traversal-error handling, regression
tests, and related documentation. Valid nonempty duplicates are distinguished from
missing/invalid identifiers. Uniqueness is true for complete unique sets, false for
established duplicates, otherwise null. Existing required-field errors are retained.
Schema version 1 and field types remain unchanged; this deliberate semantic correction
is detailed in the inventory contract. Empty arrays remain vacuously unique.

Traversal errors with missing, external, relative-unusable, or parent-escaping
filenames now use the documented `.` unknown-location marker and preserve batch
processing without leaking exception messages or external paths. Normal relative
error paths retain their existing representation.

New regression coverage includes incomplete/invalid/duplicate identifiers,
unavailable node arrays, traversal filename fallbacks with a surviving valid file,
and sensitive structural labels retained in JSONL but excluded from Markdown.
Parameters and credentials remain excluded. **Detailed inventory JSONL reports are
potentially sensitive**: workflow names, node names, paths and connection labels can
contain personal information. They are not anonymized; review before sharing.

Full pytest and Ruff commands above were rerun. The CLI was also run with the same
synthetic inputs/catalog and `--output reports/inventory-review`. SHA-256 comparisons
against reports/inventory-demo confirmed all three output files were byte-identical.
No datasets collected, n8n started, training implemented, or Git commits made.
