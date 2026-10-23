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