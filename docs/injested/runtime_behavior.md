# OmniBase Execution Patterns & Runtime Behavior

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase supports deterministic, source-agnostic execution of all registered components. Whether the source is a hardcoded module, agent-generated script, or pipeline chain, the runtime model is unified by protocol adherence and metadata introspection.

---

## Execution Entry Points

Each component must expose a callable matching:

```python
def run(input: Artifact[T], context: ExecutionContext) -> Result[U]
```

Optional async variant:

```python
async def run(...) -> Result[U]
```

---

## Executable Types

| Type        | Source                          | Execution Path                   |
|-------------|----------------------------------|----------------------------------|
| Validator   | Python function                  | `core/validators/*.py`           |
| Tool        | Python function or CLI shim      | `tools/*` or external            |
| Test        | Declarative YAML or pytest case  | `tests/*.yaml` or `*.py`         |
| AgentCode   | Runtime-compiled Python script   | `sandbox/agent_gen/*.py`         |
| Pipeline    | Composed tool/validator sequence | Inferred from dependency graph   |

---

## Execution Dispatcher

Core logic resides in `omnibase.dispatch.run_component()`:

- Loads registry metadata
- Validates signature
- Constructs execution context
- Resolves and downloads input artifacts
- Runs component in appropriate executor (sync/async/sandboxed)
- Captures and returns result with status, logs, and outputs

---

## Runtime Features

- Idempotency enforcement
- Capability verification
- Structured logging + trace context propagation
- Per-run metadata stamping
- Automatic result persistence (CAS)
- Failure recovery via retry + circuit breaker

---

## Execution Context Contracts

Context provides:

- Configuration (`cfg.get("foo")`)
- Secrets / capabilities interface
- Logger handle with run ID
- Correlation metadata
- Trace parent and span recorder

---

## CLI Example

```bash
omnibase run --uuid abc123 --input file.py --format human
omnibase compose pipeline --from tool_a --to validator_b --execute
```

---

## Future Enhancements

- [ ] Execution history browser CLI
- [ ] Context snapshots for time-travel debugging
- [ ] Runtime plugin hooks (`pre_run`, `post_run`, `on_error`)
- [ ] Memory/resource usage metrics per execution

---

> Execution is not a black box—it’s a logged, traced, permissioned pipeline with receipts.