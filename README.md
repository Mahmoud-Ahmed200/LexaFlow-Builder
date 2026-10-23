
# LexaFlow — Workflow Builder

## Overview

The Workflow Builder is responsible for generating automation workflows from natural-language requirements.

The goal is to build a model that generates workflows that are not only syntactically valid, but also structurally correct, semantically meaningful, and suitable for execution.

This module focuses on dataset analysis, workflow similarity, targeted data collection, model fine-tuning, and generation evaluation.

## Objectives

- Analyze workflow datasets and identify biases and underrepresented patterns.
- Measure workflow similarity and detect duplicates.
- Collect and normalize targeted workflow examples.
- Fine-tune a language model for workflow generation.
- Evaluate generated workflows based on structure, correctness, complexity, and generalization.


## Workflow

1. **Dataset Profiling:** Understand dataset quality, distribution, and biases.
2. **Workflow Similarity:** Identify duplicates and structural similarities.
3. **Data Preparation:** Collect, clean, normalize, and split the dataset.
4. **Model Training:** Fine-tune a model to generate workflows from user requests.
5. **Evaluation:** Measure structural validity, semantic correctness, and generalization.

## Evaluation

Generated workflows will be evaluated across multiple dimensions:

- Syntax and schema validity
- Node and parameter correctness
- Graph structure and data-flow correctness
- Semantic alignment with user requirements
- Performance across different workflow complexities
- Execution success, where supported by the evaluation environment

## Scope

This repository covers the Workflow Builder module of LexaFlow. Hierarchical test-case generation, execution-based failure diagnosis, and workflow repair are handled by the other project modules.

## Research

The implementation and experiments will be guided by research on workflow generation, dataset construction, graph-based evaluation, and model fine-tuning.

