# Milestone 1: scope and inventory contract

The target platform is n8n; the target version is **unresolved**. This milestone is
static dataset infrastructure, not an execution evaluator or training pipeline.

Proposed initial nodes: Manual Trigger, Set, HTTP Request, IF, and Sticky Note
(annotation only). `configs/nodes.yaml` remains the broader provisional catalog;
`configs/inventory-catalog.json` is the dependency-free CLI role mapping for this
milestone, including proposed control and annotation entries. Neither catalog
establishes version compatibility. Unknown types are counted and warned about, never
rejected solely for being unknown. Trigger detection uses explicit catalog roles,
not naming guesses. Without a catalog, trigger/unknown counts are unavailable (empty).

Static analysis accepts sequences, fanout, multiple outputs, multiple inputs, cycles,
and non-main connection channels. Runtime loop behavior, merge semantics, port bounds,
operations, parameter schemas, expression bindings, credentials, external services,
import, execution, IR/compiler, generation, and training remain deferred.

JSON validity means successful strict JSON decoding (nonstandard constants rejected).
Structural validity means the implemented shape and reference checks have no errors.
Importability requires acceptance by a selected n8n version. Execution success requires
a recorded controlled run without runtime failure. Behavioral correctness requires an
independent expected-behavior oracle. These are separate claims.

## Record schema v1

`inventory.jsonl` contains one object per discovered JSON file, ordered by path.
Unreadable directories additionally produce diagnostic records with status
`directory_error`, excluded from `files_scanned`; their contents cannot be enumerated.

- `schema_version`: 1; `source_path`: path relative to selected root.
- `sha256`: original-byte hash, null for inaccessible, unsafe, or oversized files.
- `parsing_status`: parsed, invalid_json, read_error, unsafe_path, too_large,
  or directory_error.
- `workflow_name`: string or null. `metadata`: null, reserved for externally reviewed
  descriptive metadata. No descriptions or arbitrary metadata are copied from input.
- `provenance`: source_id, source_url, license, revision, retrieved_at, n8n_version;
  all null until explicitly supplied by future collectors.
- `node_count`: array length or null; `node_types`: type-to-count mapping;
  `node_versions`: list of {type, typeVersion, count}. Invalid versions use null.
- `unique_ids`, `unique_names`: true only when all nodes have valid, nonempty,
  unique string identifiers; false when valid identifiers contain duplicates;
  null when identifiers/nodes are missing or invalid and no duplicate is established.
  Empty node arrays yield true; unavailable node arrays yield null. Missing/invalid
  fields retain their separate errors, and duplicates are diagnosed independently.
- `disabled_count`, `sticky_note_count`: distinct indicators, not executable-step counts.
- `trigger_types`, `unknown_types`: type frequencies under the optional role catalog.
- `connection_count`: count of well-shaped edge entries, including broken references.
- `branches`: {source, type, output, size}; preserves every slot including empty and
  null slots (size null). `edges`: {source, source_type, output, destination,
  destination_type, input}; preserves indices and channels of well-shaped edges.
- `empty_workflow`: true for an explicitly empty nodes array; warning, not proof of
  invalid import. Missing nodes and connections are errors under this inventory profile.
- `errors`, `warnings`: diagnostic codes without parameter values or exception text.
- `raw_duplicate_group`: sha256-prefixed identifier only for repeated original hashes.
- `validation_status`: not_checked, errors, warnings, structurally_valid.
- `limitations`: explicit checks not performed.

Each node is checked for nonempty string id/name/type, positive numeric typeVersion,
object parameters, and a two-number position. These are the local inventory profile,
not a frozen version-specific n8n schema. Duplicate names make references ambiguous.
No acyclicity rule is imposed. Null output buckets are allowed by n8n's interface.
Reference: [official n8n interfaces](https://github.com/n8n-io/n8n/blob/master/packages/workflow/src/interfaces.ts),
consulted during implementation; this moving reference does not pin compatibility.

## Metrics and reproducibility

`summary.json` records tool version, full effective catalog, size limit, unresolved n8n
version, and raw-hash duplicate strategy. No timestamps or absolute input paths affect
output. All three files are UTF-8 with stable ordering. All inspected nodes, including
disabled and annotation nodes, contribute to type and node counts. Parsed workflows
with structural errors still contribute inspectable data. Unparsed inputs do not.

Distinct original files counts distinct available byte hashes, not workflow semantics.
Exact duplicate groups contain only hashes seen at least twice. Differently serialized
JSON is not an exact duplicate. `duplicate_key` is the future strategy extension point;
canonical and near-duplicate strategies raise NotImplementedError.

Node-count distribution counts workflows per array length. Version distribution counts
node instances per type/version. Connections count well-shaped entries, not unique
node pairs. Output slots count branch positions, nonempty slots count those with
entries, and fanout slots count buckets with more than one entry. These are static
indicators, not path counts or execution complexity. Discovery errors and unhashed
records explicitly bound completeness.

## Safety and usage

```powershell
.\.venv\Scripts\python.exe -m lexaflow.builder.data.inventory --input tests/fixtures --output reports/inventory-demo --catalog configs/inventory-catalog.json
```

Optional `--max-bytes` defaults to 10000000. Catalog is an optional JSON object mapping
node types to roles; role `trigger` identifies triggers. Output directories must be
disjoint from input, preventing reports being rescanned or source files overwritten.
Existing output files are replaced. Inputs are never modified. Symlink files are
rejected, directory symlinks/junctions skipped, nonregular files rejected, and resolved
file paths must remain beneath the input root. Do not mutate the dataset concurrently:
portable path checks do not eliminate hostile filesystem replacement races. On Python
3.11 Windows junction detection is limited by pathlib support; resolved file checks
still enforce containment. Size bounds limit individual reads, not total batch memory.

Parameters, credentials, expressions, and arbitrary descriptions are never exported.
**Detailed `inventory.jsonl` reports are potentially sensitive.** Workflow names,
node names, paths, node types and connection labels remain structural metadata and
can contain personal information. These reports are not anonymized; restrict access
and review/redact a copy before sharing. `summary.json` can also retain paths and
node-type labels and requires review before sharing.
Markdown includes only aggregate numeric metrics and limitations.

## Reconciliation with research documents

Existing architecture/research documents and roadmap are preserved. They propose a
larger frozen operation catalog, early sandbox/import checks, benchmark authoring and
compiler work. Current user-authorized Milestone 1 deliberately precedes those steps;
no scientific result establishes the candidate IR architecture as superior. Existing
architecture links to original-named companion files/diagrams are unresolved in this
checkout. YAML configs remain planning examples; only the inventory JSON role catalog
is loaded by this CLI. Next: review inventory outputs and provenance requirements,
select n8n version and verified operation catalog, then authorize the next milestone.
Numeric values overflowing finite Python float range are reported as invalid_json;
this is a parser resource/representation limit, not a JSON syntax rule.

## Milestone 1 review compatibility clarification

Schema version remains 1; no fields or types were added or removed. Deliberate
semantic correction: incomplete identifier sets now yield null instead of misleading
true uniqueness, and repeated invalid empty identifiers no longer produce duplicate
errors. Valid duplicates still yield false, even alongside missing identifiers.
Normal workflow counts, hashes, graph data and duplicate grouping are unchanged.
Traversal errors without a usable root-relative filename use `source_path: "."`
and `discovery_errors: ["."]` as an unknown-location marker (also used for root
directory errors). No absolute external path or exception message is exported.
