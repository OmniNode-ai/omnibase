# OmniBase Security, Sandbox, and Capability System

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase components, especially agent-generated code, must be executed under strict security constraints. The system combines sandboxing, a capability-based access model, and runtime policy enforcement.

---

## Sandbox Architecture

OmniBase will support execution sandboxing via:

- **gVisor**: Container isolation
- **Filesystem restrictions**: Temporary volumes, no host mounts
- **Network controls**: Egress/ingress restrictions
- **Capability context**: Permission tokens per execution

---

## Capability Types

```python
class CapabilityType(Enum):
    FILE_READ
    FILE_WRITE
    NETWORK_CONNECT
    DATABASE_READ
    DATABASE_WRITE
    REGISTRY_READ
    REGISTRY_WRITE
    ARTIFACT_READ
    ARTIFACT_WRITE
    EXTERNAL_COMMAND
    SECRET_ACCESS
```

Each runtime execution receives a `CapabilitySet` object, which is checked before any privileged action.

---

## Capability Matching

```python
cap = Capability(type=FILE_READ, resource="src/schema/*.py")
capset.has_capability(cap)
```

Supports:

- Wildcards (`*`, `?`) in resource
- Condition-based matching (e.g. context-dependent secrets)

---

## Enforcement Context

Validators and tools receive a `CapabilityContext` injected via `ExecutionContext`:

```python
ctx.check_file_read("tmp/test.json")
ctx.check_registry("validators", "read")
```

Raises `CapabilityError` on violation.

---

## Security Enforcement in CI

- `flake8-omnibase` blocks access to disallowed imports
- Registry only accepts metadata with allowed capabilities
- Runtime execution is rejected if required capabilities are not granted

---

## Threat Model Summary

| Threat                  | Mitigation                                           |
|-------------------------|------------------------------------------------------|
| Arbitrary code execution | gVisor sandbox, capability gating                   |
| Secret exfiltration     | Secret injection via ephemeral FS, no env vars      |
| Registry poisoning      | Metadata validation, signature enforcement planned   |
| Dependency attacks      | Locked version specs, provenance tracking            |

---

## Planned Deliverables

- [ ] `docs/security/threat_model.md`
- [ ] Capability policy engine (Cedar-like language)
- [ ] CLI for reviewing granted capabilities
- [ ] Metadata-lint that rejects unsafe default grants
- [ ] Traceable denial logs and sandbox escape detection

---

> Agents may write code, but they can’t run wild. Capabilities are the leash.