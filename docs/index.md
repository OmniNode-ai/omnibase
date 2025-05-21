<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: index.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 1856a88e-e950-4535-b862-4897ea748083 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158487 -->
<!-- last_modified_at: 2025-05-21T16:42:46.052211 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a7d7b9317dc9296e4f758a607df53a36ce0fbeb9cf44f183d3ba15e58f016e47 -->
<!-- entrypoint: {'type': 'python', 'target': 'index.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.index -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: index.md -->
<!-- version: 1.0.0 -->
<!-- uuid: e7ff1f1a-8e94-4dcf-9e3a-141a24205613 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.433532 -->
<!-- last_modified_at: 2025-05-21T16:39:56.064285 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 68479f79923e5eb0af816862609f4821d4a7c0ee6bfa5e137c60769ddc6433dd -->
<!-- entrypoint: {'type': 'python', 'target': 'index.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.index -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: index.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 3d5a3b94-2ee0-4a8c-af9f-1d90bcd68734 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.661785 -->
<!-- last_modified_at: 2025-05-21T16:24:00.314391 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a3c780393931a279eb1547db1cb2bf2190a78391cbc2b00ae0a2cc4dc24a1bf4 -->
<!-- entrypoint: {'type': 'python', 'target': 'index.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.index -->
<!-- meta_type: tool -->
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
