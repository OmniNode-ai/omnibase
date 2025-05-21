<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: infrastructure.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 90aa7f47-6c8f-49f5-8484-27fdb2c79276 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158552 -->
<!-- last_modified_at: 2025-05-21T16:42:46.060570 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 92995dcbd3976e6f6ec14bc6f5fe2590f1c526963ef1965f4edc40e27f8b05ff -->
<!-- entrypoint: {'type': 'python', 'target': 'infrastructure.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.infrastructure -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: infrastructure.md -->
<!-- version: 1.0.0 -->
<!-- uuid: d5a3a27d-b456-4a5d-97c5-aaed3bab05dd -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.433611 -->
<!-- last_modified_at: 2025-05-21T16:39:56.066262 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: ffd67e486b5b598df66deb9415cfd028bd63894febeb95248918514703d0677f -->
<!-- entrypoint: {'type': 'python', 'target': 'infrastructure.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.infrastructure -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: infrastructure.md -->
<!-- version: 1.0.0 -->
<!-- uuid: fa2f2000-e70c-46bb-8df7-af1473e7b7ff -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.661847 -->
<!-- last_modified_at: 2025-05-21T16:24:00.306366 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 63a3cb63fed9a6a3bd00917561078f62d55a786b942d9324df6bbc26297bc348 -->
<!-- entrypoint: {'type': 'python', 'target': 'infrastructure.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.infrastructure -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

# OmniNode Infrastructure Specification

> **Status:** Canonical Reference
> **Last Updated:** 2025-05-14
> **Owner:** foundation-team
> **Purpose:** This document defines the canonical infrastructure, hardware, model hosting, container standards, development tooling, security, and deployment requirements for the OmniNode/ONEX platform. All environment, deployment, and operational requirements are specified here.

---

## Table of Contents

1. [OmniNode Infrastructure Overview](#omninode-infrastructure-overview)
2. [Planned/Upcoming Infrastructure and Deployment Specs](#plannedupcoming-infrastructure-and-deployment-specs)

---

## 1. OmniNode Infrastructure Overview

> **Last updated:** 2025-05-14
> **Status:** Canonical reference
> **Owner:** foundation-team

This document defines the current infrastructure setup, hardware environment, model hosting configuration, and deployment considerations for local and distributed OmniNode development.

---

## 💻 Hardware Inventory

### Primary Devices

| Label         | Type           | Specs                                          |
| ------------- | -------------- | ---------------------------------------------- |
| **AIPC**      | AI Workstation | RTX 5090 (32 GB) + RTX 4090 (24 GB), 96 GB RAM |
| **M2 Studio** | macOS Desktop  | M2 Ultra, 192 GB RAM                           |
| **M2 Mini**   | macOS Desktop  | M2 Pro, 32 GB RAM                              |
| **M4 Air**    | macOS Laptop   | M4 MacBook Air, 32 GB RAM, top CPU bin         |

---

## 🐳 Model Hosting

### Standard

* **Docker Model Runner (DMR)** is used across both macOS and Linux for standardized container-based LLM hosting.
* **Benefits**:

  * Unified interface for launching HuggingFace and custom models
  * Easier reproducibility and scaling
  * Fully compatible with vLLM and FastAPI adapters

### High-Performance (AIPC only)

* **vLLM** is used directly on the AIPC for GPU-bound model inference.

  * Model 1 (5090): DeepSeek-Coder 33B (quantized)
  * Model 2 (4090): Yi-34B or Mixtral 8x22B (quantized)

---

## 🔁 Multi-Machine Development

### Node Connectivity

All machines are connected via internal network and use:

* **Redis Streams** for intra-machine messaging
* **JetStream (NATS)** for cross-node communication
* **Consul** for service discovery and config distribution

### Filesystem

* Git-tracked project folders are mirrored on all devices via rsync or git workflows.
* `.tree` files are the primary discovery mechanism for agent and CI execution.

### Command Routing

* OmniNode proxy routes tasks based on:

  * Model availability
  * Node capabilities
  * Role-based restrictions

---

## 📦 Container Layout Standards

Every containerized service must follow this structure:

```
containers/<name>/
├── Dockerfile
├── pyproject.toml
├── config/
│   ├── default/
│   └── environments/
├── src/<package>/
│   ├── api/
│   ├── core/
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/
```

* **Entrypoint**: `app.py` or `main.py`
* **Logging**: Structured JSON logging using shared config
* **Health Checks**: `/health`, `/metrics` endpoints required
* **CI Validation**: Docker path, linting, validation must pass

---

## 🛠️ Local Development Tooling

* **Formatter**: `format_python_file.py` with header/docstring enforcement
* **Validator CLI**: Modular registry-based validator runner
* **Live Test Execution**: Integrated with Foundation test harness
* **Pre-commit Hooks**:

  * Metadata stamping
  * Docstring validation
  * Black/isort/flake8

---

## 🔒 Security Notes

* **No secrets in config files**
* **Vault or env-based** secret injection
* **mTLS or JWT** enforced for all internal APIs
* Local-only models are not exposed outside internal network

---

## 📍 Deployment Considerations

* All containers are deployable individually or as part of a group
* Docker Compose is used locally
* Kubernetes/Consul integration planned for post-MVP
* Canary and rollback-ready config supported via profiles

---

## ✅ Migration Notes

* Ollama is no longer used — fully replaced by Docker Model Runner (DMR)
* This document supersedes:

  * `omninode_infrastructure_checklist.md`
  * `multi_machine_development.md`
  * `readme_launcher.md`

---

This is the source of truth for OmniNode infrastructure and should be kept up to date with any deployment or tooling changes.

---

## 2. Planned/Upcoming Infrastructure and Deployment Specs

- [ ] Kubernetes/Consul production deployment
- [ ] Automated scaling and failover
- [ ] GPU/CPU resource scheduling
- [ ] Multi-cloud and hybrid deployment support
- [ ] Advanced monitoring and alerting integration

---

> For all infrastructure, deployment, and environment requirements, this document is the canonical source of truth.

# Infrastructure Bootstrapping & Registry Sync

> **ONEX v0.1 Canonical Section**
> This section is canonical and covers unique runtime/registry sync logic not found in the main infrastructure specification. For foundational infra, runtime, and security standards, see the main infrastructure and registry docs.

This section captures only the unique, non-duplicative infrastructure logic not already covered in the local model hosting and deployment specification.

---

## 🧩 Registry-Oriented Runtime Sync

* On launch, each machine (M2 Studio, M2 Mini, M4 MacBook Air, AIPC) registers its runtime services to the OmniNode Registry.
* Each runtime service (DMR, vLLM) declares supported models, compute availability, and context window support.
* Runtime address resolution follows this hierarchy:

  ```yaml
  - registry.local.hostname → registry.context.cluster → registry.type.default
  ```

## 🧪 Launch Context & Readme Launcher

* `readme_launcher.py` parses system metadata and initializes runtime configuration.
* Detects host machine profile (AIPC vs Mac) and sets:

  * Model allocation
  * Port and resource binding
  * Registry record injection

## 🌐 Multi-Machine Sync

* Registry entries are time-scoped with TTL and broadcast over the internal message bus.
* Devices are bootstrapped into mesh-aware context groups using tagged configs (e.g., `dev.aipc.node1`).
* Remote registry sync is stubbed but reserved for future federation.

## 🔐 Security Hooks

* On boot, container security enforcement runs:

  * Signature check (if applicable)
  * Network isolation rules (Docker-specific profiles)
  * Optional message bus credentials validation

## 🔍 Observability Stub

* Basic heartbeat logging per machine and per container.
* Future integration points for:

  * Runtime model cost usage
  * Container health and update status
  * Security alerts and intrusion attempts

---

This file is lean by design and assumes foundational infra, runtime, and security standards are defined in other canonical sources like the Local Hosting Spec, Container Standards, and Validator Registry System.
