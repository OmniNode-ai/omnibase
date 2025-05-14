# OmniBase Orchestration Specification

> **Status:** Canonical (ONEX v0.1 Supersedes)  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16
> **Precedence:** This document incorporates and is governed by the ONEX v0.1 protocol and metadata specifications. Any conflicting or missing details in previous versions are overridden by ONEX v0.1.

---

## Overview

The orchestration layer provides the standardized execution entry points for all OmniBase components. Orchestrators are stage-specific controllers that manage how functions (validators, tools, tests) are run, filtered, retried, and reported. They encode the rules of responsibility at every stage.

---

## Orchestrator Pattern

Each orchestrator is a class implementing:

```python
class Orchestrator(ABC):
    def run(self, ctx: ExecCtx) -> RunReport: ...
```

Orchestrators may be synchronous or asynchronous depending on the use case. They consume an `ExecutionContext`, execute registered components, and return a structured result.

---

## Orchestrator Types

| Name                   | Description                                        |
|------------------------|----------------------------------------------------|
| `PreCommitOrchestrator`| Runs pre-commit hooks                              |
| `CIOrchestrator`       | Executes in CI pipelines                           |
| `TestOrchestrator`     | Executes test cases                                |
| `PipelineOrchestrator` | Runs composed tool/validator pipelines             |
| `RegistryOrchestrator` | Administers the registry (add, remove, inspect)    |

All orchestrators:
- Respect idempotency contracts from metadata
- Use retry decorators for transient errors
- Raise circuit breakers on repeated failure
- Support dry-run mode for previewing changes
- Emit structured logs and metrics per run

---

## Invocation & CLI

Standard entry point for orchestration:

```bash
omnibase orch --stage pre-commit --format human || exit 1
```

Other usage patterns:
```bash
omnibase orch --stage test --tags integration
omnibase orch --stage ci --filter 'type=validator,lifecycle=canary'
omnibase orch --stage pipeline --from tool_a --to tool_b --to validator_x
```

Defaults:
- `--format json` for non-interactive runs
- `--format human` for interactive terminals (`isatty=True`)

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
- `lifecycle` (e.g., `canary`, `stable`, `deprecated`, `experimental`)
- `tags` (e.g., `schema`, `pre-commit`)
- `type` (`tool`, `validator`, `test`)

They apply filters automatically, e.g. `PreCommitOrchestrator` only runs `canary` + `pre-commit` validators by default.

---

## Retry & Circuit Integration

Orchestrators enforce:
- Exponential backoff retries for idempotent functions
- Circuit breaker short-circuiting on repeated failure
- Performance profiling and timeout logging

---

## Output Formatting

| Format Flag | Audience         | Characteristics                        |
|-------------|------------------|----------------------------------------|
| `--format human` | Developers       | ANSI color, emoji, ≤100 char lines     |
| `--format json`  | CI tools         | Canonical, machine-readable output     |
| `--format yaml`  | Debugging/Agents | Block-style YAML, anchor support       |

The formatter registry (`omnibase.cli.formatters.FORMATTERS`) maps these to rendering functions.

Auto-detection for interactive terminals and CI contexts. ASCII fallback applies when:
- `TERM=dumb`
- `CI=true`
- `--no-color` is specified

### Emoji Map (Human Output)

| Status | Emoji |
|--------|-------|
| PASS   | ✅     |
| FAIL   | ❌     |
| WARN   | ⚠️     |
| SKIP   | ⏭️     |
| TIME   | ⏱️     |

---

## Execution Modes

| Mode        | Used When                          | Retry? | Async? | Notes                          |
|-------------|------------------------------------|--------|--------|--------------------------------|
| `sync`      | Local runs, blocking                | Yes    | No     | Default                        |
| `async`     | Long pipelines, CI                  | Yes    | Yes    | Runs concurrently              |
| `dry-run`   | Debug mode                          | No     | No     | No changes, logs only          |
| `profile`   | Performance analysis                | No     | No     | Tracks latency, logs metrics   |
| `replay`    | Re-execute from snapshot            | Yes    | Yes    | Uses stored artifacts/results  |

---

## Exit Codes

| Code | Meaning                     |
|------|-----------------------------|
| 0    | Success                     |
| 1    | Execution failed            |
| 2    | Configuration error         |
| 3    | Registry resolution failure |
| 4    | Protocol violation          |
| 5    | Sandbox/security violation  |

---

## Planned Enhancements
- [ ] Finalize orchestrator ABC and shared base class
- [ ] Implement CLI `orch` command dispatch logic
- [ ] Add timeout and resource control for CI orchestrators
- [ ] Validate support for both sync and async execution
- [ ] Integrate output formatter fallback and structured logging
- [ ] Parallel pipeline composition
- [ ] Retry + circuit-breaker wrappers
- [ ] Custom hook points for pre/post execution
- [ ] Partial execution graphs with skip logic
- [ ] Visual progress reporting
- [ ] Interactive debug mode with live step-through
- [ ] Pipeline visualization after orchestrator run
- [ ] Failure snapshot and replay for postmortems
- [ ] Policy-based stage gating

---

## ONEX v0.1 Canonical Orchestration and Execution Model

> **This section is canonical and supersedes any conflicting details below.**

## Orchestration Mission
ONEX orchestration formalizes execution plans, agent negotiation, batch/hybrid/fallback execution, and lifecycle enforcement for all nodes, agents, and transformers.

## Execution Plan Model
- ExecutionPlan: plan_id, nodes, edges, default_mode (local/distributed/hybrid), description.
- Batch, hybrid, fallback, and agent negotiation are first-class.

## Agent Interface
- AgentSpec: agent_id, capabilities, trust_level, region.
- Supports dry-run routing, trust negotiation, policy enforcement, federation-aware fallback.

## Lifecycle and Policy Enforcement
- All orchestrators must enforce lifecycle, trust, and policy constraints as defined in ONEX v0.1.
- Policy model: ExecutionPolicy (type, scope, enforcement_level, payload), runtime negotiation protocol for agents.

## CI and Result Reporting
- Orchestrators must emit logs for execution_start, execution_end, retry, fallback, error, budget_exceeded, deprecation_warning, policy_violation, resource_usage.
- Must support conformance suite: schema validation, retry/fallback conformance, budget exhaustion tracing, policy injection enforcement, federation failover simulation, chaos test validation.

> Orchestrators are the operational backbone of OmniBase: they wrap execution in context, enforce lifecycle policies, and emit observable results. 