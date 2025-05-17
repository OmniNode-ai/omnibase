# OmniBase Metadata Specification

> **Status:** Canonical (ONEX v0.1 Supersedes)  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16
> **Precedence:** This document incorporates and is governed by the ONEX v0.1 protocol and metadata specifications. Any conflicting or missing details in previous versions are overridden by ONEX v0.1.

---

## Overview

Every OmniBase component—validators, tools, test cases, data artifacts—must include a canonical metadata block. Metadata enables registry indexing, dependency resolution, version enforcement, and lineage tracking via UUID-based graphs. This document defines the canonical format, field semantics, dependency schema, lineage/federation, and validation mechanisms.

---

## Canonical Metadata Block & Field Semantics

### Canonical Metadata Block (YAML)

```yaml
# === OmniNode:Metadata ===
metadata_version: "0.2.1"
schema_version: "1.1.0"
uuid: "123e4567-e89b-12d3-a456-426614174000"
name: "example_validator"
namespace: "foundation.script.validate"
version: "0.1.0"
type: "validator"
entrypoint: "python_validate_example.py"
protocols_supported: ["O.N.E. Core v0.1"]
author: "OmniNode Team"
owner: "foundation-team"
created_at: "2025-05-12T12:00:00+00:00"
last_modified_at: "2025-05-13T10:00:00+00:00"
parent_id: "uuid_of_root_validator_metadata_block"
child_ids: ["uuid_of_child1_metadata", "uuid_of_child2_metadata"]
dependencies:
  - id: "tool_fix_format_headers_uuid"
    type: "tool"
    version_spec: ">=0.1.0,<0.2.0"
    required: true
  - id: "data_example_uuid"
    type: "data_artifact"
    version_spec: "1.0.0"
    required: false
tags: ["canary", "pre-commit", "schema-validation"]
lifecycle: "canary"
status: "active"
idempotent: true
description: "A canonical example of a validator metadata block."
# === /OmniNode:Metadata ===
```

### Field Semantics

| Field                | Description                                                       |
|---------------------|-------------------------------------------------------------------|
| `uuid`              | Globally unique identifier (UUIDv4)                               |
| `name`              | Human-readable label                                              |
| `namespace`         | Hierarchical scope (e.g. `foundation.script.validate`)            |
| `version`           | Component version (SemVer required)                               |
| `entrypoint`        | Path to Python script or module                                   |
| `type`              | One of: validator, tool, test, artifact, etc.                     |
| `protocols_supported` | Which protocol versions this component conforms to              |
| `created_at`        | RFC 3339 timestamp                                                |
| `last_modified_at`  | RFC 3339 timestamp                                                |
| `parent_id`         | UUID of parent metadata (optional)                                |
| `child_ids`         | List of UUIDs of derived components (optional)                    |
| `dependencies`      | Referenced UUIDs, with version specifiers and type                |
| `tags`              | Filterable tags for execution stages, domain, lifecycle, etc.     |
| `lifecycle`         | One of: canary, experimental, stable, deprecated                  |
| `status`            | One of: active, inactive, pending_review                          |
| `idempotent`        | If true, function produces same output for same input             |
| `description`       | Optional freeform description                                     |

## Protocol-Driven Stamping and Validation

- The ONEX Metadata Stamper is implemented as a protocol-driven, fixture-injectable engine. All stamping and validation logic is defined by Python Protocols, enabling extensibility, testability, and context-agnostic execution.
- The stamper engine injects metadata blocks into files according to the canonical schema defined above, ensuring compliance with all required and recommended fields.
- All dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture, never hardcoded.
- The protocol-driven design enables registry-driven, context-agnostic validation and stamping in CI, pre-commit, and developer workflows.
- See [docs/protocols.md](../protocols.md), [docs/tools/stamper.md](../tools/stamper.md), and [docs/testing.md](../testing.md) for details on protocol-driven stamping and validation.

---

## Dependency Schema & Resolution

Each entry in `dependencies:` includes:
- `id`: UUID of dependency
- `type`: e.g., `tool`, `validator`, `data_artifact`
- `version_spec`: SemVer-compatible range (e.g., `>=0.1.0,<0.2.0`)
- `required`: Boolean

### Dependency Resolution
- Uses a modified Pubgrub algorithm
- Supports SemVer-compatible version ranges
- Conflicts yield descriptive errors
- Local overrides for testing supported
- Retains resolved versions in execution report

### Graph Semantics
- **Node:** Any component with a UUID
- **Edge:** `depends_on`, `inherits_from`, or `generated_by`
- **Use cases:** Lineage tracking, impact analysis, caching

---

## Lineage & Federation

### Registry Federation
OmniBase supports a federated registry model for distributed, multi-org collaboration.

