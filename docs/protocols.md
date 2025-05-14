# OmniBase Protocols Specification

> **Status:** Draft  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase uses standardized protocol definitions to enforce composability, compatibility, and testability across components. Every core function must adhere to these protocols for registration and execution. OmniBase distinguishes between **Protocols** and **ABCs (Abstract Base Classes)** for implementation and compatibility. This separation enables more flexible validation, agent compatibility, and better support for non-subclass-based systems like `pydantic`.

---

## Core Protocols

### 1. `ExecutionContext`
**Purpose:** Provides execution configuration, tracing metadata, logging, and capability access.

```python
from typing import Protocol, Any, Optional
from uuid import UUID

class ExecutionContext(Protocol):
    __protocol_version__ = "1.0.0"

    def get_config(self, key: str, default: Any = None) -> Any: ...
    def get_capability(self, name: str) -> bool: ...
    def get_correlation_id(self) -> UUID: ...
    def get_logger(self, name: Optional[str] = None): ...
```

### 2. `Artifact[T]`
**Purpose:** Represents a typed input to a validator or tool.

Artifacts are versioned, hashable, and carry type-specific payloads (e.g., files, directories, metadata blocks).

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Artifact(Protocol[T]):
    __protocol_version__ = "1.0.0"

    def get_payload(self) -> T: ...
    def get_hash(self) -> str: ...
    def get_metadata(self) -> dict: ...
```

### 3. `Result[U]`
**Purpose:** Encapsulates the outcome of a function call.

All results inherit from a base `UnifiedResultModel` and contain:
- Status
- Detailed messages
- Output artifacts (optional)
- Error metadata (optional)

```python
from typing import Protocol, TypeVar, Generic

U = TypeVar('U')

class Result(Protocol[U], Generic[U]):
    __protocol_version__ = "1.0.0"

    def get_status(self) -> str: ...
    def get_output(self) -> U: ...
    def get_messages(self) -> list[str]: ...
    def get_errors(self) -> list[dict]: ...
```

---

## Sync and Async Function Signatures

### Sync:
```python
def run(input: Artifact[T], context: ExecutionContext) -> Result[U]: ...
```

### Async:
```python
async def run(input: Artifact[T], context: ExecutionContext) -> Result[U]: ...
```

Use `AsyncRunnable` for long-running, I/O-bound, or concurrent operations.

---

## ABC vs Protocol

OmniBase distinguishes between **Protocols** (for interface definition and test doubles) and **ABCs** (for concrete, runtime enforcement).

| Type      | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| Protocol  | Structural interface; no inheritance required; ideal for agent generation |
| ABC       | Enforced inheritance; strict; used for internal execution/runtime binding |

- **Protocols** (in `protocols/`) are used for interface definition and test doubles.
- **ABCs** (in `core/abcs/`) are used for concrete, runtime enforcement.
- All production code must **not** import from `protocols.testing`.
- This rule is enforced via `flake8-omnibase` rule `OB101`.

### Protocol Examples

```python
class Result(Protocol):
    status: str
    errors: Optional[list]
    produced_at: datetime
```
- Used in: agents, tools, external validators
- Compatible with `typing_extensions.Protocol` or `collections.abc`
- Validated by MyPy or Pyright statically

### ABC Examples

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
| Registry       | `REGISTRY_VERSION`         | Same major + minor = compat                 |
| Metadata       | `metadata_version`         | Same major + minor = compat                 |

Use the `check_compat()` helper function for version checking.

---

## Schema Enforcement

- Pydantic models (`BaseModel`) use schema_version fields
- Validated via `omnibase validate schema <path>` or runtime orchestrator check
- Compatibility logic used to gate registry acceptance

---

## Next Steps
- [ ] Freeze core protocol versions at `1.0.0`
- [ ] Implement static checks for version drift
- [ ] Complete ABC counterparts in `core/abcs/`
- [ ] Protocol test harness generator for agents
- [ ] ABC ↔ Protocol converter stubs for hybrid use
- [ ] CLI `describe interface` tool
- [ ] Interface contract diffs and signature changesets

---

> You don't build an ecosystem on inheritance—you build it on protocol. 