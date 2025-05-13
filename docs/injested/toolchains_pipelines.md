# OmniBase Toolchains, Transformations, and Pipelines

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

Toolchains in OmniBase are composed sequences of tools and validators that operate over a shared artifact stream. Pipelines are explicit or inferred execution graphs formed from registry metadata and declared dependencies.

---

## Tool vs. Validator

| Type      | Mutates Input? | Returns Output? | Used In Pipelines? |
|-----------|----------------|------------------|---------------------|
| Validator | No             | No (pass/fail)   | Yes                 |
| Tool      | Yes            | Yes (transforms) | Yes                 |

Validators assert correctness; tools perform transformations.

---

## Pipeline Composition

You can compose pipelines using:

- Explicit CLI or agent definitions
- Dependency declarations in metadata (`dependencies:` field)
- Registry DAG traversal

---

## CLI Pipeline Composition

```bash
omnibase compose pipeline --from tool_a --to tool_b --to validator_c
omnibase run pipeline uuid-of-pipeline
```

---

## Pipeline Metadata (Future Feature)

Pipelines may eventually have their own metadata blocks:

```yaml
uuid: "abc123"
name: "sanitize_source_tree"
steps:
  - tool: fix_headers
  - tool: normalize_indent
  - validator: schema_check
tags: ["pre-commit", "refactor"]
```

---

## Execution Order

Resolved by:

1. Topological sort of dependency graph
2. Registry lifecycle filtering (e.g., skip deprecated)
3. CLI/agent-provided step override

All steps receive an `ExecutionContext`.

---

## Output Propagation

Each tool returns an `Artifact` which becomes input to the next step.

```python
artifact1 = run(tool_a, input, ctx)
artifact2 = run(tool_b, artifact1, ctx)
result = run(validator_c, artifact2, ctx)
```

All artifacts are stored in CAS and referenced in the final `Result`.

---

## Idempotency & Retry

Each step may:

- Declare `idempotent: true` to enable retry
- Be cached or skipped if identical input + digest match
- Be skipped in dry-run mode

---

## Tool Metadata Block Example

```yaml
uuid: "tool-uuid"
name: "normalize_whitespace"
version: "0.2.0"
type: "tool"
entrypoint: "tools/normalize.py"
tags: ["format", "style"]
idempotent: true
dependencies:
  - id: "tool-trim_trailing"
    type: "tool"
    version_spec: ">=0.1.0"
```

---

## Future Enhancements

- [ ] Pipeline-level validation + visualization
- [ ] DAG diffing + impact analysis
- [ ] Agent-synthesized pipelines from task description
- [ ] Partial pipelines for targeted re-validation

---

> A single tool is helpful. A validated, auditable toolchain is infrastructure.