#### Federation Modes
| Mode         | Description                                      |
|--------------|--------------------------------------------------|
| Centralized  | One authoritative registry, local caches         |
| Hierarchical | Parent-child registries, policy-controlled sync  |
| Mesh         | Peer-to-peer sync across trusted registries      |

Default: centralized → optional mesh with ACLs

#### Sync Patterns
- Pull-only: local registry pulls from upstream (read-only)
- Push: changes propagate to remote registries (if permitted)
- Partial sync: filter by tags, lifecycle, namespace
- Full sync: entire DAG of referenced entries

#### Security Controls
- Signature-based verification of remote metadata
- Trust roots for federation
- Version pinning of critical components
- Audit logs of federation events
- Optional sandboxing of newly pulled components

### Metadata Lineage Graph
Each metadata block supports:
- `parent_id`: single upstream (inheritance)
- `child_ids`: list of known descendants
- `dependencies`: typed, versioned edges
- `produced_by`: execution UUID or agent ID

Lineage graph forms a directed acyclic graph (DAG).

#### Use Cases
- Trace validator ancestry for debugging
- Replay execution history of toolchains
- Visualize test case evolution
- Filter components derived from agent-generated roots
- Detect component drift via lineage comparison

#### Lineage Visualizer (Planned)
CLI and web-based DAG viewer:
```bash
omnibase visualize lineage <uuid>
omnibase lineage diff --base <uuid1> --compare <uuid2>
```
Supports:
- Node coloring by lifecycle
- Edge labeling by dependency type
- Breadcrumb traces

---

## CLI/Validation

CLI command:
```bash
omnibase validate metadata <path_or_uuid>
```
Performs:
- Schema validation
- Type enforcement
- Version rule compliance
- Dependency resolution checks
- Graph cycle detection

Other CLI examples:
```bash
omnibase inspect metadata validator_abc
omnibase visualize dependencies tool_xyz
```

Validation is enforced in CLI and CI. Non-conforming entries are rejected at the registry level.

---

## Versioning Contracts

| Field                | Format         | Rule                                  |
|---------------------|----------------|----------------------------------------|
| `metadata_version`  | SemVer         | Same major + minor = compatible        |
| `schema_version`    | SemVer         | Same major = compatible                |
| `version` (component) | SemVer       | Used in dependency resolution          |

Incompatibilities trigger warnings or blocks depending on severity.

Version compatibility is enforced via:
```python
def check_compat(local: str, remote: str) -> Compatibility:
    # Major mismatch = incompatible
    # Minor mismatch = warning
    # Patch mismatch = compatible
```

---

## Planned Enhancements
- [ ] Lock metadata schema version `0.2.1`
- [ ] Implement graph extraction utilities
- [ ] Build visualizer for metadata graph
- [ ] Add impact analysis and downstream queries
- [ ] Metadata diff viewer
- [ ] Inferred metadata from component introspection
- [ ] Metadata explorer UI
- [ ] Pydantic-backed schema generation for static validation
- [ ] Lineage tree visualizer for docs
- [ ] Trust level annotations and audit chain
- [ ] Custom metadata injection for agents
- [ ] Federated sync agent and ACL config
- [ ] Lineage graph extract + diff tool
- [ ] Visualization engine (CLI first)
- [ ] Trust and signature enforcement CLI
- [ ] Provenance-aware execution logs

---

## References & Deep Dives
- See `docs/metadata/dependency.md` for advanced dependency resolution details
- See `docs/metadata/lineage.md` for federation and lineage deep dive
- See `docs/metadata/validation.md` for validation and CLI usage

# ONEX v0.1 Canonical Metadata Block Specification

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

## ONEX Metadata Block Specification (v0.1)

> **Note:** This document defines the canonical metadata block **schema** for ONEX nodes. It complements the existing `OmniNode Metadata Stamper Specification`, which describes how metadata blocks are injected, parsed, and validated across files and runtimes. This document focuses on the field structure, trust metadata, registry alignment, and CI compatibility.

### Overview

This document defines the required format, fields, and usage conventions for ONEX metadata blocks. Metadata blocks are used to stamp all ONEX nodes with introspectable identity, versioning, trust, and execution attributes.

---

### 🧾 Required Format

Metadata blocks must be encoded as YAML and stored in one of two places:

* In a standalone `metadata.yaml` inside the node folder
* Inline as a comment block at the top of `code.py` (optional, tools only)

Comment-based blocks must use language-specific delimiters:

* Python: `# === OmniNode:Metadata === ... # === /OmniNode:Metadata ===`
* JS/TS: `/* === OmniNode:Metadata === ... === /OmniNode:Metadata === */`

---

### ✅ Minimum Required Fields

