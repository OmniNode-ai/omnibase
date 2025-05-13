# OmniBase Protocol Definitions

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase uses standardized protocol definitions to enforce composability, compatibility, and testability across components. Every core function must adhere to these protocols for registration and execution.

---

## Core Protocols

### 1. `ExecutionContext`

**Purpose:** Provides execution configuration, tracing metadata, logging, and capability access.

    from typing import Protocol, Any, Optional
    from uuid import UUID

    class ExecutionContext(Protocol):
        __protocol_version__ = "1.0.0"

        def get_config(self, key: str, default: Any = None) -> Any: ...
        def get_capability(self, name: str) -> bool: ...
        def get_correlation_id(self) -> UUID: ...
        def get_logger(self, name: Optional[str] = None): ...

---

### 2. `Artifact[T]`

**Purpose:** Represents a typed input to a validator or tool.

Artifacts are versioned, hashable, and carry type-specific payloads (e.g., files, directories, metadata blocks).

    from typing import Protocol, TypeVar

    T = TypeVar('T')

    class Artifact(Protocol[T]):
        __protocol_version__ = "1.0.0"

        def get_payload(self) -> T: ...
        def get_hash(self) -> str: ...
        def get_metadata(self) -> dict: ...

---

### 3. `Result[U]`

**Purpose:** Encapsulates the outcome of a function call.

All results inherit from a base `UnifiedResultModel` and contain:

- Status
- Detailed messages
- Output artifacts (optional)
- Error metadata (optional)

    from typing import Protocol, TypeVar, Generic

    U = TypeVar('U')

    class Result(Protocol[U], Generic[U]):
        __protocol_version__ = "1.0.0"

        def get_status(self) -> str: ...
        def get_output(self) -> U: ...
        def get_messages(self) -> list[str]: ...
        def get_errors(self) -> list[dict]: ...

---

## Sync and Async Function Signatures

### Sync:

    def run(input: Artifact[T], context: ExecutionContext) -> Result[U]: ...

### Async:

    async def run(input: Artifact[T], context: ExecutionContext) -> Result[U]: ...

Use `AsyncRunnable` for long-running, I/O-bound, or concurrent operations.

---

## ABC vs Protocol Guidelines

- **Protocols** (in `protocols/`) are used for interface definition and test doubles.
- **ABCs** (in `core/abcs/`) are used for concrete, runtime enforcement.
- All production code must **not** import from `protocols.testing`.

This rule is enforced via `flake8-omnibase` rule `OB101`.

---

## Version Compatibility

| Component      | Version Key              | Compatibility Rule         |
|----------------|--------------------------|-----------------------------|
| Protocol       | `__protocol_version__`   | Same major = compatible     |
| ABC            | `SCHEMA_VERSION`         | Same major = compatible     |
| Registry       | `REGISTRY_VERSION`       | Same major + minor = compat |
| Metadata       | `metadata_version`       | Same major + minor = compat |

Use the `check_compat()` helper function for version checking.

---

## Next Steps

- [ ] Freeze core protocol versions at `1.0.0`
- [ ] Implement static checks for version drift
- [ ] Complete ABC counterparts in `core/abcs/`

---

> For test mocks, use only `protocols/testing/`.  
> For concrete types, extend from `core/abcs/` with `SCHEMA_VERSION`.