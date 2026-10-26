# LexaFlow milestones and research roadmap

Repository layout updated on 26 October 2026 at user request. The public Python package is now `builder`; the distribution name remains `lexaflow`. Reinstall editable packages after migrating. The old `lexaflow.builder.data` import and CLI paths are no longer supported. Inventory schema and algorithms are unchanged. Historical plans below remain research proposals, not findings.


---

## Project overview

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


---

## Research plan

# LexaFlow Builder Module
## Research and Implementation Plan: Natural Language to Executable Visual Workflows

**Version:** 1.0 (research blueprint, not a final architecture commitment)  
**Prepared:** 23 October 2026  
**Project:** LexaFlow, FCIS ASU graduation project 2026–2027  
**Primary module:** Workflow Builder  
**Model target:** one open-weight language model in the 8B–9B class, initially evaluated before fine-tuning  
**Execution platform:** pinned, self-hosted n8n; n8n is the *experimental backend*, not the scientific problem  
**Working compute assumption:** approximately US$10/month for a Colab Pro subscription, *subject to actual regional checkout prices, compute-unit balance, runtime availability, and GPU allocation*. Neither a particular GPU nor a number of training hours is guaranteed.

> **Status legend:** **[ESTABLISHED]** = supported by prior work or official documentation; **[HYPOTHESIS]** = testable claim proposed for LexaFlow; **[DESIGN]** = recommended implementation choice; **[OPEN]** = decision to resolve through experiments or reconnaissance. See the source notes and links at the end.

---

## Executive summary

### What the project does

A user writes a requirement such as:

> "When a new order arrives, check its total. If it exceeds $500, notify the sales team. Otherwise, record the order in a sheet."

The Builder interprets the requirement, identifies supported trigger/action/condition operations, constructs an explicit connected workflow graph, supplies valid operation arguments and data bindings, compiles it into an n8n-compatible artifact, and arranges a readable visual layout. It delivers **an importable workflow draft plus honest setup/validation diagnostics**, not an unsupported promise that unknown credentials or external APIs are ready.

### Scientific aim

**Study how generation representation, explicit node knowledge, hierarchical supervision, and training-data distribution affect the functional correctness and generalization of small language models synthesizing executable automation workflows.**

**Core experimental question:** *For an 8B–9B model under a fixed resource budget, which generation strategy produces the highest reliably verified workflow success, and why?*

This is **not** research novelty merely because a model outputs n8n JSON, uses RAG, employs multiple agents, or fine-tunes Llama/Qwen. Those ideas have substantial prior work. The contribution must be an **empirically supported finding, a reproducible method/representation with a demonstrable advantage, a carefully verified benchmark, or a combination of these**.

### Proposed route, not yet a conclusion

1. Build a **pinned n8n execution and evaluation harness** before model training.
2. Collect and audit a **versioned workflow-and-node knowledge base**.
3. Establish **zero-shot/few-shot direct-JSON baselines**.
4. Prototype a **compact typed intermediate representation (IR) and deterministic compiler**; optionally compare official n8n SDK-generated TypeScript as a third target.
5. Compare **one-stage vs. hierarchical generation**, and **no retrieval vs. operation-documentation retrieval**.
6. Fine-tune the selected 8B–9B model by **resource-aware QLoRA**, only if the untuned experiments justify it.
7. Investigate **natural-distribution vs. targeted/stratified data augmentation**, using untouched held-out tasks.
8. Add bounded validation-guided regeneration, then complete **cost-, validity-, semantics-, and execution-aware ablations**.

**Go/no-go principle:** an approach is retained only if its measurable value justifies its cost and additional complexity.

---

# 1. Scope, boundaries, and vocabulary

## 1.1 In scope

- Explicit automation workflows represented as nodes, typed operations, edges, conditions, data mappings, and bounded/iterative control flow.
- Natural language → plan/graph/configuration → n8n workflow JSON, directly or via an IR or SDK code.
- Version-specific node selection and operation/parameter grounding.
- Importability, static validation, bounded sandbox execution, and requirement satisfaction.
- Readable node layout, labels, and optional explanatory sticky notes.
- Small open-weight model inference and parameter-efficient fine-tuning.
- Controlled research comparisons and failure analysis.

## 1.2 Out of scope for Builder v1

- Arbitrary autonomous agents deciding their next tool at runtime (although a workflow may contain a predefined AI node).
- Perfect support for every n8n/community node and every external application.
- Obtaining real user credentials, silently activating workflows, or making live irreversible changes.
- Proving generalization to Zapier/Node-RED/BPMN without experiments on those platforms.
- A production-grade security/compliance certification.
- Unbounded self-repair, reinforcement learning, or multi-agent orchestration as baseline requirements.
- The separate LexaFlow hierarchical testing and fault-repair modules; Builder exposes contracts they can later use, but does not claim those components have been implemented.

## 1.3 Correctness ladder (never collapse these outcomes)

| Layer | Test question | Pass criterion |
|---|---|---|
| 1. Output syntax | Is model output parseable? | Strict IR or JSON parser succeeds. |
| 2. Graph validity | Are identifiers, ports, edges, and branches valid? | Typed structural checker passes. |
| 3. Node/parameter validity | Do nodes and operations exist at pinned versions, with required configuration? | Catalog-backed checks pass; unresolved environment-dependent fields are reported. |
| 4. n8n importability | Does the actual pinned platform accept the workflow? | Import/create succeeds without unsupported nodes or invalid structure. |
| 5. Runtime executability | Does it run given valid fixture inputs and allowed mocks? | No unexpected engine-level failure. |
| 6. Requirement satisfaction | Are independently specified outputs/side effects correct? | Scenario-specific oracle assertions pass. |
| 7. Deployment readiness | Are credentials, real resources, and human approvals configured? | Explicit readiness review; never inferred from a mocked run. |

A visually attractive workflow is not necessarily executable; an executable workflow is not necessarily semantically correct.

## 1.4 Target difficulty bands

**Band A — basic (first prototype):** Manual/Webhook/Schedule trigger; HTTP request; simple transformation; one action; 2–5 nodes.  
**Band B — intermediate (main experiment):** Conditions, true/false branches, multiple side effects, structured field mapping; roughly 4–10 nodes.  
**Band C — challenging (held-out/stress):** More nodes, merges, loops, more nested conditions, API failure behaviors, unusual node combinations; size chosen after profiling.  

Node-count ranges are provisional experimental strata, **not** claims about the difficulty of all workflows. Prefer complexity annotations (depth, branches, data dependencies, loop constructs, distinct operations) over node count alone.

---

# 2. Literature-grounded rationale and what is *not* novel

| Work | Established contribution | LexaFlow implication / unresolved issue |
|---|---|---|
| **WorkTeam** (Liu et al., NAACL Industry 2025; local file `2025.naacl-industry.3.pdf`) | Supervisor/orchestrator/parameter-filler role specialization for NL→workflow generation; 3,695 examples. | Do not assert that multi-stage/multi-agent design is unprecedented. Compare a staged single model with simpler alternatives. |
| **WorkflowLLM** (Fan et al., 2024; `2411.05451v1.pdf`) | WorkflowBench ~106,763 samples; Llama-3.1-8B fine-tuning for orchestration across many APIs. | SFT of an 8B model is established. Its gains do not directly prove n8n execution success. |
| **WorfBench/WorfEval** (Qiao et al., ICLR 2025; `2410.07869v3.pdf`) | Workflow graph benchmark; subsequence/subgraph evaluation. | Structural fidelity deserves measurement, but is not equivalent to functional correctness. |
| **Flow-Bench/Flow-Gen** (Duesterwald et al., EMNLP Industry 2025; `2025.emnlp-industry.100.pdf`) | Converts requirements through Python IR before BPMN; includes incremental edits. | Intermediate representations are prior art. A LexaFlow IR must be justified experimentally for this task. |
| **ComfyFlow** (Xu et al., Findings ACL 2026; `2026.findings-acl.140.pdf`) | Fine-grained format, node, graph and parameter metrics; SFT/RL experiments on ComfyUI. | Use multi-level diagnostics; its ComfyUI results are not n8n results. |
| **Knowledge-Centric Agents for Workflow Generation in ComfyUI** (Li et al., 2026; `2607.15845v2.pdf`) | Workflow knowledge inversion, strategy → skeleton → configuration, hierarchical training. | A strong staged-generation prior; test transfer rather than assume superiority. |
| **Chat2Workflow** (Zhong et al., 2026; external) | Executable visual workflows and feedback-driven generation for Dify/Coze. | End-to-end generation plus correction alone is not a novel claim. |
| **n8n Workflow SDK** (official project) | Programmatic TypeScript construction, flow control and validation. | Check whether SDK code is a competitive output representation; lock SDK and n8n versions. |  

