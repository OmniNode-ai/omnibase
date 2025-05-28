<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: fe9435d3-d963-43d8-9722-6ab68a4f12fb
author: OmniNode Team
created_at: 2025-05-28T12:40:26.816463
last_modified_at: 2025-05-28T17:20:04.205230
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 17bc33616f110bb100099291c7b80cb8f27f81d6b45b8b8bd558ae5e7b558439
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.index
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX v0.1 Canonical Specification Index

> **Status:** Canonical
> **Last Updated:** 2025-05-16
> **Purpose:** This document aggregates all ONEX v0.1 canonical specifications and provides links to their authoritative sections in the OmniBase documentation. All ONEX v0.1 requirements supersede any previous or conflicting details in their respective domains.

---

## Table of Contents

1. [Metadata Block Specification](../metadata.md#onex-v01-canonical-metadata-block-specification)
2. [Validator Protocol and Result Model](../structured_testing.md#onex-v01-canonical-validator-protocol-and-result-model)
3. [Test Registry Protocol](../structured_testing.md#onex-v01-canonical-test-registry-protocol)
4. [Directory Tree Validation](../registry.md#onex-v01-canonical-directory-tree-validation)
5. [Conflicts Pending Resolution](./conflicts_pending_resolution.md)

---

## 1. Metadata Block Specification

See: [docs/metadata.md](../metadata.md#onex-v01-canonical-metadata-block-specification)

Defines the canonical YAML schema for ONEX node metadata blocks, including required, recommended, execution, trust, registry, and CI fields. Specifies storage, format, and compliance requirements.

---

## 2. Validator Protocol and Result Model

See: [docs/structured_testing.md](../structured_testing.md#onex-v01-canonical-validator-protocol-and-result-model)

Specifies the canonical Python Protocol for validators, the required UnifiedResultModel/OnexMessageModel structure, forbidden patterns, DI/registry requirements, and CLI integration.

---

## 3. Test Registry Protocol

See: [docs/structured_testing.md](../structured_testing.md#onex-v01-canonical-test-registry-protocol)

Defines the ONEX test registry protocol, including test file location, registration, metadata, discovery, enforcement, and CLI integration.

---

## 4. Directory Tree Validation

See: [docs/registry.md](../registry.md#onex-v01-canonical-directory-tree-validation)

Describes the .tree and .treerules system for canonical directory structure enforcement, validation rules, CI/pre-commit integration, and planned enhancements.

---

## 5. Conflicts Pending Resolution

See: [docs/onex/conflicts_pending_resolution.md](./conflicts_pending_resolution.md)

Any conflicts or ambiguities found during ONEX v0.1 integration are recorded here for review and resolution.

# ONEX: OmniNode Execution Protocol

ONEX is the protocol that defines how all OmniNode components are represented, validated, and executed as self-contained "nodes." Each node is defined by metadata, a contract, and an entrypoint, and adheres to a unified lifecycle.

## Key Resources

- [Execution Architecture](../milestones/onex_execution_architecture.md)
- [Protocol Definitions](../nodes/protocol_definitions.md)
- [Node Contracts](../nodes/node_contracts.md)
- [Reducer State and Planning](../nodes/state_reducers.md)
