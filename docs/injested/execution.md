# OmniBase Registry & Execution Protocols

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

All execution in OmniBase is registry-driven. Tools, validators, and test cases are registered via UUID-indexed metadata blocks and executed through a standard function signature protocol.

---

## Function Signature Protocol

    def run(input: Artifact[T], context: ExecutionContext) -> Result[U]

This pattern enables:
- Stateless, reproducible execution
- Runtime orchestration
- Agent compatibility
- Source-agnostic substitution

An optional async variant is also supported:

    async def run(...) -> Result[U]

---

## Registry Types

| Registry           | Description                            |
|--------------------|----------------------------------------|
| `ValidatorRegistry` | Stores validator functions             |
| `ToolRegistry`      | Stores transformers/mutators           |
| `TestCaseRegistry`  | Stores declarative test cases          |

Each registry supports:

- Query by tag, version, input/output type
- Metadata validation
- UUID-based lookup
- Version-aware dependency resolution

---

## Registry Backing Store

- **Authoritative store:** PostgreSQL
- **Local cache:** Write-through file-based mirror
- **Sync behavior:** Periodic, configurable
- **Offline mode:** Read-only with TTL-limited validity

---

## Version Compatibility Matrix

| Component Type | Field                   | Rule                  |
|----------------|--------------------------|------------------------|
| Protocol       | `__protocol_version__`   | Match major version   |
| ABC            | `SCHEMA_VERSION`         | Match major version   |
| Registry Entry | `version`                | Match SemVer spec     |
| Metadata       | `metadata_version`       | Match major + minor   |

---

## Execution Context

All executions receive an `ExecutionContext` object. It provides:

- Access to configuration parameters
- Logging/tracing facilities
- Capability checking
- Correlation ID for observability

---

## Dynamic Execution Sources

Functions may originate from:

- Hardcoded Python modules
- Agent-generated code snippets
- External processes wrapped in a conforming adapter

All must conform to the protocol contract.

---

## CLI Commands (Examples)

    omnibase list validators --tag canary
    omnibase run tool fix_headers --input some_file.py
    omnibase inspect metadata tool_x_uuid
    omnibase validate metadata path/to/file.metadata.yaml
    omnibase compose pipeline --from tool1 --to tool2 --to validator3

---

## Hot Reload & Agent Registration

Agent-generated components can be registered at runtime if:

- Metadata is present and schema-valid
- Execution sandbox passes security policies
- Entry point adheres to protocol signature

---

## Future Considerations

- [ ] Add registry visualizer for component lineage
- [ ] Extend registry to support federated lookup
- [ ] Add mutation logs and audit trails per entry
- [ ] Expose GraphQL and CLI APIs for registry queries

---

> The registry is the source of truth. If it’s not in the registry, it doesn’t exist.