**Evidence boundary:** the papers above do not demonstrate that an IR+RAG+QLoRA system is optimal for n8n. That combination is a **candidate whose value must be tested**. The academic deliverable is strengthened by negative findings when faithfully measured.

---

# 3. Scientific research design

## 3.1 Research questions and falsifiable hypotheses

| ID | Research question | Working hypothesis | Main comparison | Falsifying evidence |
|---|---|---|---|---|
| **RQ1: Representation** | How does model output representation affect executable workflow synthesis? | **H1 [HYPOTHESIS]:** compact typed IR + deterministic compiler improves import and task success vs direct full JSON for a matched 8B–9B backbone. | Direct n8n JSON vs IR→compiler; optional SDK code. | No material gain or worse task success at comparable latency/compute. |
| **RQ2: Grounding** | Does version-matched external node knowledge reduce component/parameter errors? | **H2:** retrieval of correct operation schemas improves rare/unseen operation performance. | No RAG vs catalog RAG vs catalog+retrieved examples. | More invalid operations, no gain, or retrieval-related regressions. |
| **RQ3: Training data** | How do graph-pattern/operation coverage and augmentation affect generalization? | **H3:** targeted verified examples outperform an equal-count random augmentation on underrepresented patterns, without unacceptable regressions. | Natural, random-augmented, stratified, targeted-augmented. | Equal or worse out-of-distribution performance or large in-distribution degradation. |
| **RQ4: Staging** | Is hierarchical generation beneficial after accounting for extra model calls? | **H4:** plan→graph→parameters improves complex task success. | Single-pass IR vs two/three-stage IR using same backbone. | No better task success, excessive cascading mistakes or latency. |
| **RQ5: Validation feedback** | Does bounded error-conditioned regeneration improve first-attempt outputs? | **H5:** local structured diagnostics increase valid/functional output. | 0 vs 1 vs 2 correction rounds; full vs local revision (if implemented). | Corrections do not raise semantic success or introduce changes outside target. |

**Primary outcome:** *end-to-end task success on independent executable fixtures* (per-scenario oracle).  
**Secondary outcomes:** n8n import success, operation choice, parameter validity, graph fidelity, hallucination frequency, latency, token use, compute spend, and visual-quality measures.  
**Experimental unit:** an independently authored requirement with an environment fixture and checked expected behavior (not merely an existing JSON template).

## 3.2 Research novelty candidates: conditional, not promised

1. A **reproducible n8n execution-grounded benchmark** with version-pinned operations, specification-backed expected outputs, and compositional/rare-operation splits. Novelty requires checking existing benchmarks and showing new coverage/quality, not naming a new dataset.
2. A **typed workflow IR and compiler** whose advantage is demonstrated by controlled representation comparisons, not just by its implementation.
3. A **data-coverage intervention** with experimentally quantified effects on error categories and generalization.
4. A **cost–correctness frontier** for alternative small-model workflow generation strategies under a constrained compute budget.
5. A **mechanistic error taxonomy** linking failure modes to planning, operation selection, connection/data binding, parameter configuration, platform serialization, and runtime semantics.

An incremental combination of known techniques with no identified gain is likely an **engineering contribution**, not independently strong scientific novelty. The team should be prepared to narrow to the strongest one or two findings.

## 3.3 Fairness controls

- Reuse a **single frozen test set** for final comparison; tune only on development data.
- Match base checkpoints when attributing improvements to architecture. Compare model families only as a separate variable.
- Record prompts, seeds (where supported), temperature, decoding limits, candidate catalog, retrieval top-k, inference budget, correction count and model context.
- Match amount of training data and update budget for data-distribution comparisons; report deviations and GPU time.
- Separate *first-pass* score from *after-feedback* score.
- Avoid artificially favoring IR: both direct JSON and IR outputs should get the same *platform-level* validators and the same oracle. If the IR compiler provides stronger deterministic assistance, state that plainly and measure its engineering cost.
- Report failures and per-category sample counts, not only aggregate success rates.
- Bootstrap confidence intervals over **task-level** successes; use paired comparisons by evaluating systems on exactly the same tasks.

---

# 4. Workstream A: scope and execution infrastructure **before training**

### A1. Pin the toolchain

- Record the precise self-hosted n8n version and image digest; freeze installed community nodes.
- Record compatible versions of `@n8n/workflow-sdk`, Python, Node.js, JSON Schema library, CUDA/driver, Transformers, TRL, PEFT, and bitsandbytes.
- Prefer self-hosted Docker for test isolation, not a production account. Store a reusable compose/configuration file and environment-variable template with **no real secrets**.
- Research question dependency: *Without a pinned environment, performance changes may reflect platform drift rather than model changes.*

**Acceptance check:** import and execute at least five hand-built fixtures across the supported control-flow patterns; capture stable outputs and engine errors.

### A2. Define the supported operation subset

- Choose a small purposeful starting catalog (e.g., Manual Trigger, Webhook, Schedule, HTTP Request, Edit Fields, If, Switch, Merge, Google Sheets, Slack), selecting exact supported operations and versions.
- Catalog available ports, parameter dependencies, expression syntaxes, credentials, and known sandbox limitations.
- Build coverage levels A/B/C (Section 1.4). Use an explicit `unsupported_operation` response rather than inventing capabilities.

**Acceptance check:** each supported operation has a minimal valid example and at least one generated validation error fixture.

### A3. Build a sandbox execution harness

- Provide a pristine n8n instance/test database; load fixtures; import workflow; trigger via supported interface or CLI; collect logs, per-node execution metadata, and final test-observable state; clean up.
- Replace live services with controllable fixtures (HTTP mock server, dummy inbox/sheet/database) and verify actual side effects via server state.
- Distinguish configuration prerequisites from model mistakes. A missing OAuth credential is an unresolved deployment dependency, not proof of an incorrect graph.
- Never enable production triggers, send live messages, or call unknown external URLs as part of generated workflow evaluation.

**Acceptance check:** repeat a known workflow three times from the same starting state and obtain the same oracle result; record any nondeterminism.

---

# 5. Workstream B: dataset and node knowledge

## B1. Collection and provenance

Potential sources: official n8n template catalog, permissively reusable community exports, hand-written seed workflows, published workflow datasets, and adjacent work (Flow-Bench/WorkflowBench) for **methodological comparison**, not unexamined direct target mixing.

**Record per workflow:** source URL/license, fetch timestamp, source version, JSON hash, title, author-provided description, node types/versions, control-flow features, dependencies, and reason for exclusion if filtered. **Verify licenses and redistribution rights; public visibility is not blanket reuse permission.**

## B2. Cleaning and canonicalization

1. Parse JSON; preserve original separately.
2. Remove or redact sensitive fields, credential references, tokens, user-specific endpoints, personal data and sample execution records; ensure sanitation does not corrupt semantic labels.
3. Validate node existence and type version against the frozen catalog.
4. Resolve all node references and connection endpoints.
5. Normalize non-semantic IDs/positions/naming for comparison, **without deleting semantic conditions, expressions or branch labels**.
6. Calculate exact hashes and **graph-aware near-duplicate clusters**; review semantic equivalence before merging.
7. Identify non-executable/incomplete templates and tag them rather than pretending they passed execution.
8. Produce an audit CSV with input/output counts and exclusion reasons.

