# OmniBase Orchestration Layer

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

The orchestration layer provides the standardized execution entry points for all OmniBase components. Each stage of the system—pre-commit, CI, pipeline, test, and registry—is handled by a dedicated orchestrator class, implementing common interfaces for invocation, configuration, and reporting.

---

## Orchestrator Pattern

Each orchestrator is a class implementing:

    class Orchestrator(ABC):
        def run(self, ctx: ExecCtx) -> RunReport: ...

Orchestrators may be synchronous or asynchronous depending on the use case. They consume an `ExecutionContext`, execute registered components, and return a structured result.

---

## Orchestrator Types

### 1. `PreCommitOrchestrator`

Validates changes before code is committed. Typically fast, stateless, and tagged with `pre-commit`.

### 2. `CIOrchestrator`

Runs validations and tests in CI environments. Supports parallel execution and performance tuning.

### 3. `PipelineOrchestrator`

Executes composed tool/validator pipelines. Resolves dependencies, handles chaining and caching.

### 4. `TestOrchestrator`

Runs registry-registered test cases. Filters by test type, lifecycle, and target component.

### 5. `RegistryOrchestrator`

Handles registry mutations:
- Add/update/remove entries
- Validate metadata blocks
- Sync with remote or file-based sources

---

## CLI Entry Point

Standard entry point for orchestration:

    omnibase orch --stage pre-commit --format human || exit 1

Defaults:
- `--format json` for non-interactive runs
- `--format human` for interactive terminals (`isatty=True`)

---

## Output Formats

| Format Flag | Audience         | Characteristics                        |
|-------------|------------------|----------------------------------------|
| `--format human` | Developers       | ANSI color, emoji, ≤100 char lines     |
| `--format json`  | CI tools         | Canonical, machine-readable output     |
| `--format yaml`  | Debugging/Agents | Block-style YAML, anchor support       |

The formatter registry (`omnibase.cli.formatters.FORMATTERS`) maps these to rendering functions.

---

## Emoji Map (Human Output)

| Status | Emoji |
|--------|-------|
| PASS   | ✅     |
| FAIL   | ❌     |
| WARN   | ⚠️     |
| SKIP   | ⏭️     |
| TIME   | ⏱️     |

ASCII fallback applies when:
- `TERM=dumb`
- `CI=true`
- `--no-color` is specified

---

## Execution Contracts

All orchestrators:
- Respect idempotency contracts from metadata
- Use retry decorators for transient errors
- Raise circuit breakers on repeated failure
- Support dry-run mode for previewing changes
- Emit structured logs and metrics per run

---

## Next Steps

- [ ] Finalize orchestrator ABC and shared base class
- [ ] Implement CLI `orch` command dispatch logic
- [ ] Add timeout and resource control for CI orchestrators
- [ ] Validate support for both sync and async execution
- [ ] Integrate output formatter fallback and structured logging

---

> Orchestrators are the operational backbone of OmniBase: they wrap execution in context, enforce lifecycle policies, and emit observable results.