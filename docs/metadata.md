<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: a8bb09b3-09b8-452b-82c1-63977216b030 -->
<!-- name: metadata.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:02.429855 -->
<!-- last_modified_at: 2025-05-19T16:20:02.429858 -->
<!-- description: Stamped Markdown file: metadata.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 2de5aefb1bf0a0d4805292e8a3a16c30b4abc8625b6cd6b7125cde586df986d9 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'metadata.md'} -->
<!-- namespace: onex.stamped.metadata.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# OmniBase Metadata Specification

> **Status:** Canonical (ONEX v0.1 Supersedes)  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-06-14
> **Precedence:** This document incorporates and is governed by the ONEX v0.1 protocol and metadata specifications. Any conflicting or missing details in previous versions are overridden by ONEX v0.1.

---

## Overview

Every OmniBase component—validators, tools, test cases, data artifacts—must include a canonical metadata block. Metadata enables registry indexing, dependency resolution, version enforcement, and lineage tracking via UUID-based graphs. This document defines the canonical format, field semantics, dependency schema, lineage/federation, and validation mechanisms.

---

## Canonical Metadata Block & Field Semantics

### Canonical Metadata Block (YAML)

```yaml
# === OmniNode:Metadata ===
metadata_version: "0.1.0"
protocol_version: "1.0.0"
schema_version: "1.1.0"
uuid: "123e4567-e89b-12d3-a456-426614174000"
name: "example_validator"
namespace: "foundation.script.validate"
version: "0.1.0"
author: "OmniNode Team"
owner: "foundation-team"
copyright: "Copyright OmniNode"
created_at: "2025-05-12T12:00:00Z"
last_modified_at: "2025-05-13T10:00:00Z"
description: "A canonical example of a validator metadata block."
state_contract: "state_contract://default"
lifecycle: "active"
hash: "0000000000000000000000000000000000000000000000000000000000000000"
entrypoint:
  type: "python"
  target: "python_validate_example.py"
runtime_language_hint: "python>=3.11"
meta_type: "tool"
tags: ["canary", "pre-commit", "schema-validation"]
capabilities: []
protocols_supported: ["O.N.E. Core v0.1"]
base_class: []
dependencies: []
inputs: []
outputs: []
environment: []
license: "MIT"
signature_block: null
x_extensions: {}
testing: null
os_requirements: []
architectures: []
container_image_reference: null
compliance_profiles: []
data_handling_declaration: null
logging_config: null
source_repository: null
# === /OmniNode:Metadata ===
```

### Field Semantics (matches NodeMetadataBlock)

| Field                    | Type         | Description                                                      |
|--------------------------|--------------|------------------------------------------------------------------|
| metadata_version         | str          | Metadata schema version (SemVer)                                 |
| protocol_version         | str          | Protocol version (SemVer)                                        |
| schema_version           | str          | Node schema version (SemVer)                                     |
| uuid                     | str (UUID)   | Globally unique identifier (UUIDv4)                              |
| name                     | str          | Human-readable label                                             |
| namespace                | str          | Hierarchical scope (e.g. `foundation.script.validate`)           |
| version                  | str          | Component version (SemVer)                                       |
| author                   | str          | Author of the component                                          |
| owner                    | str          | Owning team or org                                               |
| copyright                | str          | Copyright statement                                              |
| created_at               | str (ISO8601)| RFC 3339 timestamp                                              |
| last_modified_at         | str (ISO8601)| RFC 3339 timestamp                                              |
| description              | str          | Optional freeform description                                    |
| state_contract           | str          | State contract URI                                               |
| lifecycle                | Enum         | One of: active, draft, deprecated, etc.                         |
| hash                     | str          | Canonical content hash (SHA-256, 64 hex chars)                   |
| entrypoint               | object       | Entrypoint block: `{type: str, target: str}`                     |
| runtime_language_hint    | str          | Language/version hint (e.g. `python>=3.11`)                      |
| meta_type                | Enum         | One of: tool, validator, plugin, etc.                            |
| tags                     | list[str]    | Filterable tags                                                  |
| capabilities             | list[str]    | Capabilities provided                                            |
| protocols_supported      | list[str]    | Supported protocol versions                                      |
| base_class               | list[str]    | Base classes (if any)                                            |
| dependencies             | list         | Dependency blocks                                                |
| inputs                   | list         | Input blocks                                                     |
| outputs                  | list         | Output blocks                                                    |
| environment              | list[str]    | Environment requirements                                         |
| license                  | str          | License string                                                   |
| signature_block          | object/null  | Signature block (optional)                                       |
| x_extensions             | dict         | Arbitrary extensions                                             |
| testing                  | object/null  | Testing block (optional)                                         |
| os_requirements          | list[str]    | OS requirements                                                  |
| architectures            | list[str]    | Supported architectures                                          |
| container_image_reference| str/null     | Container image reference (optional)                             |
| compliance_profiles      | list[str]    | Compliance profiles                                              |
| data_handling_declaration| object/null  | Data handling declaration (optional)                             |
| logging_config           | object/null  | Logging config (optional)                                        |
| source_repository        | object/null  | Source repository info (optional)                                |

- **Enums**: `lifecycle`, `meta_type`, and some nested fields are enums. See the canonical model for allowed values.
- **Entrypoint**: Always a structured block, not a string.
- **No longer canonical**: `type`, `status`, `idempotent`, `parent_id`, `child_ids` are not part of the canonical model.

---

## Canonical Block Delimiters

All metadata blocks **must** be wrapped in the following comment delimiters (file-type-specific):

- Python: `# === OmniNode:Metadata ===` ... `# === /OmniNode:Metadata ===`
- YAML: `# === OmniNode:Metadata ===` ... `# === /OmniNode:Metadata ===`
- JSON/Markdown: ``

---

## Canonical Normalization & Serialization

- All string fields are normalized to empty string if null/None.
- All list fields are normalized to empty list if null/None.
- All enums are serialized as their `.value` (not as objects).
- YAML serialization is deterministic: sorted keys, block style, explicit start/end, UTF-8, normalized line endings.
- Volatile fields (`hash`, `last_modified_at`) are replaced with protocol placeholders during hash computation.
- All normalization and serialization is enforced by the engine, not the handler.

---

## Canonical Hash Computation

- The canonical hash is computed by:
  1. Normalizing the file body (excluding the metadata block).
  2. Serializing the metadata block with protocol placeholders for `hash` and `last_modified_at`.
  3. Concatenating the canonicalized block and normalized body.
  4. Hashing the result with SHA-256.
- This guarantees idempotency and hash stability across repeated stamps.

---

## Layered Validation & Protocol Compliance

- **Handler validation**: File-type-specific syntax, schema, and block extraction.
- **Engine validation**: Protocol-level field presence, canonical formatting, uniqueness, block placement, hash/timestamp consistency, idempotency.
- **All validation is protocol-driven and type-enforced.**
- **All stamping, normalization, and validation logic is centralized in the engine.**

---

## Protocol-Driven, Type-Enforced, Registry-Driven Architecture

- All stamping and validation logic is defined by Python Protocols, using strong typing and Pydantic models.
- All protocol interfaces use the canonical `TYPE_CHECKING`/forward reference import pattern.
- All dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture, never hardcoded.
- The protocol-driven design enables registry-driven, context-agnostic validation and stamping in CI, pre-commit, and developer workflows.

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
