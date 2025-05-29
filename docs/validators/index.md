<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:27.225611'
description: Stamped by ONEX
entrypoint: python://index.md
hash: b1dd0ec2ff8306d065b6729b79c2173d3d5ca879eacd6d0ba0a240fdd318499c
last_modified_at: '2025-05-29T11:50:15.393473+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: index.md
namespace: omnibase.index
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: a26b0c8f-1289-4427-af58-5f9d31c7a2a4
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# ONEX Validators Canonical Index

> **Status:** Canonical
> **Last Updated:** 2025-05-16
> **Purpose:** This directory contains canonical specifications, protocols, and implementation guides for all ONEX validators. All validator types, including chunk validators, metadata validators, and future domain-specific validators, will be documented here.

> **Note:** All validator registration, enforcement, and discovery is now metadata-driven and governed by the canonical metadata specification. See [docs/metadata.md](../metadata.md) for stamping/enforcement requirements.

---

## Table of Contents

1. [ONEX Chunk Validator Specification (v0.1)](#onex-chunk-validator-specification-v01)
2. [Validator Protocol and Result Model Reference](../structured_testing.md#onex-v01-canonical-validator-protocol-and-result-model)
3. [Planned/Upcoming Validator Specs](#planned-upcoming-validator-specs)

---

## 1. ONEX Chunk Validator Specification (v0.1)

// Begin canonical content from onex_chunk_validator_spec.md

## ONEX Chunk Validator Specification (v0.1)

### Overview

The ONEX Chunk Validator is responsible for analyzing and slicing large source files into well-formed, testable, and versionable units. This system supports metadata stamping, token budgeting, refactor planning, and agent-compatible context reuse.

---

### 📦 Phase 1: MVP Chunking (Line + Token Budget)

* Uses Python's `tokenize` and line slicing
* Supports chunk types:

  * `code_chunk`
  * `test_chunk`
  * `comment_block`
* Inserts `chunk_id` into metadata block per chunk
* Automatically builds `metadata.yaml` with:

```yaml
chunks:
  - id: chunk_imports
    type: code
    token_count: 36
    start_line: 1
    end_line: 8
```

* Token limit: configurable (e.g. 300 tokens)
* Used in: test slicing, LLM prompt shaping, CLI `diff` tooling

---

### 🧠 Phase 2: AST-Based Chunking (Structural)

* Uses language-native ASTs (e.g. `ast` in Python, `ts-morph` in TS)
* Chunk types:

  * `function`, `class`, `method`, `block`
* Maintains chunk graph:

```yaml
chunks:
  - id: chunk_001
    symbol: my_function
    deps: [chunk_000_imports]
    type: function
    tokens: 87
```

* Adds `symbol`, `dependencies`, and `semantic_type`
* Enables refactor previews and agent reranking

---

### 🧱 Phase 3: Dependency Graph + Agent-Aided Refactor

* Construct a node graph of file symbols
* Enable diff-based rebuild plans
* Agent can suggest:

  * Merge chunks
  * Extract method
  * Promote chunk to node
* Output chunk graph in `.treechunks` file

```yaml
chunk_graph:
  nodes:
    - id: chunk_foo
      type: function
      rank: 0.83
    - id: chunk_bar
      type: method
      rank: 0.41
  edges:
    - from: chunk_foo
      to: chunk_utils
      reason: "import"
```

---

### 🔧 CLI Integration

```bash
onex chunk path/to/code.py
onex chunk --phase=2 --graph
onex chunk --extract --to metadata.yaml
```

---

### 🧪 CI Enforcement

* CI verifies:

  * No overlapping chunks
  * Full file coverage
  * Metadata hash matches extracted structure
  * Symbol-to-ID uniqueness

---

### 🔍 Use Cases

* Token-optimized chunking for GPT-4.1 / Claude
* Precise diffing for fine-grained CI feedback
* Graph construction for training agents and refactor planning
* Caching execution results per chunk for trust scoring

---

**Status:** The chunk validator is the canonical slicing mechanism for large source analysis, LLM prep, test structuring, and metadata graphing in ONEX environments. Phase 1 is required for MVP.

---

## 2. Validator Protocol and Result Model Reference

See: [docs/structured_testing.md#onex-v01-canonical-validator-protocol-and-result-model](../structured_testing.md#onex-v01-canonical-validator-protocol-and-result-model)

---

## Validator Orchestration Extensions

### Validator Profiles

Validator profiles enable context-specific validation bundles, allowing users to select different sets of validators for different execution contexts:

- **fast**: Lightweight checks only (linters, schema presence)
- **ci**: Balanced validations for continuous integration
- **full**: Full validation suite (includes slow, optional, and edge-case validators)

Profiles are defined as metadata groups and dynamically resolved. Example CLI usage:

```bash
run_validators --profile fast
run_validators --profile ci
run_validators --profile full
```

Profiles are governed by metadata fields and can be extended as new validation contexts emerge.

---

### Scorecard & Grading System

The validator system supports project health scoring and grading based on weighted validator results:

- Each validator can define a **weight** and **severity** in its metadata.
- Validation runs produce a health **score** and **grade** (e.g., `A`, `B-`, `F`).
- Results are suitable for CI dashboards, PR checks, and agent feedback.

Example output:

```json
{
  "score": 88.3,
  "grade": "B+",
  "failed": ["PerformanceAntiPatternsValidator", "TagCoverageValidator"]
}
```

Scorecard and grading logic is protocol-aligned and should be implemented in the validator result model/reporting pipeline.

---

### Streaming Validator Results

Validator results can be streamed in real time to the CLI, dashboards, and agents:

- Results are streamed incrementally, highlighting early failures before full validation completes.
- Streaming can be toggled via CLI flag:

```bash
run_validators --stream
```

This enables progressive feedback and integration with agent UIs or CI dashboards.

---

## 3. Planned/Upcoming Validator Specs (Extended)

- [ ] Metadata Block Validator
- [ ] Trust Chain Validator
- [ ] Registry Entry Validator
- [ ] Custom domain-specific validators
- [ ] **Metadata enhancements:** cost, category, recommended_profile, dependencies (see [docs/metadata.md](../metadata.md))
- [ ] Remote validator packs (load from external sources)
- [ ] CI optimization via metadata fields (priority, risk_level)
- [ ] Trust system integration (validator results feed into trust scores)

---

> All validator orchestration, reporting, and configuration is protocol-aligned and metadata-driven. See [docs/metadata.md](../metadata.md) for canonical field definitions and enforcement requirements.
