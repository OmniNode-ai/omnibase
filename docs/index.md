<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.439569'
description: Stamped by ONEX
entrypoint: python://index.md
hash: 56f10af690556ba9e678aae0c2f08d4e0f55d1deb22e8c019e215560c0f64b8d
last_modified_at: '2025-05-29T11:50:14.971401+00:00'
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
uuid: 3777e348-39c1-46df-a9c3-ad3909680a5e
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# OmniBase Documentation Hub

> **Status:** Draft
> **Last Updated:** 2025‑05‑16
>
> This landing page is the entry‑point for all OmniBase documentation. Use the quick‑links below to jump straight to specs, guides, and design artefacts.

---

## 📚 Canonical Specs

| Spec                                                    | Purpose                                            |
| ------------------------------------------------------- | -------------------------------------------------- |
| [Metadata Spec](./metadata.md)                          | Canonical metadata schema, field semantics, and overview |
| [Metadata Deep Dives](./metadata/)                      | Advanced topics: dependency resolution, lineage, validation |
| [Error Handling Spec](./error_handling.md)              | Canonical error/result model, taxonomy, and guarantees |
| [Error Handling Deep Dives](./error_handling/)          | Advanced topics: observability, retry, circuit breaker |
| [Security Spec](./security.md)                          | Canonical security, sandboxing, and capability model |
| [Security Deep Dives](./security/)                      | Threat model and advanced security topics |
| [Protocols Spec](./protocols.md)                        | Core interface protocols, ABCs, and compatibility |
| [Orchestration Spec](./orchestration.md)                | Orchestrator patterns, lifecycle, CLI, and contracts |
| [Registry Spec](./registry.md)                          | Registry types, discovery, policy, and federation |
| [Graph Extraction & Schema Reference](./graph_extraction.md) | Metadata graph, CLI, and schema tooling |
| [ExecutionContext & Capability Protocols](./execution_context.md) | Runtime context, capability enforcement, and secrets |
| [CLI Interface & Output Formatting](./cli_interface.md) | Canonical CLI, formatter registry, and output modes |
| [OmniBase Design Spec](./specs/omnibase_design_spec.md) | Source‑of‑truth architecture & protocol definition |
| [Registry Architecture](./registry_architecture.md)        | Canonical specification for the ONEX/OmniBase Node and CLI Adapter Registry, including versioned artifact layout, loader/discovery logic, and registry-centric best practices. |

---

## 🛠️ How‑to Guides

*Coming soon – step‑by‑step walkthroughs will live in* **[`docs/guides/`](./guides/)**.

---

## 🏛️ Architecture Deep Dives

* In‑depth explorations, trade‑offs, and reference diagrams are placed under **[`docs/architecture/`](./architecture/)**.

---

## 💡 RFCs

| Folder                  | Description                       |
| ----------------------- | --------------------------------- |
| [`docs/rfcs/`](./rfcs/) | Proposals under active discussion |

*Note: Architecture Decision Records (ADRs) will be added to `docs/adr/` when architectural decisions need to be formally documented.*

---

## 🔐 Security

Threat models and hardening guides are collected in **[`docs/security/`](./security/)**.

---

## 📝 Contributing to Docs

1. Follow the directory conventions outlined in [`docs/README.md`](./README.md).
2. Every substantial document should include a short metadata block (`Status`, `Last Updated`, etc.).
3. Name files with lowercase snake‑case; number RFCs with zero‑padded prefixes (e.g., `rfc-0007-async-execution.md`).
4. Keep line length ≲ 100 chars when practical.
5. Run `pre‑commit run --all-files` before pushing.

---

<!-- Add more navigation helpers or badges here as the docs site evolves -->