```yaml
metadata_version: 0.1
id: validator.check.namegen
namespace: omninode.validators.check
version: 0.3.4
entrypoint: code.py
protocols_supported:
  - ONEX v0.1
```

---

### 🧩 Recommended Additional Fields

```yaml
category: validation
status: active
lifecycle: active | frozen | batch-complete
trust_level: signed
signed_by: omninode:shane
signature_alg: ed25519
fingerprint: sha256:abc...
author: Jonah Gray
description: Checks namegen formatting consistency
```

---

### 🔧 Execution Fields

```yaml
runtime_constraints:
  sandboxed: true
  privileged: false
  requires_network: false
  requires_gpu: false
```

---

### 🧪 Test and CI Metadata

```yaml
test_suite: true
test_status: passing
coverage: 92.3
ci_url: https://ci.omninode.dev/validator.check.namegen/status
```

---

### 🔐 Trust Metadata

```yaml
trust:
  level: verified
  signer: omninode.root
  expires_at: 2025-12-31T00:00:00Z
  federation_scope: [zone.core, zone.partner.alpha]
```

---

### 📦 Distribution + Registry Fields

```yaml
registry_url: https://registry.omninode.dev/validator.check.namegen
docs_url: https://docs.omninode.dev/validator.check.namegen
source_url: https://github.com/omninode/validator-check-namegen
```

---

### 🔁 Metadata in CI and CLI

```bash
onex lint --require-metadata
onex metadata validate ./nodes/validator.check.namegen/metadata.yaml
onex publish --with-metadata
```

---

**Status:** This is the canonical metadata block schema specification for all ONEX nodes. All node folders must include a valid `metadata.yaml` to be CI- and registry-compliant.

---

> **Note:** All ONEX v0.1 sections below are canonical. Any previous or conflicting details are explicitly superseded.

# ONEX v0.1 Canonical Enforcement and Linting Rules

> **This section is canonical and supersedes any conflicting details below.**

## Lint Rules and Enforcement Policies
- No direct instantiation of dependencies (E001)
- All nodes/tools must have a valid metadata block (E002)
- Registry bypass is forbidden (E003)
- Naming must follow ONEX standards (E004)
- No inline fixture definitions (E005)
- Lifecycle/status must be declared (E006)

## Validation Targets
- All validators, tools, plugins, and tests
- YAML-based registries
- Entrypoint Python files and test cases

## CLI Integration
- `onex lint`, `onex lint --strict`, `onex lint --rules E001,E002,E006`

## Lint Report Format (Example)
```json
{
  "file": "validators/validate_name.py",
  "rules_failed": ["E001", "E002"],
  "errors": [
    {"rule": "E001", "message": "Logger instantiated directly"},
    {"rule": "E002", "message": "Missing metadata block"}
  ]
}
```

## CI Hook Usage
- CI runs `onex lint --strict`
- All errors must be resolved before merge
- Summary shown on PR and exported with batch run result

**Status:** Canonical lint rule and enforcement policy layer for ONEX components, merged from validator pitfalls and standards checklists.

# ONEX v0.1 Canonical Logging and Observability

> **This section is canonical and supersedes any conflicting details below.**

## Log Entry Schema
- All logs must be JSON-serializable and follow this schema:
  - timestamp (ISO 8601 UTC, required)
  - level (required)
  - message (required)
  - logger (required)
  - agent_id, execution_id, context, metadata, trace_id (optional)

## Example Log Entry
```json
{
  "timestamp": "2025-05-01T12:34:56.789Z",
  "level": "info",
  "message": "Validator completed successfully.",
  "logger": "foundation.validator.namegen",
  "agent_id": "agent-uuid-001",
  "execution_id": "run-42",
  "context": {"file": "namegen.py", "line": 88},
  "metadata": {"protocol_version": "v0.1", "state": "frozen"},
  "trace_id": "abc-123-xyz"
}
```

## Trust Logging Requirements
- All validators must include trust-state metadata in logs
- Batch/frozen node executions must emit lifecycle tags
- Signature verification errors must emit severity `error` and include offending node ID

## Logger Injection Pattern
- All loggers must be passed via constructor DI
- Never call `logging.getLogger()` in business logic

## Batch Run Logging
- Logs must include batch ID if running as part of orchestrated CI run
- Support streaming to JetStream, local file, and `onex report`

## CI and Observability Integration
- `onex run` emits log streams or bundles per batch
- CI uploads structured log archive to observability backend
- Errors are parsed for trust violations, lint compliance, signature/auth failures

**Status:** Canonical observability and structured logging standard for ONEX-compatible execution and validation tooling.

# ONEX v0.1 Canonical Security and Data Redaction Policy

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

## ONEX Security and Data Redaction Policy (v0.1)

