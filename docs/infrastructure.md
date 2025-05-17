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