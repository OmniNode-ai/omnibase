# OmniBase Protocol vs ABC Guidelines and Compatibility Matrix

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase distinguishes between **Protocols** and **ABCs (Abstract Base Classes)** for implementation and compatibility. This separation enables more flexible validation, agent compatibility, and better support for non-subclass-based systems like `pydantic`.

---

## Definitions

| Type      | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| Protocol  | Structural interface; no inheritance required; ideal for agent generation |
| ABC       | Enforced inheritance; strict; used for internal execution/runtime binding |

---

## Protocol Examples

```python
class Result(Protocol):
    status: str
    errors: Optional[list]
    produced_at: datetime
```

- Used in: agents, tools, external validators
- Compatible with `typing_extensions.Protocol` or `collections.abc`
- Validated by MyPy or Pyright statically

---

## ABC Examples

```python
class Validator(ABC):
    def run(self, input: Artifact, ctx: ExecutionContext) -> ValidationResult:
        raise NotImplementedError
```

- Used in: orchestrators, CLI runners
- Subject to registration hooks and decorators
- Enables mixins, tracing, and capability enforcement

---

## Compatibility Matrix

| Consumer Type | Expects Protocol? | Expects ABC? | Notes                                  |
|---------------|-------------------|--------------|----------------------------------------|
| Agents        | ✅                | ❌           | Protocols ensure flexibility           |
| CLI           | ❌                | ✅           | Uses runtime-registered ABCs           |
| Registry      | ✅                | ✅           | Can register both if schema-valid      |
| Sandbox       | ✅                | ❌           | Protocols + signature check only       |
| Internal Tools| ❌                | ✅           | ABCs allow for tracing, retry, etc.    |

---

## Decorator Guidance

- Prefer `@runtime_checkable` on all Protocols
- Use `@abstractmethod` only inside ABCs
- Avoid mixing Protocol and ABC patterns in a single interface

---

## Versioning Strategy

| Interface Type | Version Field              | Compatibility Rule                         |
|----------------|----------------------------|---------------------------------------------|
| Protocol       | `__protocol_version__`     | Major version must match                    |
| ABC            | `SCHEMA_VERSION` (constant)| Major version must match; warn on minor     |

---

## Schema Enforcement

- Pydantic models (`BaseModel`) use schema_version fields
- Validated via `omnibase validate schema <path>` or runtime orchestrator check
- Compatibility logic used to gate registry acceptance

---

## Future Features

- [ ] Protocol test harness generator for agents
- [ ] ABC ↔ Protocol converter stubs for hybrid use
- [ ] CLI `describe interface` tool
- [ ] Interface contract diffs and signature changesets

---

> You don’t build an ecosystem on inheritance—you build it on protocol.