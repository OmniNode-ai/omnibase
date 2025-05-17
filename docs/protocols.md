# OmniBase Protocols Specification

> **Status:** Canonical (ONEX v0.1 Supersedes)  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16
> **Precedence:** This document incorporates and is governed by the ONEX v0.1 protocol and metadata specifications. Any conflicting or missing details in previous versions are overridden by ONEX v0.1.

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

### ProtocolStamperEngine and Protocol-Driven Tooling

The ONEX Metadata Stamper and related tools are implemented using a protocol-driven, fixture-injectable architecture. This approach ensures that all core logic is defined by Python Protocols, enabling extensibility, testability, and context-agnostic execution.

### ProtocolStamperEngine Interface

The canonical interface for the stamper engine is defined as a Protocol:

```python
from typing import Protocol, Any, Sequence

class ProtocolStamperEngine(Protocol):
    def stamp(self, files: Sequence[str], *, dry_run: bool = False, context: Any = None) -> list[dict]: ...
    def load_ignore_patterns(self, path: str) -> list[str]: ...
    def should_ignore(self, file_path: str) -> bool: ...
```

- **stamp**: Stamps one or more files, supporting dry-run and context injection.
- **load_ignore_patterns**: Loads ignore patterns from a file (e.g., `.stamperignore`).
- **should_ignore**: Determines if a file should be ignored based on loaded patterns.

### Extensibility and Registry

- All protocol-driven engines (including the stamper) are registered in a protocol registry, enabling dynamic discovery and selection at runtime or via CLI.
- New engines can be implemented for different file systems, in-memory testing, or hybrid contexts by implementing the protocol and registering with the registry.

### Fixture Injection and Testability

- All dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture, never hardcoded.
- The protocol-driven design enables context-agnostic, registry-driven tests: the same test suite can run against real, in-memory, or mock engines by swapping fixtures.
- See [docs/testing.md](./testing.md) and [docs/structured_testing.md](./structured_testing.md) for canonical patterns.

### CLI and Engine Selection

- The CLI supports selecting protocol engines and fixture contexts via flags or environment variables.
- This enables full testability and extensibility in CI, pre-commit, and developer workflows.

See also: [docs/tools/stamper.md](./tools/stamper.md), [docs/registry.md](./registry.md), [docs/testing.md](./testing.md)

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

# ONEX v0.1 Canonical Protocols and Execution Model

> **This section is canonical and supersedes any conflicting details below.**

## Mission Statement
Establish a recursive, schema-governed, feedback-aware execution mesh where each task is decomposed into atomic transformers—functions, agents, or classes—bound by formal schemas. Nodes dynamically join, specialize, and execute transformers based on role, memory context, and schema compatibility.

## Core Architectural Principles
- Schema-first, composable, agent-native, memory-backed, trust-aware, simulation-capable, fallback-ready, green-aware, extensible, federated, verifiable, chaos-tolerant, budget-constrained.

## Schema System
- MUST use Pydantic or JSON Schema.
- Field validation, versioning, migration hooks, multi-modal support, live documentation, introspection metadata, export formats.

## Transformer Definition
- Decorator-based registration with input/output schemas, namespace, version, role, simulation-ready flag.
- Side effect, budget, and confidential handling declarations.

## Error Taxonomy
- Canonical error model: Transient, Validation, BudgetExceeded, SecurityViolation.
- Retryable and fallback hints required.

## Registry System
- Signed, hash-addressed, time-stamped entries.
- Searchable by object_type, namespace, tags, trust_level.
- Federation, manifest sync, trust anchor rotation.

## Execution Context and Budget
- Simulation, trace_id, caller_id, execution_budget, policies.
- Budget: max_cost, max_steps, max_energy_kwh, time_limit_seconds.

## Orchestration and Plans
- ExecutionPlan: plan_id, nodes, edges, default_mode, description.
- Batch, hybrid, fallback, agent negotiation.

## Agent Interface
- AgentSpec: agent_id, capabilities, trust_level, region.
- Dry-run routing, trust negotiation, policy enforcement, federation-aware fallback.

## Feedback and Reward
- ExecutionFeedback: transformer_id, rating, reward_signal, notes.

## Federation Model
- Trust anchors, fallback, conflict resolution policies.

## Policy Model
- ExecutionPolicy: type, scope, enforcement_level, payload.
- Runtime negotiation protocol for agents.

