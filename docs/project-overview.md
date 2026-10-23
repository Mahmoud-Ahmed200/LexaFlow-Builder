# LexaFlow project overview

LexaFlow is a university graduation research project investigating LLM-based
generation, testing, execution, diagnosis, and repair of n8n workflows.

Builder converts natural-language requirements into executable workflows. Tester
will investigate hierarchical tests for nodes, blocks, and complete workflows.
Repairer will investigate failure diagnosis and repair. Only Builder is currently
in scope; the other modules are reserved directories.

Builder research concerns approximately 8B–9B parameter models and compares direct
JSON generation, compact intermediate representations with deterministic compilation,
and hierarchical planning, node selection, graph construction, and configuration.
Dataset composition, structural complexity, node frequency, and training strategies
are experimental factors. No comparative results are established.

The current phase is dataset preparation, starting with a local workflow inventory.
Future inventory work includes provenance preservation, parsing, graph validation,
exact and near deduplication, sensitive-data sanitization, coverage analysis, and
instruction–workflow pairing. This scaffold does not implement those features.

Python 3.11+, pytest, Ruff, Git, and YAML/JSON form the initial toolchain. PyTorch,
Transformers, PEFT, and isolated Docker-based n8n execution are deferred. The target
n8n version remains undecided.

Raw workflows must remain unchanged and be treated as untrusted input. Parsing must
not execute embedded code or expressions. Preserve provenance and licensing records,
protect secrets and personal information, and retain semantic names and references.
JSON validity, graph validity, importability, execution, and behavioral correctness
are separate claims. Prevent related variants leaking across splits, maintain an
independently verified final benchmark, and label description origins explicitly.

Experiments must record configurations, seeds, versions, sample sizes, exclusions,
limitations, and failures. Do not fabricate findings or equate reference JSON matches
with correctness. Original research and architecture documents are still awaited.
