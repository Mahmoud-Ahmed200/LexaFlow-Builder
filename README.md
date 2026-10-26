# LexaFlow

**AI-Powered Workflow Generation, Testing, and Repair**

LexaFlow is a graduation research project exploring how AI can turn natural-language instructions into executable automation workflows. The project uses **n8n** as its initial workflow platform.

## Project Overview

LexaFlow is organized around three research modules:

- **Builder:** Generates workflows from natural-language requirements.
- **Tester:** Develops tests to check workflow components and overall behavior.
- **Repairer:** Investigates workflow failures and proposes fixes.

The long-term goal is to connect these modules into a workflow lifecycle:

**Requirement → Generation → Testing → Execution → Diagnosis → Repair → Re-testing**

## Current Status

**Milestone 1 is complete.** The Builder currently provides a local workflow inventory tool that reads n8n JSON files, checks basic structural consistency, and summarizes workflow data. Workflow generation, execution, and automatic repair are future work.

## Repository Structure

```text
LexaFlow/
├── src/builder/    # Builder source code
├── data/           # Workflow datasets
├── configs/        # Configuration files
├── tests/          # Automated tests and fixtures
├── docs/           # Architecture and milestone documentation
├── notebooks/      # Research and experimentation notebooks
└── reports/        # Generated analysis reports
```

## Documentation

- [Architecture](docs/architecture.md) — system design and proposed components.
- [Milestones](docs/milestones.md) — research roadmap, progress, and implementation notes.
