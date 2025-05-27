<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: orchestration.md
version: 1.0.0
uuid: fc75e506-2efa-4a93-a9ea-76b62055637f
author: OmniNode Team
created_at: 2025-05-27T05:42:34.597764
last_modified_at: 2025-05-27T17:26:51.859838
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: c89bd4238340b991efcffe0de7c8243af34e156e8da618176108d1ba472fe38d
entrypoint: python@orchestration.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.orchestration
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Orchestration Specification

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Standardized execution entry points for all OmniBase components

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
onex orch --stage pre-commit --format human || exit 1
```

Other usage patterns:
```bash
onex orch --stage test --tags integration
onex orch --stage ci --filter 'type=validator,lifecycle=canary'
onex orch --stage pipeline --from tool_a --to tool_b --to validator_x
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

## ONEX Orchestration and Execution Model

### Orchestration Mission
ONEX orchestration formalizes execution plans, agent negotiation, batch/hybrid/fallback execution, and lifecycle enforcement for all nodes, agents, and transformers.

### Execution Plan Model
- ExecutionPlan: plan_id, nodes, edges, default_mode (local/distributed/hybrid), description.
- Batch, hybrid, fallback, and agent negotiation are first-class.

### Agent Interface
- AgentSpec: agent_id, capabilities, trust_level, region.
- Supports dry-run routing, trust negotiation, policy enforcement, federation-aware fallback.

### Lifecycle and Policy Enforcement
- All orchestrators must enforce lifecycle, trust, and policy constraints as defined in ONEX v0.1.
- Policy model: ExecutionPolicy (type, scope, enforcement_level, payload), runtime negotiation protocol for agents.

### CI and Result Reporting
- Orchestrators must emit logs for execution_start, execution_end, retry, fallback, error, budget_exceeded, deprecation_warning, policy_violation, resource_usage.
- Must support conformance suite: schema validation, retry/fallback conformance, budget exhaustion tracing, policy injection enforcement, federation failover simulation, chaos test validation.

---

## Orchestrator Implementation Guidelines

### Base Orchestrator Class

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExecutionContext:
    """Context for orchestrator execution"""
    stage: str
    tags: List[str]
    filters: Dict[str, Any]
    dry_run: bool = False
    format: str = "human"
    timeout: Optional[int] = None

@dataclass
class RunReport:
    """Result of orchestrator execution"""
    status: str
    results: List[Any]
    execution_time_ms: int
    started_at: datetime
    completed_at: datetime
    correlation_id: str
    exit_code: int = 0

class Orchestrator(ABC):
    """Base class for all orchestrators"""
    
    @abstractmethod
    def run(self, ctx: ExecutionContext) -> RunReport:
        """Execute the orchestrator with given context"""
        pass
    
    def supports_stage(self, stage: str) -> bool:
        """Check if orchestrator supports given stage"""
        return stage in self.supported_stages
    
    def validate_context(self, ctx: ExecutionContext) -> bool:
        """Validate execution context"""
        return True
```

### Error Handling in Orchestrators

```python
from omnibase.errors import OrchestratorError, RetryableError

class OrchestratorExecutionError(OrchestratorError):
    """Raised when orchestrator execution fails"""
    pass

class OrchestratorTimeoutError(OrchestratorError):
    """Raised when orchestrator execution times out"""
    pass

# Example error handling
try:
    result = orchestrator.run(context)
except RetryableError as e:
    # Apply retry logic
    logger.warning(f"Retryable error in orchestrator: {e}")
    # Implement exponential backoff
except OrchestratorError as e:
    # Handle orchestrator-specific errors
    logger.error(f"Orchestrator error: {e}")
    return RunReport(status="failed", exit_code=1, ...)
```

### Integration with Registry

```python
from omnibase.registry import Registry

class RegistryAwareOrchestrator(Orchestrator):
    """Orchestrator that uses registry for component discovery"""
    
    def __init__(self, registry: Registry):
        self.registry = registry
    
    def discover_components(self, ctx: ExecutionContext) -> List[Any]:
        """Discover components based on context filters"""
        query = self.build_registry_query(ctx)
        return self.registry.find(query)
    
    def build_registry_query(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Build registry query from execution context"""
        return {
            "stage": ctx.stage,
            "tags": ctx.tags,
            "lifecycle": "active",
            **ctx.filters
        }
```

---

## Best Practices

### For Orchestrator Developers

1. **Always validate context**: Check execution context before proceeding
2. **Implement proper error handling**: Use structured error types and proper logging
3. **Support dry-run mode**: Allow preview of changes without execution
4. **Emit structured logs**: Include correlation IDs and execution metadata
5. **Respect timeouts**: Implement proper timeout handling and cleanup

### For CLI Integration

1. **Use consistent exit codes**: Follow the standard exit code conventions
2. **Support multiple output formats**: Implement human, JSON, and YAML formatters
3. **Provide progress feedback**: Show execution progress for long-running operations
4. **Handle interruption gracefully**: Support SIGINT/SIGTERM for clean shutdown

### For Testing

1. **Test all execution modes**: Verify sync, async, dry-run, and profile modes
2. **Mock external dependencies**: Use registry mocks and fixture injection
3. **Test error conditions**: Verify proper error handling and recovery
4. **Validate output formats**: Ensure all formatters produce valid output

---

> Orchestrators are the operational backbone of OmniBase: they wrap execution in context, enforce lifecycle policies, and emit observable results.
