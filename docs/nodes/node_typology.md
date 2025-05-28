<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: node_typology.md
version: 1.0.0
uuid: b4e844ac-3cbe-41d1-9329-9f2d59118597
author: OmniNode Team
created_at: 2025-05-28T12:40:26.711082
last_modified_at: 2025-05-28T17:20:04.566804
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 435401cd0066bac564e5f5fc7133745d3fc5ca244b0d5fb6c3b3cd0cc9193026
entrypoint: python@node_typology.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.node_typology
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Typology and Execution Model

> **Status:** Draft  
> **Last Updated:** 2025-05-18  
> **Purpose:** Define a tiered model for ONEX nodes to clarify execution semantics, state handling, side effect classification, and planning implications. This document supports clearer node authoring, validation, and orchestration.  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation.

---

## Overview

ONEX nodes are the core building blocks of the system. Each node is defined via metadata (`.onex`), a declared interface (`state_contract`), and an optional internal state handler (`reducer`). To support composability, testability, and execution planning, ONEX nodes are categorized into three functional tiers:

---

## Tier 1: Pure Functional Nodes (Stateless)

**Definition:** Deterministic transformations that accept external state and return modified state. No side effects, no internal state.

* **Meta Type:** `tool` or `utility`
* **Reducer:** None
* **State:** Uses only `state_contract`
* **Execution:** One-shot, stateless, side-effect free

**Examples:**

* Math functions (e.g., `add`, `scale`, `clamp`)
* Format converters (e.g., `dict_to_yaml`)
* Content transformers (e.g., `normalize_text`, `strip_html_tags`)
* Embedding or summarization wrappers

**Output State Pattern:**

```json
{
  "status": "success",
  "result": "..."
}
```

> **Expanded Classification:** The [Functional Monadic Node Architecture](./functional_monadic_node_architecture.md) provides an enhanced categorization based on functional purity with specific monadic types (Pure Nodes, Impure Nodes, Plugin Nodes, and Ephemeral Nodes). This approach further refines the classification with stronger guarantees for composition via the `bind()` method and a structured `NodeResult` return type.

---

## Tier 2: Reducer Nodes (Encapsulated State Logic)

**Definition:** Deterministic nodes that include an internal state machine. They support progressive state transitions across invocations.

* **Meta Type:** Often `tool` or `agent`
* **Reducer:** Implements `ReducerProtocol`
* **State:** Internal (via reducer) + External (via `state_contract`)
* **Execution:** Deterministic but state-aware

**Use Cases:**

* Retry with backoff
* Branching logic within a tool
* Memory for session-local data
* Stateful validators or classifiers

**Metadata Example:**

```yaml
reducer: src/omnibase/reducers/retry_tracker.py
```

**ReducerProtocol (stub):**

```python
class ReducerProtocol:
    def initial_state(self) -> dict: ...
    def dispatch(self, state: dict, action: dict) -> dict: ...
```

---

## Tier 3: Impure or Middleware Nodes

**Definition:** Nodes that perform side effects—network calls, file writes, logging, database mutations. May include reducers.

* **Meta Type:** `agent`, `plugin`, `utility`
* **Reducer:** Optional
* **State:** Optional internal state + external context
* **Execution:** Impure (side effects allowed)

**Examples:**

* Remote API callers
* Loggers, file writers
* External service wrappers
* Streaming output handlers

**Identification:**

* Future metadata field: `impure: true`
* Must document affected systems in metadata extensions

---

## Composition & Orchestration

ONEX allows recursive and declarative orchestration:

* Dependencies are declared in metadata (`dependencies`, `base_class`, `protocols_supported`)
* Reducers govern internal decision making
* External orchestration tools (planners) can treat all nodes as functions:

  ```
  (input_state: dict) -> (output_state: dict)
  ```
* Impure nodes may require planning constraints (e.g., ordering, mutex)

---

## Implications for Validation and Execution

### Validation:

* Tier 1: Strict schema validation
* Tier 2: Schema + reducer test coverage
* Tier 3: Additional sandboxing and policy checks

### Trust and Audit:

* All nodes may define `trust_score_stub`
* Impure nodes must track provenance and impact metadata

### Planning:

* Execution planner can use tier to optimize chaining
* Impure/middleware nodes may be deferred, parallelized cautiously, or require gating
* Nodes with declared `execution_profile` and `model_profiles` enable the planner to make decisions based on speed, accuracy, and cost, supporting context-aware and resource-optimized dispatch.
* Composite nodes using `memoization_tier: deep` benefit from subgraph-level caching and reusable execution paths identified via `trace_hash` structures.
* Reducer nodes may declare snapshot strategies to reduce session replay overhead, improving planner efficiency in stateful graph rehydration scenarios.

---

## Future Considerations

* Add `tier` or `impure` hint to `.onex` schema
* Reducers may optionally expose `reducer_contract` for test validation
* Add orchestration metadata for step flows, priority, retry budget

---

## Summary Table

| Tier | Type                | State    | Side Effects | Reducer  | Meta Type(s)           |
| ---- | ------------------- | -------- | ------------ | -------- | ---------------------- |
| 1    | Pure function       | None     | No           | No       | tool, utility          |
| 2    | Stateful (reducer)  | Local    | No           | Yes      | tool, agent            |
| 3    | Middleware / Impure | Optional | Yes          | Optional | utility, agent, plugin |

---

> This document supports clear node authoring, classification, and execution strategy alignment. It should be referenced when designing node metadata and runtime behavior.