**Data hygiene hazard:** two structurally identical workflows with different thresholds or data mappings may have different behavior. Never deduplicate solely by unlabeled topology.

## B3. Data profiling and bias/coverage diagnosis

Produce distribution charts and counts for node types, individual operations, length/depth, branch count, loop presence, edge/port types, API diversity, expression complexity, common motifs, missing documentation and description length. Inspect long-tail operation frequency and conditional performance by stratum.

**Report:** coverage plots, rare-pattern examples, candidate sampling strategies, and *what observed failure* each proposed augmentation is intended to address.

## B4. Requirement annotation

Use four provenance classes:

- **GOLD-HUMAN:** independently written/checked requirement and expected behavior.
- **SILVER-REVIEWED:** LLM-drafted requirement aligned with original workflow, human-checked.
- **SYNTHETIC-CHECKED:** generated requirement and corresponding workflow validated by deterministic checks / approved fixture.
- **WEAK:** raw template title/description; not eligible as sole test-set ground truth.

Annotate trigger, source data contract, conditions, transformations, actions, exception behavior, unknown/missing details, and expected external side effects. Review samples twice when possible and adjudicate disagreement.

**Avoid reverse-description leakage:** a model-written paraphrase of training JSON can create unrealistic pairs. Maintain a genuinely independently authored test portion.

## B5. Dataset variants

- **D-JSON:** `(requirement, allowable catalog context) → n8n JSON`.
- **D-IR:** `(requirement, allowable catalog context) → compact typed IR`.
- **D-STAGED:** plan examples, graph examples, parameter-fill examples; associate all with the same underlying workflow ID.
- **D-CORRECTION:** invalid output + validator report → verified localized correction (optional, later).

Do not create synthetic explanations that contain unverified assumptions and then treat them as authoritative.

## B6. Splits and leakage control

Use grouped splitting by duplicate/near-duplicate graph families, task templates, semantic intent, and closely related API patterns. Hold out:

1. **IID paraphrase tasks:** seen concepts in new instructions.
2. **Unseen composition:** seen node types in unseen *combinations*.
3. **Rare-operation tasks:** limited-frequency operations.
4. **Structural OOD:** longer/deeper graphs or novel motifs.
5. **Optional version shift:** operation/node versions only if ground truth is truly available.

Final testing must be **unseen throughout prompt tuning, augmentation, and model selection**.

---

# 6. Workstream C: representation and compiler

## C1. Explore three output targets

**Target J — n8n JSON:** full platform export with node specs, connections and parameters.  
**Target I — typed IR:** compact platform-aware operation graph with symbolic typed bindings.  
**Target S — n8n SDK TypeScript:** generate SDK code and compile/validate using pinned `@n8n/workflow-sdk`; first prove feature completeness for the supported subset and sandbox any generated code.

**Do not execute arbitrary SDK TypeScript without isolation and explicit constraints.** Generated code is executable code, not harmless serialization. If sandboxing is too expensive, keep SDK comparison restricted to safe syntax or omit it.

## C2. Example candidate typed IR (DESIGN, not an n8n schema)

```json
{
  "ir_version": "0.1",
  "name": "High value order notice",
  "assumptions": [],
  "unresolved": ["slack.destination", "auth.order_source"],
  "nodes": [
    {"id":"n1","op":"trigger.webhook","args":{"path":"orders"}},
    {"id":"n2","op":"control.if","args":{
      "left":{"bind":{"node":"n1","path":"order.total","type":"number"}},
      "operator":"gt","right":500}},
    {"id":"n3","op":"slack.send_message","args":{
      "destination":{"placeholder":"slack.destination"},
      "message":"High-value order received"}}
  ],
  "edges": [
    {"from":"n1","output":"main","to":"n2","input":"main"},
    {"from":"n2","output":"true","to":"n3","input":"main"}
  ]
}
```

The IR must represent: node **operation identity**, version constraints, typed input/output ports, control-flow branches, symbolic data bindings, unresolved environment-dependent fields, human-approved assumptions, source traceability, and loop semantics. **Do not impose acyclicity** on real workflows that use loops.

**IR design tests:** can every supported seed workflow be represented without information loss? Can compiled output round-trip through n8n while preserving behavior? If not, revise the IR or explicitly narrow coverage.

## C3. Deterministic compiler steps

1. Validate IR against JSON Schema and semantic invariants.
2. Resolve each canonical `op` to installed node type and operation and select a pinned compatible node version.
3. Check args against *operation-conditional* required/optional fields and allowed values.
4. Resolve typed symbolic bindings to actual n8n expressions, with correct execution-path and item semantics.
5. Assign unique IDs and collision-free node names; preserve semantic references.
6. Map typed output ports to correct n8n connection indices, including true/false and multi-output nodes.
7. Serialize platform JSON (or code→JSON for SDK path).
8. Apply deterministic graph layout and optional section annotations.
9. Run import/platform validation. Produce **typed diagnostics**, not only `true/false`.

A compiler can guarantee some classes of structural validity, but **cannot prove user-intent satisfaction** without a specification/oracle. Node schemas may be conditional or populated dynamically through external APIs.

## C4. Layout as a separate pass

- Evaluate Dagre/ELK layered layout (respecting loops, branches and convergence).
- Deterministic coordinates, consistent direction, branch spacing, stable node names, optional group notes.
- Never let layout failures alter graph semantics.
- Evaluate overlaps, edge crossings, alignment, readability, and human review.

---

# 7. Workstream D: baseline generation and model selection

## D1. Mandatory baselines

| ID | Generator | Why it matters |
|---|---|---|
| **B0** | Base 8B–9B, zero-shot → direct n8n JSON | Minimal baseline. |
| **B1** | Base 8B–9B, few-shot → direct JSON | Controls for examples without training. |
| **B2** | Base 8B–9B + node-catalog RAG → direct JSON | Controls for fresh node knowledge. |
| **B3** | Base 8B–9B → IR → deterministic compiler | Tests representation without fine-tuning. |
| **B4** | Base 8B–9B + RAG → IR → compiler | Tests combined grounding/representation. |
| **B5 optional** | Base 8B–9B → constrained SDK code → SDK validation/JSON | Tests programmatic code as representation. |

**Model families for preliminary selection:** Qwen3-8B, Qwen3.5-9B, with Llama-3.1-8B-Instruct a literature-connected comparator. Use model licenses, actual Colab fit, supported quantization, and empirical task performance to select the backbone. *Do not assume the newest model wins at this workload.*

## D2. Baseline workflow

- Assemble ~30–50 *development* tasks (not the frozen final test set).
- Freeze input contexts and permissible operations.
- Measure first-pass quality, invalid-output classes and token/latency requirements.
- Pilot schema-constrained decoding when supported; it enforces formatting, **not semantics**.
- Compare against available published n8n generators when they can be reproduced fairly; if closed tools are used, treat them as **product context**, not necessarily reproducible research baselines.

**Decision checkpoint:** prioritize the output representation with the strongest execution signal *relative to its complexity and inference cost*, not simply maximum JSON validity.

---

# 8. Workstream E: grounding and staged generation

## E1. Catalog retrieval

- Build an operation-level index with canonical operation ID, description, parameter schema, required credentials, output contract and supported versions.
- Index validated examples separately from authoritative operation schemas.
- Use lexical/metadata filtering first; semantic retrieval/reranking second; bound context length and record retrieved IDs/scores.
- Train and test retrieval independently: **Recall@k of required operations**, unsupported-operation rate, and context contamination.
- Test `no retrieval`, `operation-doc retrieval`, `operation-doc + similar-example retrieval` on identical requirements.
- If a retrieval result conflicts with installed node metadata, trust the pinned local installation.

## E2. Single-stage vs hierarchical inference

**Single-stage:** requirement + candidates → complete IR.  
**Two-stage:** requirement → semantic plan; plan + catalog → full IR.  
**Three-stage:** requirement → plan; plan → graph; graph + schemas → parameter bindings.  

Use **one model** for all stages initially. Multi-agent role specialization is a separate experiment, not a default dependency.

