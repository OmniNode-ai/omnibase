<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: d7af1033-8f7f-4c4c-a97a-c2d83b9fee9e -->
<!-- name: index.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:54.974985 -->
<!-- last_modified_at: 2025-05-19T16:19:54.974987 -->
<!-- description: Stamped Markdown file: index.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 2e1015f2771866a770a0a1a4016f2cebae8660116476f2a818485c1dc8b7d83c -->
<!-- entrypoint: {'type': 'markdown', 'target': 'index.md'} -->
<!-- namespace: onex.stamped.index.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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

---

## 🛠️ How‑to Guides

*Coming soon – step‑by‑step walkthroughs will live in* **[`docs/guides/`](./guides/)**.

---

## 🏛️ Architecture Deep Dives

* In‑depth explorations, trade‑offs, and reference diagrams are placed under **[`docs/architecture/`](./architecture/)**.

---

## 💡 RFCs & ADRs

| Folder                  | Description                       |
| ----------------------- | --------------------------------- |
| [`docs/rfcs/`](./rfcs/) | Proposals under active discussion |
| [`docs/adr/`](./adr/)   | Accepted architecture decisions   |

---

## 🔐 Security

Threat models and hardening guides are collected in **[`docs/security/`](./security/)**.

---

## 📝 Contributing to Docs

1. Follow the directory conventions outlined in [`docs/README.md`](./README.md).
2. Every substantial document should include a short metadata block (`Status`, `Last Updated`, etc.).
3. Name files with lowercase snake‑case; number RFCs/ADRs with zero‑padded prefixes (e.g., `rfc-0007-async-execution.md`).
4. Keep line length ≲ 100 chars when practical.
5. Run `pre‑commit run --all-files` before pushing.

---

<!-- Add more navigation helpers or badges here as the docs site evolves -->
