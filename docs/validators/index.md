<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: bf1b8e68-fb67-4374-9b87-65d7774ea7b8
author: OmniNode Team
created_at: 2025-05-27T07:40:22.349882
last_modified_at: 2025-05-27T17:26:51.881070
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 03409d6d5db1fca1bb3493b480dc7c8c5aec7defab53aa63449afafceb338163
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.index
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Validators Canonical Index

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** This directory contains canonical specifications, protocols, and implementation guides for all ONEX validators  
> **Audience:** Validator developers, system architects, quality engineers  

---

## Overview

This directory contains canonical specifications, protocols, and implementation guides for all ONEX validators. All validator types, including chunk validators, metadata validators, and domain-specific validators, are documented here.

> **Note:** All validator registration, enforcement, and discovery is now metadata-driven and governed by the canonical metadata specification. See [Metadata Specification](../metadata.md) for stamping/enforcement requirements.

---

## Table of Contents

1. [ONEX Chunk Validator Specification](#onex-chunk-validator-specification)
2. [Validator Protocol and Result Model Reference](#validator-protocol-and-result-model-reference)
3. [Validator Orchestration Extensions](#validator-orchestration-extensions)

---

## ONEX Chunk Validator Specification

### Overview

The ONEX Chunk Validator is responsible for analyzing and slicing large source files into well-formed, testable, and versionable units. This system supports metadata stamping, token budgeting, refactor planning, and agent-compatible context reuse.

### Phase 1: MVP Chunking (Line + Token Budget)

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

### Phase 2: AST-Based Chunking (Structural)

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

### Phase 3: Dependency Graph + Agent-Aided Refactor

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

### CLI Integration

```bash
onex chunk path/to/code.py
onex chunk --phase=2 --graph
onex chunk --extract --to metadata.yaml
```

### CI Enforcement

* CI verifies:
  * No overlapping chunks
  * Full file coverage
  * Metadata hash matches extracted structure
  * Symbol-to-ID uniqueness

### Use Cases

* Token-optimized chunking for GPT-4.1 / Claude
* Precise diffing for fine-grained CI feedback
* Graph construction for training agents and refactor planning
* Caching execution results per chunk for trust scoring

**Status:** The chunk validator is the canonical slicing mechanism for large source analysis, LLM prep, test structuring, and metadata graphing in ONEX environments. Phase 1 is required for MVP.

---

## Validator Protocol and Result Model Reference

See: [Structured Testing - ONEX Validator Protocol and Result Model](../structured_testing.md#onex-v01-canonical-validator-protocol-and-result-model)

---

## Validator Orchestration Extensions

### Validator Profiles

Validator profiles enable context-specific validation bundles, allowing users to select different sets of validators for different execution contexts:

- **fast**: Lightweight checks only (linters, schema presence)
- **ci**: Balanced validations for continuous integration
- **full**: Full validation suite (includes slow, optional, and edge-case validators)

Profiles are defined as metadata groups and dynamically resolved. Example CLI usage:

```bash
onex run validators --profile fast
onex run validators --profile ci
onex run validators --profile full
```

Profiles are governed by metadata fields and can be extended as new validation contexts emerge.

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

### Streaming Validator Results

Validator results can be streamed in real time to the CLI, dashboards, and agents:

- Results are streamed incrementally, highlighting early failures before full validation completes.
- Streaming can be toggled via CLI flag:

```bash
onex run validators --stream
```

This enables progressive feedback and integration with agent UIs or CI dashboards.

---

## Implementation Guidelines

### Validator Development

All validators must:

1. **Implement the Validator Protocol**: Follow the canonical validator protocol defined in [Structured Testing](../structured_testing.md)
2. **Include Metadata**: Provide complete metadata blocks with proper classification
3. **Support Profiles**: Indicate which profiles the validator belongs to
4. **Define Weights**: Specify weight and severity for scoring systems
5. **Handle Streaming**: Support incremental result reporting when applicable

### Registration and Discovery

Validators are discovered through:

- Metadata-driven registry scanning
- Protocol-compliant introspection
- Profile-based filtering
- Dynamic loading from entry points

### Quality Standards

- **Test Coverage**: >90% test coverage required
- **Performance**: Must complete within reasonable time limits
- **Error Handling**: Robust error handling with structured error reporting
- **Documentation**: Complete documentation with usage examples

---

## References

- [Structured Testing](../structured_testing.md) - Validator protocol definitions
- [Metadata Specification](../metadata.md) - Metadata requirements
- [Error Handling](../error_handling.md) - Error reporting standards
- [Registry](../registry.md) - Validator registration and discovery
- [Testing Guide](../testing.md) - Testing standards for validators

---

**Note:** All validator orchestration, reporting, and configuration is protocol-aligned and metadata-driven. See [Metadata Specification](../metadata.md) for canonical field definitions and enforcement requirements.