**Stage-level evaluation:** plan requirement recall, correct operation set, graph edge/branch accuracy, parameter/binding correctness, final execution success, number of calls, latency and total tokens.

**Early-rejection policy:** if the plan misses a required branch or invents an unsupported step, do not assume the compiler can repair intent. Flag it early.

---

# 9. Workstream F: Colab Pro–aware model training

## F1. First verify available hardware; never budget by imagined GPU-hours

Official Colab documentation states that **GPU types, availability, session duration and resource limits vary, including on paid plans**. The current public signup page does not allow independent confirmation of a fixed regional US$10 price without checkout. Treat $10/month as the **user's planning cap**; confirm regional currency, tax, and included compute units in the actual account before paying.

**Every Colab training session should begin with:**

```bash
nvidia-smi
python - <<'PY'
import torch
print('CUDA:', torch.cuda.is_available())
if torch.cuda.is_available():
    p=torch.cuda.get_device_properties(0)
    print('GPU:', p.name, 'VRAM GiB:', round(p.total_memory / 2**30, 2))
PY
```

Record detected GPU, VRAM, start/end timestamps, training examples/tokens, effective batch size and observed Colab compute-unit consumption. **Do not use a premium GPU while only doing preprocessing or plotting.**

## F2. Resource-dependent plan

| Assigned resource (illustrative, not guaranteed) | Training strategy |
|---|---|
| **T4-class ~16 GB VRAM** | Start with 4-bit inference; 8B–9B QLoRA only after a 10-step memory smoke test. Short sequences, microbatch 1, gradient accumulation/checkpointing, small LoRA rank; CPU offload only if verified. It may be too slow or OOM for the desired run. |
| **L4-class ~24 GB** | Better candidate for controlled 8B–9B QLoRA; still check model architecture, prompt length and optimizer overhead. |
| **A100-class larger VRAM** | Longer contexts/higher throughput possible, but often costlier in compute units. Reserve for experiments needing it. |
| **No usable GPU / exhausted units** | Continue CPU-bound annotation, catalog/compiler/evaluation work; postpone training. Do **not** infer failure of the research approach from unavailable compute. |

Model architecture compatibility matters: Qwen3.5-9B uses a hybrid attention architecture, so confirm supported Transformers/PEFT/bitsandbytes versions and training adapter targets before promising QLoRA.

## F3. Colab operational checklist

1. Put durable data, split manifests, configs, logs, and adapter checkpoints in persistent Drive or versioned object storage; do not rely on `/content` surviving disconnection.
2. Commit the notebook and training scripts to version control; pin package versions and checkpoint revision IDs.
3. Start with 100–200 verified training examples to test loss masking, save/resume and evaluation.
4. Quantize backbone to 4-bit NF4 where supported; train low-rank adapters through PEFT/TRL.
5. Initial **search candidates**: LoRA rank `{8,16,32}`, alpha `{16,32,64}`, learning rate `{1e-4,2e-4}`, dropout `0–0.05`, 1–3 epochs. These are tunable starting points, not established optimal settings.
6. Use microbatch 1 and accumulation when needed; enable checkpointing and length bucketing; derive max sequence length from token histograms.
7. Train on target/completion tokens only where the dataset format and model chat template permit it; verify loss masking by inspecting an actual batch.
8. Save adapter/checkpoint plus tokenizer, prompt template, catalog version, data manifest and optimizer/trainer state where resume is needed.
9. Run development evaluation after each candidate, not only training loss.
10. Stop an approach early if OOM, repeated timeouts, or little measured progress make it unsuitable for the budget.

**Budget policy:** one frozen model selection, one baseline SFT, one IR-SFT, and at most one carefully chosen data/staging variant before expanding hyperparameter search. Plan **sequential experiments** instead of attempting a full factorial sweep on Colab Pro.

## F4. SFT experiments

- **SFT-J:** base model fine-tuned on verified `D-JSON`.
- **SFT-I:** same base model fine-tuned on matched `D-IR`, then compile.
- **SFT-H (conditional):** same base model trained on plan/graph/parameter tasks.
- **SFT-I-RAG (conditional):** IR model with version-matched retrieval; note retrieval context must match its training setup if used during training.

Hold dataset provenance, train-task groups, evaluation tasks, optimizer budget and run logs constant wherever possible.

## F5. Data coverage intervention

Construct experiments with matched **additional example counts**:

1. Natural collected distribution (baseline).
2. Random augmentation on eligible workflow families.
3. Stratified augmentation by graph motif/operation category.
4. Targeted augmentation based on development errors, with human/fixture verification.

Main outcome: held-out *rare-pattern and unseen-combination* execution success; also monitor overall performance and regressions on common patterns.

## F6. Advanced only after justification

- Bounded structural-reward optimization or preference tuning if strong gold rewards and sufficient compute exist.
- Multi-agent approach only if stage-wise specialization demonstrates measurable added benefit.
- Distillation from larger teacher models only with clear teacher provenance, quality audits, and properly measured training cost; do not use model-generated labels as independent gold evaluation.

---

# 10. Workstream G: evaluation benchmark and protocol

## G1. Construct independent executable tasks

**Proposed initial benchmark:** 100–200 human-checked tasks if time permits (planning target, not a validated sample-size requirement), divided into difficulty bands and structural/rare-operation groups. Every benchmark task needs:

```text
case_id, requirement, allowed_catalog_version, starting_state,
input_fixture, expected_outputs, expected_side_effects,
negative_cases, credential_fixture_policy, time_limit,
permitted_external_hosts, gold_spec_author, review_status
```

Crucially, an **expected n8n JSON** can help compare structure, but must not be the sole answer key. For flexible workflows, **observable behavior under controlled fixtures is the preferred oracle**.

### Example oracle

Requirement: "If order.total > 500, notify sales. Otherwise record to table."

| Input | Expected |
|---|---|
| `total = 600` | One sales notification; no fallback table append. |
| `total = 500` | No notification; one fallback table append (strictly `>`). |
| `total = 100` | No notification; one fallback table append. |
| Missing `total` | Defined failure/skip/clarification outcome per task specification. |

**Test-oracle rule:** never ask the same model that generated the workflow to define the authoritative expected outputs on the fly.

## G2. Metrics and operational definitions

| Metric | Formula / decision rule | Caveat |
|---|---|---|
| **Parse rate** | parsed generations / attempted generations | Does not prove semantics. |
| **IR/schema rate** | outputs passing format and typed-schema check / attempts | Depends on IR expressiveness. |
| **n8n import rate** | artifacts accepted by the pinned platform / attempts | May miss runtime errors. |
| **Runtime execution rate** | artifacts completing fixture runs without unexpected engine errors / attempts | Does not prove intended outcome. |
| **Task success rate (primary)** | tasks whose specified oracle assertions all pass / evaluated tasks | Clearly define how multiple fixtures per task aggregate (e.g., all). |
| **Required-operation recall** | correctly selected required operations / annotated required operations | Gold operation sets may be non-unique. |
| **Unsupported-operation rate** | predicted operations absent from catalog / predicted operations | Version-sensitive. |
| **Parameter error rate** | missing/invalid requirements or bad bindings / checked parameter obligations | Some schemas dynamic and incomplete. |
| **Graph measures** | typed-edge precision/recall/F1 and optional graph edit distance | Alternative correct graphs exist. |
| **First-pass uplift** | success after bounded correction minus first-pass success | Also report extra compute/tokens. |
| **Cost and latency** | median/p95 generation time; tokens per task; GPU training/inference cost | Colab allocations may vary. |
| **Visual metrics** | node overlaps, crossings, alignment and human readability | Secondary, cannot replace task success. |

Report **success at the task level**, with per-difficulty/per-error-type results and stratified uncertainty intervals. When sample sizes are small, avoid making strong statistical claims based on a single-point difference.

## G3. Evaluation harness protocol

1. Reset sandbox fixture and mock services.
2. Generate artifact with a frozen configuration.
3. Save raw model output *before* sanitization/repair.
4. Run parser, catalog/graph checks, compiler and platform import; record separate outcomes.
5. Run controlled execution and evaluate final state/recorded side effects.
6. Collect failure trace, operation/parameter mismatches, and token/time statistics.
7. If correction is enabled, pass **only diagnostic evidence permitted by the experimental design** and repeat a bounded number of times.
8. Reset the environment again before next case.
9. Write immutable results keyed by run ID, task ID and model/config hash.

