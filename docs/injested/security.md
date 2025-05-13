# OmniBase Security & Sandboxing

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase must safely execute both hardcoded and agent-generated functions. This requires strict sandboxing, input validation, permission enforcement, and auditability.

The system uses a capability-based security model and supports container-level isolation for untrusted code paths.

---

## Execution Trust Levels

| Level        | Source              | Isolation Mechanism   | Permission Scope          |
|--------------|---------------------|------------------------|---------------------------|
| Trusted      | OmniNode-authored   | Direct execution       | Full access (governed)    |
| Semi-trusted | Agent-generated     | Sandboxed (gVisor)     | Limited by capabilities   |
| Untrusted    | External components | Isolated subprocess    | Minimal + reviewed config |

---

## Sandboxing Strategy

- **Sandbox Runtime:** `gVisor` (for Linux) or future WASM container support
- **Isolation Layer:** Restricted filesystem, network, and syscall surfaces
- **Secrets Handling:** Injected via tempfs, ephemeral, never stored
- **Timeouts:** Execution hard-capped by orchestrators
- **Retry Behavior:** Controlled by `idempotent` flag in metadata

---

## Capability System

Capabilities define **what** a function is allowed to do and **with what** resource.

### Example Capabilities

| Type              | Resource Example            |
|-------------------|-----------------------------|
| FILE_READ         | `src/*.py`                  |
| NETWORK_CONNECT   | `api.github.com:443`        |
| DATABASE_WRITE    | `omnibase.registry`         |
| SECRET_ACCESS     | `registry_writer_token`     |
| ARTIFACT_WRITE    | `uuid-of-output-artifact`   |

### Enforcement

At runtime, each function is wrapped with a `CapabilityContext` which validates access checks against a `CapabilitySet`.

Violations raise `CapabilityError`.

---

## Security Error Taxonomy

    class SecurityError(OmniBaseError): ...
    class SandboxViolationError(SecurityError): ...
    class CapabilityError(SecurityError): ...
    class SecretAccessError(SecurityError): ...
    class ExternalCommandError(SecurityError): ...

All security violations are reported in structured logs and span traces.

---

## Policy Model

Policies govern:

- What types of functions are allowed to run
- Under what lifecycle phase (e.g., no `experimental` in `ci`)
- What capabilities can be requested per registry group
- Whether dynamic grant requests (e.g., by agents) are permitted

Future support: **Cedar-based policy language**

---

## CLI Enforcement

When executing functions via CLI:

    omnibase run tool fix_headers --input file.py

Orchestrator resolves:
- Registry entry
- Metadata
- Required capabilities

If `--require-sandbox` is set or agent-generated logic is detected, sandboxing is enabled and enforced.

---

## Threat Model Document

The dedicated security design is maintained at:

    docs/security/threat_model.md

It includes:
- Attack surface analysis
- Isolation guarantees
- Runtime boundaries
- Secret lifecycle diagrams
- Agent misbehavior scenarios
- Audit and forensics strategy

---

## Next Steps

- [ ] Finalize capability schema and DSL
- [ ] Implement gVisor-based executor prototype
- [ ] Integrate with orchestrator lifecycle stages
- [ ] Complete threat model and penetration testing checklist

---

> Any agent that can mutate your system must first prove it can’t destroy it.