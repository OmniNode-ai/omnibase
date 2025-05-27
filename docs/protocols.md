# OmniBase Protocols Specification

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Standardized protocol definitions to enforce composability, compatibility, and testability across components

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

### 4. ProtocolStamperEngine and Protocol-Driven Tooling

The ONEX Metadata Stamper and related tools are implemented using a protocol-driven, fixture-injectable architecture. This approach ensures that all core logic is defined by Python Protocols, enabling extensibility, testability, and context-agnostic execution.

#### ProtocolStamperEngine Interface

The canonical interface for the stamper engine is defined as a Protocol:

```python
from typing import Protocol, Any, Sequence

class ProtocolStamperEngine(Protocol):
    def stamp(self, files: Sequence[str], *, dry_run: bool = False, context: Any = None) -> list[dict]: ...
    def load_ignore_patterns(self, path: str) -> list[str]: ...
    def should_ignore(self, file_path: str) -> bool: ...
```

- **stamp**: Stamps one or more files, supporting dry-run and context injection.
- **load_ignore_patterns**: Loads ignore patterns from a file (e.g., `.onexignore`).
- **should_ignore**: Determines if a file should be ignored based on loaded patterns.

#### Extensibility and Registry

- All protocol-driven engines (including the stamper) are registered in a protocol registry, enabling dynamic discovery and selection at runtime or via CLI.
- New engines can be implemented for different file systems, in-memory testing, or hybrid contexts by implementing the protocol and registering with the registry.

#### Fixture Injection and Testability

- All dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture, never hardcoded.
- The protocol-driven design enables context-agnostic, registry-driven tests: the same test suite can run against real, in-memory, or mock engines by swapping fixtures.
- See [docs/testing.md](./testing.md) for canonical patterns.

#### CLI and Engine Selection

- The CLI supports selecting protocol engines and fixture contexts via flags or environment variables.
- This enables full testability and extensibility in CI, pre-commit, and developer workflows.

See also: [docs/tools/stamper.md](./tools/stamper.md), [docs/registry.md](./registry.md), [docs/testing.md](./testing.md)

---

## Function Signatures

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
- Validated via `onex validate <path>` or runtime orchestrator check
- Compatibility logic used to gate registry acceptance

---

## ONEX Execution Protocol

### ExecutionPlan Model

```python
class ExecutionPlan(BaseModel):
    plan_id: str
    nodes: List[str]  # Node IDs in registry
    edges: List[Tuple[str, str]]  # Directed edges
    default_mode: Literal["local", "distributed", "hybrid"]
    description: Optional[str]
```

Plans can:
- Describe execution graphs
- Be submitted via CLI or scheduled by agents
- Include fallback, retry, or simulation overrides

### Execution Modes

| Mode | Description |
|------|-------------|
| local | Run everything in current environment |
| distributed | Routed across trusted ONEX clusters |
| hybrid | Default; runtime chooses per node |

### Execution Budget & Simulation

```python
class ExecutionBudget(BaseModel):
    max_cost: Optional[float]  # USD
    max_energy_kwh: Optional[float]
    max_steps: Optional[int]
    time_limit_seconds: Optional[int]
```

- Agents can perform dry-run with `mode: dry_run`
- Execution halted on budget overrun unless fallback defined

### Fallback & Retry

```python
class RetryPolicy(BaseModel):
    max_retries: int
    delay_strategy: str  # exponential, fixed, jitter
    fallback_node_id: Optional[str]
```

- Fallbacks defined per node or edge
- Signature or trust failures trigger auto-fallback
- Retry and quorum checks embedded in agent feedback loop

### Execution Feedback

```python
class ExecutionFeedback(BaseModel):
    node_id: str
    version: str
    status: Literal["success", "failure", "partial"]
    reward_signal: Optional[float]
    trace_id: Optional[str]
    notes: Optional[str]
```

Agents log feedback per node for:
- Trust scoring
- Node version promotion
- Replay debugging and learning

### CLI Integration

```bash
onex run plan.yaml --mode=hybrid
onex simulate --plan plan.yaml
onex feedback submit feedback.json
```

---

## Core Architectural Principles

- **Schema-first:** All interfaces defined by formal schemas
- **Composable:** Components can be combined and reused
- **Agent-native:** Designed for autonomous agent interaction
- **Memory-backed:** Persistent state and context
- **Trust-aware:** Built-in security and verification
- **Simulation-capable:** Dry-run and testing support
- **Fallback-ready:** Graceful degradation and recovery
- **Extensible:** Plugin and extension architecture
- **Federated:** Distributed operation support
- **Verifiable:** Formal verification capabilities
- **Budget-constrained:** Resource and cost management

---

## Schema System

- MUST use Pydantic or JSON Schema
- Field validation, versioning, migration hooks
- Multi-modal support, live documentation
- Introspection metadata, export formats

---

## Error Taxonomy

Canonical error model includes:
- **Transient:** Temporary failures that may resolve
- **Validation:** Schema or input validation failures
- **BudgetExceeded:** Resource or cost limits exceeded
- **SecurityViolation:** Trust or security policy violations

All errors must include retryable and fallback hints.

---

## Registry System

- Signed, hash-addressed, time-stamped entries
- Searchable by object_type, namespace, tags, trust_level
- Federation, manifest sync, trust anchor rotation

---

## Observability and Telemetry

Emit logs for:
- execution_start, execution_end
- retry, fallback, error
- budget_exceeded, deprecation_warning
- policy_violation, resource_usage

---

## Future Enhancements

- [ ] Freeze core protocol versions at `1.0.0`
- [ ] Implement static checks for version drift
- [ ] Complete ABC counterparts in `core/abcs/`
- [ ] Protocol test harness generator for agents
- [ ] ABC ↔ Protocol converter stubs for hybrid use
- [ ] CLI `describe interface` tool
- [ ] Interface contract diffs and signature changesets 