## G4. Experiments in practical priority order

| Priority | Experiment | Comparator | Scientific result expected |
|---|---|---|---|
| **P0** | Compiler expressiveness/round-trip | Hand-built gold IR↔n8n | Demonstrate what the representation can actually encode. |
| **P0** | J vs I vs optional S | Same untuned backbone | RQ1 effect without training. |
| **P0** | No RAG vs catalog RAG | Same backbone/output target | RQ2, retrieval benefits/errors. |
| **P1** | Untuned vs SFT-J vs SFT-I | Same data families/backbone | RQ1 + impact of SFT. |
| **P1** | Natural vs targeted augmentation | Matched sample counts/updates | RQ3; generalization/regression. |
| **P1** | One-pass vs staged | Same backbone/fixtures | RQ4; benefit vs compute. |
| **P2** | 0/1/2 feedback rounds | Same base generator | RQ5; correction-cost curve. |
| **Stretch** | Multi-agent or reward training | Strongest lower-cost comparator | Conditional research extension only. |

**Do not confound studies:** when comparing SFT-J and SFT-I, account for any difference in target length and compiler assistance. Report those differences explicitly.

## G5. Error taxonomy

Use a stable categorical label on every failure: `requirement_misread`, `missing_step`, `wrong_operation`, `unsupported_node`, `invalid_graph_port`, `wrong_branch`, `broken_data_binding`, `wrong_condition`, `invalid_parameter`, `missing_external_configuration`, `n8n_import_error`, `runtime_api_error`, `wrong_output`, `uncontrolled_side_effect`, `evaluator_or_fixture_issue`. A case can have multiple labels; distinguish **first causal error** from downstream effects if evidence permits.

---

# 11. Workstream H: integration, interface and demonstrator

Minimum demonstrator:

- Requirement input box; optional clarification for critical unspecified values.
- Selected model/experiment mode (clearly labeled for researchers).
- Generated graph preview with plain-language node rationale.
- Importable n8n JSON file and canvas-ready layout.
- Validation report, unresolved credentials/fields, assumptions, and safety notice.
- Controlled test-run button in sandbox; show actual oracle results.
- Export of reproducibility manifest for every generation.

**Important deployment semantics:** `generated` ≠ `validated` ≠ `tested` ≠ `approved to activate`. Never auto-activate or execute externally consequential actions based only on a model response.

---

# 12. Schedule and dependency-aware milestones

The existing LexaFlow Gantt chart places early research and architecture in October–early November 2026, dataset profiling and normalization in November–December, fine-tuning in late January–February 2027, Builder evaluation in February–early March, integration/robustness in March–April, and documentation/final presentation in April–May. **The sequence below refines that plan**, not a claim that all tasks will fit without adjustment.

| Phase / target window | Work | Exit gate (must be demonstrated) |
|---|---|---|
| **0. Oct–early Nov 2026** | Scope, literature, experiment pre-registration, frozen operation subset, n8n harness | Handwritten reference workflow imports/runs reproducibly. |
| **1. Nov 2026** | Collection, provenance, cleaning, first node catalog, profiling | Audit report, legal/quality filters, 30–50 verified dev cases. |
| **2. Nov–Dec 2026** | IR design, compiler, layout, validation, gold-fixture authoring | Core supported gold IRs compile/import and preserve expected fixture behavior. |
| **3. Dec 2026–Jan 2027** | Untuned JSON/IR/RAG/SDK baselines; GPU smoke tests | Comparative development results and selected backbone/representation. |
| **4. Late Jan–Feb 2027** | QLoRA and targeted dataset experiments | Saved adapters, logs, seeds/configs, completed ablations. |
| **5. Feb–Mar 2027** | Hierarchical/correction experiments if justified; integrated Builder | Frozen benchmark evaluation and reproducible demonstration. |
| **6. Mar–Apr 2027** | Robustness, statistical analysis, literature comparison, failure audit | Defensible claims, negative findings, complete method reporting. |
| **7. Apr–May 2027** | Thesis, artifact cleanup, final demonstrations | Reproducible repository/docs, final charts, archived code and model/dataset manifests. |

**Fallback if compute budget constrains training:** finish B0–B4, benchmark, and compiler/IR comparison as a coherent systems research study; train one selective QLoRA adapter when resources permit. Do not sacrifice independently verified evaluation to squeeze in many training runs.

---

# 13. Responsibility split and interfaces

Suggested Builder micro-roles (can be carried by a small subset of the six-person graduation team; **not** a rigid personnel allocation):

| Responsibility | Artifact | Handoff |
|---|---|---|
| Dataset & annotation owner | provenance data, splits, labels | `dataset_manifest.json`, verified examples |
| Node catalog/compiler owner | operation schemas, IR, n8n backend, layout | `ir_schema.json`, `compile(ir)->artifact` |
| Model & experiment owner | prompts, inference adapters, QLoRA checkpoints | `generate(requirement, catalog)->ir/json` |
| Evaluation owner (may overlap with other teams) | fixtures, sandbox runner, result database | `evaluate(artifact, scenario)->report` |

Builder-to-testing/repair module contract: immutable requirement and expectation references; IR graph; compiled n8n JSON; catalog/version hash; validation diagnostics; controlled execution trace; no raw credentials. The testing module must not silently redefine the builder's training/evaluation ground truth.

---

# 14. Risks, mitigations, and stop conditions

| Risk | Why it matters | Mitigation or decision |
|---|---|---|
| Limited Colab availability | Interrupted/insufficient training time | Smoke tests, checkpoints, staged experiments, CPU-side pipeline first. |
| Dataset leakage | Inflated scores by memorization | Group-aware splits and independent requirements. |
| Incorrect LLM-written descriptions | Misleading supervision | Label provenance tiers, human review and semantics checks. |
| Changes in n8n nodes/SDK | Version drift invalidates metrics | Freeze installation and catalog versions; record migration separately. |
| Catalog is incomplete | False validation and impossible dynamic fields | Explicitly mark unknown/dynamic fields; use sandbox query; report limits. |
| IR too restrictive | Compiler cannot express valid workflows | Round-trip on gold examples; extend grammar or narrow claims. |
| Too many components | Weak causal attribution, engineering overload | Sequential ablations and go/no-go gates. |
| LLM creates unsafe side effects | Real messages/deletions/payments | Mock, allowlist, sandbox, credentials never generated; human approval. |
| Structural metrics inflate results | Text/graph match without correct behavior | Independent execution oracle as primary outcome. |
| No measurable SFT advantage | Fine-tune novelty weak | Report result honestly; emphasize representation/data coverage findings if supported. |
| Reproducibility of GPU performance | Hardware variability | Log actual GPU, VRAM, time and compute consumption, run settings. |

**Stop/reconsider a direction when:** (a) it requires unsupported node behavior; (b) no independent test oracle can be built; (c) it cannot run at least a smoke test on available Colab resources; (d) all gains disappear against a stronger, fair baseline; or (e) safety constraints cannot be enforced.

---

# 15. Definitions of done and final scientific deliverables

## Builder MVP (engineering)

- [ ] At least one 8B–9B backbone generates a typed workflow representation from natural language.
- [ ] A pinned node catalog covers the declared supported subset and versions.
- [ ] Compiler generates correctly wired, importable n8n artifacts on verified seed examples.
- [ ] Layout pass produces non-overlapping, legible graphs on supported examples.
- [ ] Unresolved fields and credentials are reported, not invented.
- [ ] Sandbox execution and fixture-based checks are reproducible.

## Scientific minimum (non-negotiable)

