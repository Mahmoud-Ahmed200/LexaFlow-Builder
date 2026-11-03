# Milestone 2 — Provenance and quality audit (first increment)

This increment builds on Milestone 1's bounded JSON reader and structural validator.
It does **not** download datasets, copy workflows, normalize parameters, execute n8n,
verify a dataset license, or certify a workflow as fit for model training.

## Run locally

Install the package from the repository root:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_provenance.py
```

Run against your own reviewed local workflow files:

```bash
python -m builder.provenance \
  --input tests/fixtures \
  --output reports/provenance-demo \
  --source-id local-fixtures \
  --source-url https://example.org/local-fixtures \
  --source-revision local-demo-v1 \
  --license reviewed-local-fixture \
  --permitted-use local-testing
```

Replace these example provenance values with **verified real source metadata** for
a real dataset; do not label an unverified license or permitted use as approved.

Outputs:
- `manifest.jsonl`: one metadata-only record per discovered JSON file;
  includes SHA-256, structural errors, exact-byte duplicate reference,
  and provenance as provided by the operator.
- `summary.json`: file counts by outcome.

`review_required` means only that the JSON parsed and passed the
limited Milestone 1 structural checks. It does **not** imply that it imports
into n8n, executes, has valid parameters, or is legally safe for training.

`collected_at` is null because the original acquisition time is unknown.
`audited_at` records the time of this local audit. Operators must independently
verify the origin, revision, license and permitted use.

## Next increments

1. Verify and pin the target n8n release and supported node/operation catalog.
2. Build safe semantic normalization and secret-redaction with explicit preservation
   of expressions, branches and connections.
3. Add graph-aware deduplication, distribution profiling, and human-reviewed
   quality gates before splitting train/validation/test.

Reports can expose sensitive relative filenames, node-related validation labels,
and source identifiers. Review before sharing. Keep raw data out of commits.