### Overview

This document defines security enforcement, redaction rules, and agent safety policies for ONEX environments. All logs, configs, and agent inputs/outputs must comply with these guidelines to prevent PII leaks, protect secrets, and ensure system integrity.

---

### 🔐 Schema-Validated Execution (Mandatory)

All ONEX agents and tools must:

* Declare a schema for inputs and outputs
* Use a schema guard for runtime validation
* Log invalid input attempts

```python
def execute(payload):
    validated = InputSchema(**payload)
    return tool(validated)
```

---

### 🧼 Redaction & PII Masking

All logs must redact sensitive content.

#### ✅ Redaction Rules

| Pattern             | Masked Output |
| ------------------- | ------------- |
| Email addresses     | `[REDACTED]`  |
| API keys/tokens     | `[MASKED]`    |
| Secrets from `.env` | `[SECRET]`    |

#### ✅ Log Sample

```json
{
  "agent": "coder",
  "trace_id": "abc-123",
  "inputs": {
    "user_email": "[REDACTED]",
    "api_key": "[MASKED]"
  }
}
```

---

### 🔐 Secret Handling

* Use `EncryptedStr` or equivalent to annotate secret-bearing fields
* Inject secrets via Doppler, Vault, or environment variables
* Never commit raw secrets to config files
* Ensure redacted display in:

  * CLI
  * Debug logs
  * API outputs

---

### 📉 Rate Limiting

All exposed endpoints must implement protection:

* `/agent/execute`, `/config/set`, and `/prompt/invoke` must:

  * Use Traefik rate limit middleware or equivalent
  * Block after N failed attempts
  * Log abuse with trace ID and IP metadata

---

### 🛡️ Validation Testing

Test cases must cover:

* Schema rejection for malformed inputs
* Redaction correctness
* Secret omission in debug mode

---

### 📖 Documentation & CI

* `SECURITY_PRACTICES.md` must describe redaction + masking rules
* CI should include:

  * Redaction linter for logs
  * Schema validation unit tests
  * Secret injection stubs for test environments

---

**Status:** These redaction and execution safety standards are required for all ONEX agents, tools, and services. Violations are treated as critical CI failures and must be addressed before deployment.

---

> **Note:** All ONEX v0.1 sections below are canonical. Any previous or conflicting details are explicitly superseded.

# Canonical Metadata Stamping and Enforcement Requirements

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

## Universal Metadata Stamping & Enforcement

- **Requirement:** All files in the foundation must include a valid metadata header (namespace, access, tags, etc.).
- **Enforcement:** A language-agnostic stamping tool runs on every commit and in CI, blocking any file that lacks a valid metadata block.
- **CI/Pre-commit Integration:** The stamping tool is integrated into pre-commit and CI pipelines, ensuring compliance before merge.
- **Static, Metadata-Driven Discovery:** Registration and discovery are handled via static metadata, not runtime decorators. This enables language-agnostic enforcement, static analysis, dashboards, and registry population.
- **Metadata Integrity:** Metadata integrity checks, semantic validation, and linting are required. Contributor templates must be provided for community submissions.

**Immediate Benefits:**
- Consistent metadata across all files
- Language-agnostic enforcement
- Enables static analysis, dashboards, and registry population

---

## Planned Enhancements (Summary)
- Dynamic registry/crawler for all entities using metadata
- Unified query API by type, group, tag, etc.
- Hot reload/sync on file changes or commands
- Schema and required field validation
- Cross-type queries (e.g., "all validators in group 'security'")
- Auto-generated docs and dashboards from metadata
- Directory-level metadata validation
- Metadata change tracking and versioning
- Feedback loops for metadata usage
- Security and privacy filtering for public metadata
- Validator dependencies and CI/testing profiles via metadata
- Live updates and streaming of metadata/validation results
- Policy enforcement and access/compliance rules via metadata
- Automated migration tools for legacy metadata
- Agent-driven metadata editing and provenance/audit trails
- Metadata-as-code enforcement policies (versioned YAML/Python with PR checks)

---

> All validator registration, enforcement, and discovery is now metadata-driven and governed by this specification. Future validator types and enforcement logic will be defined by metadata schemas and stamping.

# OmniNode Traceability & Metadata System (v0.3)

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

This section consolidates the design goals, stamping standards, and traceability architecture that underpin the OmniNode execution model. It defines how every tool, script, validator, and agent-related file within OmniBase is discoverable, inspectable, and reproducible via metadata blocks.

---

## ✨ Purpose

To ensure every file within the OmniNode ecosystem can:
- Be programmatically traced across executions
- Expose core metadata fields for registry ingestion
- Support audit, replay, and provenance operations
- Remain language-agnostic and CI-compliant

---