- [ ] Clear preregistered RQs/hypotheses and strong baselines.
- [ ] Independent, documented development/test split with leakage mitigation.
- [ ] At least two representations or generation approaches compared on the *same* verified tasks.
- [ ] At least one controlled intervention beyond plain prompting (e.g., RAG, SFT, or data coverage), with an appropriate control.
- [ ] Import, semantic execution, and cost/latency measured separately.
- [ ] Per-class failures, limitations, ablations, and uncertainty reported.
- [ ] Released/reproducible evaluation scripts, sanitized configuration, dataset/model provenance, and sample workflows to the extent licensing allows.

## Possible thesis statement only **after evidence**

> "For a controlled subset of executable automation workflows, we find that [specific representation/grounding/training strategy] [improves / fails to improve] [defined measure] relative to [precise baselines], with the largest effects on [measured failure categories]."

This claim is defensible whether the proposed method wins or loses, provided the experiment is rigorous and transparently reported.

---

# 16. First 14 working days: operational checklist

| Day(s) | Exact task | Evidence of completion |
|---|---|---|
| **1** | Freeze n8n and environment; define in/out-scope operations | `environment.lock`, operation inventory |
| **2–3** | Create five hand-authored workflows with mock services; import and execute | Recorded fixture results |
| **3–4** | Draft IR v0.1, typed edges, unresolved-field format | Versioned JSON Schema and sample cases |
| **5–6** | Implement IR compiler for 4–6 foundational operations | Tests on seed examples |
| **6–7** | Add graph validation and simple layered layout | Validated, visually readable import |
| **8–9** | Collect 100–300 candidate templates with provenance and quality tiers | Raw inventory (size is target, not guaranteed) |
| **9–10** | Write 30–50 independent dev requirements/fixtures; separate from training | Frozen dev package |
| **11** | Prototype base model direct-JSON and IR inference | Saved prompts and outputs |
| **12** | Add operation-level retrieval baseline | Retrieval recall and generated results |
| **13** | Compare first-pass semantic/import performance and costs | Preliminary experiment table |
| **14** | Decide representation/model and plan the smallest feasible QLoRA smoke test | Explicit go/no-go memo |

**Best immediate action:** implement the **n8n sandbox + gold fixtures + IR compiler** in parallel with source collection. This prevents the team from spending weeks fine-tuning a model against the wrong output contract.

---

# 17. Reference and verification notes

## User-provided project artifacts

- `LexaFlow.docx`: project goal, proposed three-module lifecycle, small-model/data-bias strategy, hierarchical testing and repair; includes original project framing.
- `LexaFlow Gantt Chart.xlsx`: workstreams and October 2026–May 2027 schedule. Some existing spreadsheet dates may require reconciliation before use as exact execution deadlines.
- `2025.naacl-industry.3.pdf` — WorkTeam.
- `2411.05451v1.pdf` — WorkflowLLM.
- `2410.07869v3.pdf` — WorfBench.
- `2025.emnlp-industry.100.pdf` — Flow-Bench/Flow-Gen.
- `2026.findings-acl.140.pdf` — ComfyFlow.
- `2607.15845v2.pdf` — Knowledge-Centric Agents for Workflow Generation in ComfyUI.

## Original research and technical sources

1. WorkTeam, NAACL Industry 2025: https://aclanthology.org/2025.naacl-industry.3/
2. WorfBench, ICLR 2025: https://proceedings.iclr.cc/paper_files/paper/2025/hash/adbe936993aa7cf41e45054d8b72f183-Abstract-Conference.html
3. WorkflowLLM and code: https://github.com/OpenBMB/WorkflowLLM
4. IBM Flow-Bench: https://github.com/IBM/Flow-Bench
5. Chat2Workflow (2026): https://arxiv.org/abs/2604.19667 and https://github.com/zjunlp/Chat2Workflow
6. n8n Workflow SDK (official source): https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/workflow-sdk/README.md
7. n8n official documentation: https://docs.n8n.io/
8. Google Colab official FAQ (availability limits): https://research.google.com/colaboratory/faq.html
9. Hugging Face Qwen3.5-9B model card: https://huggingface.co/Qwen/Qwen3.5-9B
10. Hugging Face TRL PEFT/QLoRA guide: https://huggingface.co/docs/trl/en/peft_integration
11. Hugging Face SFT Trainer: https://huggingface.co/docs/trl/en/sft_trainer

**Version/date caution:** online projects and software can change after 23 October 2026. Record exact repository commits and package versions before execution. Commercial plan prices and included compute units must be checked in the account's checkout UI. This document makes no guarantee of a Colab GPU, fixed compute units, or demonstrated LexaFlow model performance.


---

## Implementation roadmap

# LexaFlow Builder — Step-by-Step Implementation & Research Plan

Goal: Build an AI system that takes a user's natural-language request and generates a correct, executable, well-organized workflow using an 8B–9B language model, with n8n as the execution environment.

We will develop multiple approaches, compare them scientifically, and select the strongest based on experimental results rather than assumptions.

The order below is designed to minimize wasted work, especially with your Colab Pro budget.

# Phase 1 — Define the problem and prepare the environment

### 1. Define exactly what the builder must support

- Define the input: natural-language workflow requirements.
- Define the output: an importable n8n workflow JSON.
- Specify supported workflow features: triggers, sequential actions, conditions, branches, loops, and data transformations.
- Define what counts as a correct workflow.
- Separate workflow correctness from visual quality.

Output: Builder requirements and scope document.

### 2. Choose the initial supported n8n nodes

- Start with approximately 10–20 node types.
- Include common triggers, HTTP requests, conditions, transformations, and integrations.
- Identify each node's supported operations and required parameters.
- Expand support later.

Output: Initial node and operation catalog.

### 3. Set up the development environment

- Install a fixed version of n8n locally using Docker.
- Prepare Python for datasets, models, and experiments.
- Prepare Google Colab Pro for training.
- Configure version control and experiment tracking.
- Create an isolated testing environment.

Output: Reproducible development environment.

### 4. Create manually verified example workflows

- Construct 15–20 workflows in n8n.
- Include simple, intermediate, and relatively complex scenarios.
- Export their JSON files.
- Verify that they execute correctly with controlled inputs.
- Document their expected behavior.

Output: A small collection of trusted workflow examples.

### 5. Implement an initial workflow evaluation tool

Build a script that can:

- Parse workflow JSON.
- Check node and connection validity.
- Import workflows into n8n.
- Execute workflows using test fixtures.
- Capture errors and outputs.
- Determine whether the expected behavior occurred.

This must exist before serious model training so we can measure progress objectively.

Output: Initial evaluation harness.

# Phase 2 — Dataset collection and preparation

### 6. Collect workflow datasets

Investigate and collect suitable workflows from:

- Official n8n templates.
- Public GitHub repositories.
- Existing workflow-generation datasets.
- Research datasets, including WorkflowLLM and Flow-Bench, where representations can be adapted.
- Additional manually constructed examples.

Track dataset provenance and permitted use.

Output: Raw workflow dataset.

### 7. Clean and normalize the dataset

- Remove invalid JSON.
- Detect broken node references.
- Handle unsupported nodes.
- Remove credentials and sensitive information.
- Standardize non-semantic fields.
- Record missing runtime dependencies.
- Deduplicate identical and near-identical workflows.

Output: Clean workflow dataset.

### 8. Analyze dataset distribution

Calculate:

- Frequency of every node and operation.
- Workflow lengths.
- Common node combinations.
- Branching and loop frequency.
- Graph patterns.
- Frequency of rare operations.

Research purpose: Understand dataset coverage and discover whether some capabilities are insufficiently represented.

Output: Dataset analysis report.

### 9. Generate natural-language descriptions

For each suitable workflow:

- Use its original description where available.
- Generate additional descriptions using a stronger LLM if necessary.
- Check whether the descriptions accurately represent the workflow.
- Human-review important examples.
- Record ambiguities and unsupported assumptions.

Create training pairs:

\\[ \text{Natural Language} \rightarrow \text{Workflow} \\]

Output: Paired natural-language/workflow dataset.

### 10. Prepare training and testing splits

Create separate datasets for:

- Training.
- Validation.
- Final testing.
- Unseen combinations.
- Rare nodes and operations.
- Increasing workflow complexity.

