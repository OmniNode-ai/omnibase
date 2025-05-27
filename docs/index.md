# OmniBase Documentation Hub

> **Status:** Active
> **Last Updated:** 2025-01-27
>
> This landing page is the entry point for all OmniBase documentation. Use the quick links below to jump straight to specs, guides, and design artifacts.

---

## 📚 Core Specifications

| Spec                                                    | Purpose                                            |
| ------------------------------------------------------- | -------------------------------------------------- |
| [Metadata Specification](./metadata.md)                 | Canonical metadata schema, field semantics, and overview |
| [Core Protocols](./reference-protocols-core.md)         | Core protocols and execution |
| [Registry Protocols](./reference-protocols-registry.md) | Registry, validation, handler protocols |
| [Data Models](./reference-data-models.md)               | Data models, composition, testing |
| [Error Handling Specification](./error_handling.md)     | Canonical error/result model, taxonomy, and guarantees |
| [Security Overview](./reference-security-overview.md)   | Architecture and authentication |
| [Security Implementation](./guide-security-implementation.md) | Authorization, secrets, secure execution |
| [Security Design](./architecture-security-design.md)    | Network security architecture |
| [Security Monitoring](./guide-security-monitoring.md)   | Security monitoring and vulnerability management |
| [Incident Response](./guide-incident-response.md)       | Incident response and compliance |
| [Orchestration Specification](./orchestration.md)       | Orchestrator patterns, lifecycle, CLI, and contracts |
| [Registry Specification](./registry.md)                 | Registry types, discovery, policy, and federation |
| [ExecutionContext & Capability Protocols](./execution_context.md) | Runtime context, capability enforcement, and secrets |
| [CLI Interface & Output Formatting](./cli_interface.md) | Canonical CLI, formatter registry, and output modes |
| [Registry Architecture](./registry_architecture.md)     | Specification for the ONEX/OmniBase Node and CLI Adapter Registry |
| [Monadic Node Core](./architecture-node-monadic-core.md) | Core monadic principles and interfaces |
| [Node Composition](./architecture-node-composition.md)   | Composition patterns and execution models |
| [Handler Protocols](./reference-handlers-protocol.md)   | Handler protocols and interfaces |
| [Handler Registry](./reference-handlers-registry.md)    | Registry API and management |
| [Handler Implementation](./guide-handlers-implementation.md) | Implementation examples and testing |

---

## 🛠️ How-to Guides

Step-by-step walkthroughs and tutorials are available in **[`docs/guides/`](./guides/)**.

---

## 🏛️ Architecture Deep Dives

In-depth explorations, trade-offs, and reference diagrams are placed under **[`docs/architecture/`](./architecture/)**.

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

## 🧪 Testing

Testing guidelines, fixtures, and node testing specifications are available in **[`docs/testing/`](./testing/)**.

---

## 📝 Contributing to Documentation

1. Follow the directory conventions outlined in [`docs/README.md`](./README.md).
2. Every substantial document should include a short metadata block (`Status`, `Last Updated`, etc.).
3. Name files with lowercase snake_case; number RFCs with zero-padded prefixes (e.g., `rfc-0001-async-execution.md`).
4. Keep line length ≤ 100 chars when practical.
5. Run `pre-commit run --all-files` before pushing.

---

## 📂 Documentation Structure

```
docs/
├── index.md                    # This file
├── README.md                   # Documentation overview
├── architecture/               # Architecture deep dives
├── error_handling/             # Error handling specifications
├── guides/                     # How-to guides and tutorials
├── metadata/                   # Metadata specifications
├── nodes/                      # Node architecture and specifications
├── onex/                       # ONEX protocol documentation
├── plugins/                    # Plugin system documentation
├── protocol/                   # Protocol specifications
├── rfcs/                       # Request for Comments
├── security/                   # Security specifications
├── standards/                  # Coding and naming standards
├── templates/                  # Documentation templates
├── testing/                    # Testing guidelines
└── tools/                      # Tool documentation
``` 