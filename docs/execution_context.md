# OmniBase ExecutionContext, Capability, and Security Protocols

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

> **Note:** This document is a technical reference for the ExecutionContext protocol and capability enforcement. It is closely related to the [Protocols Spec](./protocols.md) and [Security Spec](./security.md).

---

## ExecutionContext Protocol

`ExecutionContext` provides the shared runtime environment for all tools, validators, and tests.

### Responsibilities

- Provide access to configuration
- Expose secrets or capabilities in a controlled way
- Log execution details
- Trace correlation ID for observability
- Enforce capability-based permissions

### Protocol Definition

See also: [Protocols Spec](./protocols.md) for canonical interface definitions.

```python
class ExecutionContext(Protocol):
    __protocol_version__ = "1.0.0"

    def get_config(self, key: str, default: Any = None) -> Any: ...
    def get_capability(self, name: str) -> bool: ...
    def get_correlation_id(self) -> UUID: ...
    def get_logger(self, name: Optional[str] = None): ...
```

---

## Capabilities

Capabilities represent fine-grained, declarative permissions granted to components at runtime. See [Security Spec](./security.md) for the full capability model.

### Example Capability Types

| Type             | Example Resource     |
|------------------|----------------------|
| `file.read`      | `/etc/config.yaml`   |
| `network.connect`| `api.service.local`  |
| `registry.write` | `tools/*`            |
| `artifact.read`  | `abc123`             |
| `secret.access`  | `GITHUB_TOKEN`       |

---

## Capability Enforcement Pattern

Before performing an action:

```python
if not context.get_capability("file.read:/etc/config.yaml"):
    raise CapabilityError("Access denied")
```

---

## Capability Registry Format

```yaml
capabilities:
  - type: "file.read"
    resource: "/etc/config.yaml"
  - type: "registry.write"
    resource: "tools/*"
  - type: "secret.access"
    resource: "OMNIBASE_API_KEY"
```

Wildcards (`*`) and prefix patterns are supported.

---

## CapabilityContext Utilities

Provides helper methods:

```python
context.check_file_read(path)
context.check_network_connect(host, port)
context.check_registry_access(name, mode="read")
context.check_artifact_access(id, mode="write")
```

Raises `CapabilityError` if access is denied.

---

## Secrets Handling

- Secrets are injected into `ExecutionContext`
- Access is gated via `get_secret("SECRET_NAME")`
- May be backed by temp file mounts, env vars, or secret managers

All secret accesses are audited and must be declared in metadata or config.

---

## Planned Security Features

- [ ] Sandbox runners for agent-generated code (gVisor, Firecracker)
- [ ] Capability manifest validation before execution
- [ ] Automatic redaction of sensitive values from logs
- [ ] Threat model documentation ([see Security Deep Dives](./security/threat_model.md))
- [ ] Canary-only execution mode for untrusted tools

---

## Error Types

```python
class CapabilityError(Exception): ...
class SecretAccessError(Exception): ...
class SandboxViolationError(Exception): ...
```

---

> Permissions aren't toggles. They're contracts. Enforce them like you mean it. 