Group similar workflows before splitting to prevent leakage. Perform data augmentation only after the split.

Output: Reproducible dataset splits.

# Phase 3 — Investigate different workflow representations

This is one of the most important research phases.

### 11. Approach A — Direct JSON representation

The language model generates the n8n workflow JSON directly.

Natural-language request

8B–9B LLM

n8n Workflow JSON

Tasks:

- Prepare description-to-JSON training records.
- Normalize JSON fields.
- Define prompts and output constraints.
- Implement JSON parsing and validation.

Research purpose: Establish the simplest generation approach.

### 12. Approach B — Intermediate representation (IR)

Instead of generating n8n JSON directly, the model generates a simpler logical graph.

Natural-language request

8B–9B LLM

Compact workflow graph

Compiler

n8n Workflow JSON

Tasks:

- Design a compact workflow representation.
- Represent nodes, operations, connections, branches, and parameter bindings.
- Convert existing workflows into this representation.
- Build an IR-to-n8n compiler.
- Validate generated outputs.

Research purpose: Determine whether reducing output complexity improves model performance.

### 13. Approach C — Hierarchical workflow generation

Separate workflow creation into several reasoning tasks.

Natural-language request

Generate workflow plan

Select nodes and operations

Generate graph connections

Configure node parameters

Generate executable workflow

Tasks:

- Define intermediate planning representations.
- Generate training examples for each stage.
- Implement staged generation with one model.
- Validate outputs between stages.

Research purpose: Investigate whether decomposing generation improves correctness for complex workflows.

### 14. Investigate SDK-based generation as another representation

- Study n8n's Workflow SDK.
- Test whether an LLM can generate SDK code.
- Convert the generated code to n8n workflows.
- Compare against JSON and IR generation.

This is optional if the SDK is unsuitable for your supported nodes or time budget.

### 15. Compare output representations

| Comparison                  | Main question                                                      |
| --------------------------- | ------------------------------------------------------------------ |
| Direct JSON vs IR           | Is a compact representation easier for a small LLM?                |
| Direct JSON vs hierarchical | Does task decomposition improve generation?                        |
| IR vs hierarchical IR       | Is explicit planning useful beyond simplifying the representation? |
| IR vs SDK                   | Which gives better correctness with less engineering overhead?     |

Important: These experiments can initially use untuned models. Do not fine-tune every approach before learning which representations are promising.

# Phase 4 — Model selection and baseline experiments

### 16. Select candidate 8B–9B models

Start with:

- Qwen3-8B.
- Qwen3.5-9B.
- Optionally Llama-3.1-8B-Instruct as a literature-connected baseline.

### 17. Evaluate models without fine-tuning

For each candidate, test:

- Zero-shot generation.
- Few-shot generation.
- Structured output generation.
- Direct JSON and IR generation.

Use the same small development benchmark.

Output: Baseline model comparison.

### 18. Select one primary model

Compare:

- Correctness.
- Structured-output reliability.
- Inference cost.
- GPU memory requirements.
- Model and fine-tuning ecosystem compatibility.

Choose one model for the main training experiments, with an optional second model for replication.

Output: Primary model selection.

# Phase 5 — Fine-tuning experiments

### 19. Prepare Colab Pro training

- Install compatible training libraries.
- Configure model quantization.
- Prepare LoRA/QLoRA adapters.
- Test maximum feasible sequence length.
- Implement checkpoint saving and recovery.
- Run a short training smoke test.

Colab Pro doesn't guarantee a particular GPU or uninterrupted runtime. Begin with a small experiment before committing the entire training dataset.

### 20. Fine-tune using direct JSON

Train:

\\[ \text{NL} \rightarrow \text{n8n JSON} \\]

Evaluate the result against the untuned direct-generation baseline.

Output: Direct-JSON SFT model.

### 21. Fine-tune using intermediate representation

Train:

\\[ \text{NL} \rightarrow \text{Workflow IR} \\]

Use the same base model and comparable training budget.

Output: IR SFT model.

### 22. Compare the fine-tuned approaches

Experiment E1 — Effect of representation and fine-tuning

| Model condition  | Output        |
| ---------------- | ------------- |
| Base 8B–9B       | Direct JSON   |
| Fine-tuned 8B–9B | Direct JSON   |
| Base 8B–9B       | IR + compiler |
| Fine-tuned 8B–9B | IR + compiler |

Measure actual workflow correctness, not merely similarity to a reference JSON file.

Research question: Does an intermediate representation help an 8B–9B model synthesize more correct workflows?

### 23. Investigate hierarchical fine-tuning

If earlier results justify it:

- Train the model on planning tasks.
- Train graph-generation examples.
- Train parameter-filling examples.
- Combine them into a staged pipeline.

Compare against end-to-end IR fine-tuning with a matched data and training budget.

Research question: Does hierarchical supervision improve generalization, particularly on more complex workflow structures?

# Phase 6 — Knowledge augmentation and dataset experiments

### 24. Approach D — Retrieval-augmented generation (RAG)

Build a knowledge base containing:

- Node documentation.
- Available operations.
- Required parameters.
- Supported node versions.
- Validated workflow examples.

Retrieve relevant knowledge for each user request before generation.

### 25. Compare generation with and without RAG

Experiment E2 — Effect of knowledge retrieval

| Approach               | Retrieval |
| ---------------------- | --------- |
| Base model             | No        |
| Base model + RAG       | Yes       |
| Fine-tuned model       | No        |
| Fine-tuned model + RAG | Yes       |

Use the same chosen output representation and evaluation tasks.

Measure:

- Correct node selection.
- Hallucinated operations.
- Parameter correctness.
- Execution success.
- Additional token and inference costs.

Research question: Does retrieval help the model handle node documentation and uncommon operations?

### 26. Approach E — Dataset distribution improvement

Create experimental training variations:

- D1: Original dataset distribution.
- D2: Stratified or balanced sampling.
- D3: Targeted augmentation of rare nodes and difficult graph patterns.

Keep training budgets comparable.

### 27. Compare the dataset strategies

Experiment E3 — Effect of dataset composition

Train the same model using D1, D2, and D3.

Measure:

- Overall correctness.
- Performance on rare nodes.
- Performance on unseen combinations.
- Performance by graph complexity.
- Any regression on common workflows.

Research question: Does targeted dataset augmentation improve generalization more than simply using the original data distribution?

# Phase 7 — Validation, correction, and presentation

### 28. Build the validation pipeline

Validate:

- Generated representation syntax.
- Graph connections.
- Node types and versions.
- Required parameters.
- Expression dependencies.
- n8n import compatibility.

Return structured errors rather than only a generic failure message.

### 29. Approach F — Validation-guided correction

Allow the model to receive validation errors and correct its generated workflow.

Compare:

- No correction.
- Whole-workflow regeneration.
- Selective correction of invalid components.

Limit the number of attempts to make results comparable.

### 30. Compare correction strategies

Experiment E4 — Effect of validation feedback

Measure:

- First-pass success.
- Success after correction.
- Number of attempts.
- Additional compute cost.
- Regressions introduced by correction.

Research question: Can structured validation feedback improve workflow generation efficiently?

### 31. Build workflow visualization and layout

- Apply a deterministic graph layout algorithm.
- Generate readable node names.
- Organize branches.
- Avoid unnecessary overlaps.
- Add documentation or sticky notes where helpful.
- Export the visually arranged n8n JSON.

Treat visual layout quality separately from functional correctness.

### 32. Integrate the selected builder approaches

After comparing the alternatives, combine the techniques that demonstrate useful improvements.

For example, the final approach might be:

User natural language

Node documentation retrieval

Fine-tuned 8B–9B model

Intermediate workflow representation

Compiler and validator

Visual layout

Importable n8n workflow

This is only a candidate. It should not become the final architecture until the experiments support its components.

# Phase 8 — Final scientific evaluation

### 33. Build the final benchmark

Expand the development benchmark into an independently verified test suite covering:

- Basic workflows.
- Conditional workflows.
- Workflows with multiple branches.
- Complex data transformations.
- Unseen combinations.
- Rare operations.
- Longer workflows.

