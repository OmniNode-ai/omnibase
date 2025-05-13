# OmniBase Orchestrator Framework

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

All execution flows in OmniBase are driven by orchestrators. These are stage-specific controllers that manage how functions (validators, tools, tests) are run, filtered, retried, and reported.

---

## Canonical Invocation Pattern

```bash
omnibase orch --stage pre-commit --format human || exit 1
```

The orchestrator handles:

- Registry resolution
- Input artifact discovery
- Execution context setup
- Capability validation
- Retry logic and circuit breakers
- Result formatting and output

---

## Orchestrator Classes

Defined in `core/orchestrators/`.

### Base Interface

```python
class Orchestrator(ABC):
    def run(self, ctx: ExecCtx) -> RunReport: ...
```

### Stage-Specific Types

| Class                  | Role                                      |
|------------------------|-------------------------------------------|
| `PreCommitOrchestrator`| Executes pre-commit validations            |
| `CIOrchestrator`       | CI gate validations                        |
| `TestOrchestrator`     | Runs test cases, filters by lifecycle      |
| `PipelineOrchestrator` | Runs tool/validator pipelines              |
| `RegistryOrchestrator` | Manages registry entry mutations           |

---

## Run Report Object

Each orchestrator returns a `RunReport` containing:

- List of `Result[U]` entries
- Summary status
- Execution time and metadata
- Exit code for CLI tools
- Trace correlation IDs

---

## Lifecycle Awareness

All orchestrators support filtering by:

- `lifecycle` (e.g., `canary`, `stable`)
- `tags` (e.g., `schema`, `pre-commit`)
- `type` (`tool`, `validator`, `test`)

This allows selective enforcement depending on stage and environment.

---

## Retry + Circuit Integration

Orchestrators enforce:

- Exponential backoff retries for idempotent functions
- Circuit breaker short-circuiting on repeated failure
- Performance profiling and timeout logging

---

## CLI Usage Patterns

```bash
omnibase orch --stage test --tags integration
omnibase orch --stage ci --filter 'type=validator,lifecycle=canary'
omnibase orch --stage pipeline --from tool_a --to tool_b --to validator_x
```

---

## Output Formatting

Respects `--format` flags:

- `human`: Dev-facing
- `json`: CI-facing
- `yaml`: Debug/agent-facing

Auto-detection for interactive terminals and CI contexts.

---

## Future Work

- [ ] Interactive debug mode with live step-through
- [ ] Pipeline visualization after orchestrator run
- [ ] Failure snapshot and replay for postmortems
- [ ] Policy-based stage gating

---

> Orchestrators are the CPUs of OmniBase: all logic flows through them.