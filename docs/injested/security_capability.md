# OmniBase Security & Capability Model

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

All agent-generated code, remote components, and dynamic tools must execute within a sandboxed environment governed by a strict capability-based security model.

---

## Security Principles

- **Deny by default:** No capabilities are granted unless explicitly declared.
- **Capability granularity:** Access is defined per operation, resource, and context.
- **Sandbox isolation:** Runtime enforcement via technologies like gVisor.
- **Traceability:** All access decisions are logged and correlated with execution spans.

---

## Capability Types

| Type               | Example Resource         | Use Case                           |
|--------------------|--------------------------|-------------------------------------|
| `FILE_READ`        | `/src/foo.py`            | Validator scans a file              |
| `FILE_WRITE`       | `/tmp/output.json`       | Tool generates output               |
| `NETWORK_CONNECT`  | `api.external.com:443`   | Fetch data from external service    |
| `DATABASE_READ`    | `registry.db`            | Read artifact metadata              |
| `ARTIFACT_WRITE`   | `digest:abc123`          | Store a new artifact in CAS         |
| `EXTERNAL_COMMAND` | `black`, `pytest`        | Run external CLI tools              |
| `SECRET_ACCESS`    | `OMNIBASE_API_KEY`       | Read credentials from vault         |

---

## Capability Declaration

Defined in:

- ExecutionContext setup
- Metadata (`capabilities_required`)
- Registry policies

---

## Enforcement Layers

1. **Static Analysis**
   - Validate declared needs against known policies
2. **Runtime Gate**
   - Check against granted capabilities
3. **Sandbox Interface**
   - Enforce isolation (e.g., file system, network, process)

---

## Capability Objects

```python
cap = Capability(CapabilityType.FILE_READ, "/src/config.yaml")
context.check_capability(cap)
```

Pattern matching supports glob/wildcards.

---

## Security Sandbox

- **Backend:** gVisor (or similar OCI-compatible container sandbox)
- **Isolation:** Filesystem, network, process table, PID namespace
- **Secrets:** Injected via ephemeral mount; destroyed after use
- **Runtime:** Capabilities enforced via context object passed into all executions

---

## Permission Models

- Registry-level: who can register/update/retire components
- Execution-level: what each function can access/do
- Audit trail: automatic metadata recording for every granted capability

---

## Planned Security Features

- [ ] Formal capability schema in metadata
- [ ] Cedar-based policy language for grants
- [ ] Audit log viewer with filter by capability or executor
- [ ] Dynamic request/review flow for agent-granted capabilities

---

> Every action has a gate. Every gate requires a key. OmniBase enforces this—systematically.