## Observability and Telemetry
- Emit logs for execution_start, execution_end, retry, fallback, error, budget_exceeded, deprecation_warning, policy_violation, resource_usage.

## Chaos and Resilience
- chaos_mode, fault domain tagging, simulation fallback validation.

## Formal Verification (Optional)
- formally_verified, proof_reference, verified_chain.

## Continuous Benchmarking
- latency_ms, memory_mb, energy_kwh, error_rate, canary runs, regression checks, benchmark deltas.

## Monetization Hooks
- billing_model, pricing, SLA.

## Deprecation and Sunset Policy
- deprecated_since, sunset_date, replacement, warning emission.

## RegistryEntry Wrapper
- object_type, payload, fingerprint, trust_level, registered_at, doc_url.

## Execution Trust Chain
- Agent keypair, node identity, signed registry entry, session grant, execution attestation.

# ONEX v0.1 Canonical Execution Protocol Additions

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

ONEX Execution Protocol (v0.1)

Overview

This document defines the runtime coordination model for ONEX nodes: how they are scheduled, invoked, evaluated, and managed under trust, cost, and fallback constraints.

This spec focuses on execution plans, chaining behavior, dry-run simulation, budget enforcement, and operational feedback. It complements other documents such as onex_validator_protocol_and_result_model, onex_metadata_block_spec, and onex_chunk_validator_spec.

⸻

🧠 ExecutionPlan Model

class ExecutionPlan(BaseModel):
    plan_id: str
    nodes: List[str]  # Node IDs in registry
    edges: List[Tuple[str, str]]  # Directed edges
    default_mode: Literal["local", "distributed", "hybrid"]
    description: Optional[str]

Plans can:
	•	Describe execution graphs
	•	Be submitted via CLI or scheduled by agents
	•	Include fallback, retry, or simulation overrides

⸻

⚙️ Execution Modes

Mode	Description
local	Run everything in current environment
distributed	Routed across trusted ONEX clusters
hybrid	Default; runtime chooses per node

Execution planners may override via CLI or config.

⸻

💸 Execution Budget & Simulation

class ExecutionBudget(BaseModel):
    max_cost: Optional[float]  # USD
    max_energy_kwh: Optional[float]
    max_steps: Optional[int]
    time_limit_seconds: Optional[int]

	•	Agents can perform dry-run with mode: dry_run
	•	Execution halted on budget overrun unless fallback defined

⸻

🔄 Fallback & Retry

class RetryPolicy(BaseModel):
    max_retries: int
    delay_strategy: str  # exponential, fixed, jitter
    fallback_node_id: Optional[str]

	•	Fallbacks defined per node or edge
	•	Signature or trust failures trigger auto-fallback
	•	Retry and quorum checks embedded in agent feedback loop

⸻

🔁 Execution Feedback

class ExecutionFeedback(BaseModel):
    node_id: str
    version: str
    status: Literal["success", "failure", "partial"]
    reward_signal: Optional[float]
    trace_id: Optional[str]
    notes: Optional[str]

Agents log feedback per node for:
	•	Trust scoring
	•	Node version promotion
	•	Replay debugging and learning

⸻

🧪 Chaos and Simulation Modes
	•	chaos_mode: true triggers fault injection in CI
	•	Simulation may:
	•	Randomly drop nodes
	•	Fail nodes with expired trust
	•	Measure fallback efficacy

Used for:
	•	Validating execution plans
	•	Auditing fallback resilience
	•	Benchmarking fault tolerance

⸻

📊 SLA and Billing (Optional)

Nodes may declare:

sla:
  uptime: "99.95%"
  latency_ms: 200
billing_model: metered
cost_per_execution: 0.0005

This metadata is used in hybrid execution decisions and trust scoring.

⸻

🧩 CLI Integration

onex run plan.yaml --mode=hybrid
onex simulate --plan plan.yaml
onex feedback submit feedback.json

⸻

Status: Canonical runtime coordination spec for ONEX execution chains, fallback handling, dry-run simulation, budget modeling, and fault injection support.

---

# Appendix A: General Execution Model Descriptions

> The following sections provide historical context and high-level rationale for ONEX execution plans, fallback, retry, budget, and feedback models. These are retained for reference only; the explicit model definitions above are canonical and supersede all prior general descriptions.

// [Move the general/abstract execution plan, fallback, retry, budget, and feedback content here.] 