Keep this test set untouched during model and architecture selection.

### 34. Run final comparisons

Compare the strongest variants of:

| Experiment | Comparison                               |
| ---------- | ---------------------------------------- |
| E1         | Direct JSON vs IR vs hierarchical        |
| E2         | Untuned vs fine-tuned model              |
| E3         | With vs without RAG                      |
| E4         | Original vs balanced vs targeted dataset |
| E5         | With vs without validation correction    |
| E6         | Performance across complexity levels     |

Control decoding settings, evaluation inputs, and compute budgets where possible. Report additional inference attempts and retrieval costs rather than treating them as free improvements.

### 35. Evaluate scientific metrics

Measure:

| Metric                   | Meaning                                             |
| ------------------------ | --------------------------------------------------- |
| JSON/IR validity         | Is the generated representation valid?              |
| n8n import success       | Can n8n accept the result?                          |
| Node selection accuracy  | Were the appropriate components chosen?             |
| Graph correctness        | Are dependencies and branches correct?              |
| Parameter correctness    | Are operations configured correctly?                |
| Requirement satisfaction | Does it implement what was requested?               |
| Execution success        | Does it produce the correct outcome?                |
| Generalization           | Does it work on unseen structures and combinations? |
| Cost and latency         | How expensive is generation?                        |

Report results by workflow complexity and use confidence intervals or repeated runs where appropriate.

### 36. Perform error analysis

For each failed workflow, identify its main failure category:

- Wrong node.
- Missing node.
- Incorrect connection.
- Wrong operation.
- Invalid parameter.
- Incorrect expression.
- Missing requested behavior.
- Unsupported or ambiguous requirement.
- Execution-environment failure.

Analyze which methods reduce which errors.

This is important because an approach may improve syntax validity while leaving semantic correctness unchanged.

### 37. Write the scientific contribution

Your final contribution should be determined by the actual experimental findings.

Possible conclusions include:

- Intermediate representations improve workflow correctness for small models.
- Retrieval reduces hallucinated node operations.
- Hierarchical supervision improves complex graph generation.
- Targeted data augmentation improves rare-node performance.
- Some techniques increase cost without meaningful accuracy gains.

Negative results are also scientifically useful when experiments are well controlled.

### 38. Deliver the final builder

Produce:

- Trained model adapters.
- Workflow datasets and processing scripts.
- Selected workflow-generation pipeline.
- Compiler and validation components.
- n8n integration.
- Visual layout module.
- Reproducible experiment code.
- Benchmark and final results.
- Documentation explaining limitations.

## Overall research flow

1\. Data + n8n environment + evaluation benchmark

2\. Compare output representations

Direct JSON vs IR vs hierarchical / SDK

3\. Compare base and fine-tuned models

4\. Test improvement strategies

RAG · dataset coverage · validation feedback

5\. Select strongest experimentally supported combination

6\. Final evaluation + scientific analysis + Builder prototype

## What I would prioritize with your Colab Pro budget

Not every experiment requires GPU training. Dataset preparation, IR/compiler development, validation, and much of the execution benchmarking can run locally.

I would use this priority order:

1. First: Dataset, benchmark, n8n execution harness, IR and compiler.
2. Second: Untuned-model comparisons for JSON vs IR, plus few-shot and RAG baselines.
3. Third: One primary 8B–9B model with QLoRA, comparing direct JSON and IR under comparable training budgets.
4. Fourth: RAG and dataset-distribution ablations using the strongest trained representation.
5. Fifth: Hierarchical training and validation-guided correction, if earlier error analysis supports them.
6. Last: Reinforcement learning or multi-agent generation only if there is a clear remaining research question and sufficient compute.

The key is that we're not just developing a workflow builder. We're studying what makes smaller language models better at generating executable workflows.

I'd begin with Steps 1–5, especially constructing a small, independently verified benchmark and an n8n execution harness. That foundation will make every later architectural comparison scientifically meaningful.

---

## Inventory contract

# Milestone 1: scope and inventory contract

The target platform is n8n; the target version is **unresolved**. This milestone is
static dataset infrastructure, not an execution evaluator or training pipeline.

Proposed initial nodes: Manual Trigger, Set, HTTP Request, IF, and Sticky Note
(annotation only). The former `nodes.yaml` example is archived below;
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
.\.venv\Scripts\python.exe -m builder.inventory --input tests/fixtures --output reports/inventory-demo --catalog configs/inventory-catalog.json
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


---

## Milestone 1 report

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
.\.venv\Scripts\python.exe -m builder.inventory --input tests/fixtures --output reports/inventory-demo --catalog configs/inventory-catalog.json
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

See the Inventory contract section above for the complete v1 contract, safety boundaries and metric
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


## Archived planning example: dataset.yaml

```yaml
# Example only; no collection is enabled or implemented.
schema_version: 1
target_n8n_version: null # TODO: select and record an exact version.
paths:
  raw: data/raw
  manifests: data/manifests
  cleaned: data/cleaned
  paired: data/paired
  splits: data/splits
  gold: data/gold
collection:
  enabled: false
  local_only: true
  dry_run: true
sources:
  # Names reserve folders; source identities and permissions are unverified.
  - id: n8nbuilder
    path: data/raw/n8nbuilder
    url: null # TODO: verify canonical source URL.
    revision: null
    license: null # TODO: verify license and permitted use before collection.
    permitted_use: null
    enabled: false
  - id: zie619
    path: data/raw/zie619
    url: null
    revision: null
    license: null
    permitted_use: null
    enabled: false
  - id: nusquama
    path: data/raw/nusquama
    url: null
    revision: null
    license: null
    permitted_use: null
    enabled: false
provenance:
  # Proposed fields for the next inventory milestone, not a manifest implementation.
  required_fields:
    - source_url
    - source_id
    - source_revision
    - collected_at
    - source_timestamp
    - content_sha256
    - license
    - permitted_use
    - description_origin

```


## Archived planning example: nodes.yaml

```yaml
# Candidate initial catalog, awaiting target-version compatibility review.
schema_version: 1
target_n8n_version: null # TODO: select exact n8n version.
status: provisional
nodes:
  - type: n8n-nodes-base.manualTrigger
    type_version: null # TODO: verify against the selected n8n release.
    role: trigger
  - type: n8n-nodes-base.set
    type_version: null
    role: transform
  - type: n8n-nodes-base.httpRequest
    type_version: null
    role: action
# Entries express intended initial coverage, not verified generation support.

```


## Archived planning example: evaluation.yaml

```yaml
# Proposed settings only; no evaluator is implemented.
schema_version: 1
target_n8n_version: null # TODO: select exact n8n version.
random_seed: 42 # Initial reproducibility default, not an experimental finding.
checks:
  json_validity: true
  graph_validity: true
  importability: false # TODO: version-pinned isolated n8n environment.
  execution_success: false
  behavioral_correctness: false # TODO: independently specified behavior oracles.
splits:
  strategy: null # TODO: group exact/near duplicates and related variants.
  train_fraction: null
  validation_fraction: null
  test_fraction: null
benchmark:
  path: data/gold
  independent_verification_required: true
  selection_policy: null # TODO: define before benchmark construction.

```

## Compact layout verification — 26 October 2026

Implementation moved to src/builder/reader.py, validator.py and inventory.py. The
Python import path and CLI are builder.inventory; distribution metadata remains
lexaflow 0.1.0. Editable installation was refreshed. All 44 existing test cases are
preserved across tests/test_reader.py, test_validator.py and test_inventory.py.
Full pytest: 44 passed in 0.92s on Python 3.12.10. Ruff lint and formatting passed.
Synthetic CLI command:

```powershell
.\.venv\Scripts\python.exe -m builder.inventory --input tests/fixtures --output reports/inventory-layout --catalog configs/inventory-catalog.json
```

All three generated files were byte-identical to the prior inventory-demo outputs.
The old module path is intentionally removed; no schema or analysis rules changed.
The new exploration notebook is unexecuted. Former planning YAML files are archived
in this document; inventory-catalog.json is the active runtime configuration.
