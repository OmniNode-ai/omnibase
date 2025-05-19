<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 8163d9a9-ed4e-44ff-b66a-87abc96f7c84 -->
<!-- name: configuration.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:00.402713 -->
<!-- last_modified_at: 2025-05-19T16:20:00.402715 -->
<!-- description: Stamped Markdown file: configuration.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: dfb6f565209f7d61a9ec8cd4db2b3b371c8473f2859978a907163846dcdf7b60 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'configuration.md'} -->
<!-- namespace: onex.stamped.configuration.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# OmniBase Configuration System Specification

> **Status:** Canonical
> **Last Updated:** 2025-05-16
> **Purpose:** This document defines the canonical, protocol-aligned configuration system for the OmniBase/ONEX platform. All agent, validator, tool, model, node, and environment configuration requirements, APIs, and best practices are specified here.

---

## Table of Contents

1. [FoundationConfigManager: Protocol-Aligned Configuration System Design](#foundationconfigmanager-protocol-aligned-configuration-system-design)
2. [Planned/Upcoming Configuration Specs](#plannedupcoming-configuration-specs)

---

## 1. FoundationConfigManager: Protocol-Aligned Configuration System Design

This document outlines the finalized design and implementation plan for `FoundationConfigManager`, the centralized, protocol-compliant configuration system used across all OmniNode subsystems—including agents, tools, validators, models, nodes, security policies, and execution environments.

---

### 🧱 Core Concepts

#### 1. Protocol-Aware Namespacing

All configuration keys follow the O.N.E. Protocol hierarchy:

```text
validator.foundation.lint.strict_mode
agent.product.RESEARCH.max_depth
tool.deepseek_coder.context_limit
model.mixtral8x22b.quantization
node.security.firewall.enabled
env.dev.messagebus.retry_policy
```

Supports deep nesting and structured resolution:

```text
validator.<container>.<validator_name>.<setting>
agent.<role>.<mode>.<setting>
tool.<name>.<setting>
model.<name>.<setting>
node.<type>.<name>.<setting>
env.<env_name>.<subsystem>.<setting>
```

#### 2. Layered Configuration Resolution

Configuration is resolved using four prioritized layers:

1. `defaults/` — static default values
2. `config/` — environment YAML/JSON files
3. `ENV` — environment variables
4. `runtime` — programmatic/CLI overrides

Supports fallback and inheritance by context:

```text
container.foundation EXECUTE mode:
  > env.dev.container.foundation
  > env.dev.default
  > container.foundation.default
  > global.default
```

#### 3. Schema Enforcement per Namespace

Each configuration namespace must register a schema:

```python
FoundationConfigManager.register_schema("validator.lint", LintValidatorSchema)
```

Schemas (Pydantic-based) enforce:

* Type safety
* Required fields
* Defaults
* Validation logic

#### 4. Override Tracking & Auditing

Tracks config source, layer, and change history:

```python
config.get("validator.foundation.lint.strict_mode")
# Value: False
# Source: ENV (VALIDATOR_LINT_STRICT_MODE=false)
# Layer: env.dev.container.foundation
```

Built-in audit tools:

* `config.audit_changes()`
* `config.view_resolution_path(key)`
* `config.list_overrides()`

#### 5. Injection & CLI Integration

* DI injection for services and tools
* CLI overrides via `--set key=value`
* Execution profiles: `--profile ci`, `--profile safe_mode`

---

### 🛠️ Implementation Plan

#### FoundationConfigManager APIs

```python
get(key: str, context: Optional[Context])
set(key: str, value: Any, source: str)
register_schema(namespace: str, schema: BaseModel)
load_profile(name: str)
list_overrides()
audit_changes()
view_resolution_path(key: str)
enable_watch_mode()
```

#### Loaders & Backends

* `FileLoader`: YAML/JSON
* `EnvLoader`: ENV keys (e.g., `VALIDATOR_LINT_STRICT_MODE`)
* `InMemoryLoader`: for CLI and runtime
* `RemoteLoader`: planned (e.g., Consul, etcd, Redis)

All implement `BaseConfigLoader`.

#### CLI Commands

```bash
config get <key>
config set <key> <value>
config list
config validate
config export
config audit
config profile <name>
```

---

### 🔐 Security & Compliance

* `EncryptedStr` for secure values
* Log redaction and masking
* RBAC for config editing (future)
* CI check: `validate_configs.py`
* Profile fallback for disaster recovery

---

### 📈 Future Enhancements

* Remote sync via Consul, Vault, or S3
* Live reload with `watchdog`
* Visual dependency graph
* GUI editor with profile switcher
* Config diffing, rollback, and snapshots

---

This system is required for all production agents, validator nodes, tools, and runtime services. Contributions must register a schema and ensure fallback compatibility. CI validation and runtime traceability are mandatory for all configs beginning MVP Milestone 2.

---

## 2. Planned/Upcoming Configuration Specs

- [ ] Remote configuration sync and secrets management
- [ ] Profile-based config switching and live reload
- [ ] Visual config editor and dependency graph
- [ ] Config diffing, rollback, and audit trail

---

> For all configuration, settings, and environment requirements, this document is the canonical source of truth. 
