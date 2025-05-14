## 01 – Node Contracts and Metadata Structure

### Context & Origin

This document formalizes the philosophy and structure behind treating **contracts** and **metadata** as the true execution foundation of ONEX.

This shift began with the realization that:

> "The most important thing in the system isn’t what executes—it’s the metadata that describes it."

---

### Key Principles

#### ✅ Every Node is Metadata-First

* A node is defined entirely by its metadata:

  * What it does
  * What it needs
  * What it outputs
  * What it affects
* Logic is *secondary* to declared contracts and performance history

#### ✅ Contracts Define Executability

```yaml
input_contract:
  metadata.name: str
  config.enabled: bool
output_contract:
  patch.valid: bool
  patch.modified_files: [str]
```

* Contracts are strict, versioned, and testable
* Every node must register a contract to be eligible for execution

#### ✅ Contracts = Validation, Composition, Replacement

* Contracts enable:

  * Pre-flight checks
  * Composition across nodes
  * Trust score comparisons
  * Dynamic replacement and substitution

---

### Metadata Block Structure

```yaml
id: scaffold.validator
version: 0.3.1
hash: sha256:abcd1234
input_contract: {...}
output_contract: {...}
performance:
  total_runs: 152
  success_rate: 96.7%
  avg_latency_ms: 108
  cost_profile_usd: 0.0012
trust:
  verified: true
  signer: omninode.registry
  score: 0.92
```

#### 🔁 Performance Memory

* Nodes self-report execution results
* Registry aggregates and updates over time
* Failed nodes can be replaced, promoted, or demoted automatically

#### 🔄 Trace Hashing

* `trace_hash` = deterministic representation of:

  * Node ID + version
  * Input + config
  * Output + exit state

This enables:

* Cache key creation
* Node equivalence comparisons
* Hash-based override or fallback selection

---

### Node Lifecycles

* Nodes are:

  * Defined via contract
  * Executed under constraint
  * Tracked via metadata
  * Benchmarked over time
  * Swappable via hash or contract match

#### 🧬 Evolutionary Optimization

* Nodes can be tournament-tested or judged
* If a node fails or degrades, the system can:

  * Generate a new variant
  * Compare hash and score
  * Promote the best-fit node

---

### Node Identity and Mutation Policy

| Field            | Mutable? | Notes                         |
| ---------------- | -------- | ----------------------------- |
| `id`             | ❌        | Immutable                     |
| `version`        | ✅        | Version bump required         |
| `trace_hash`     | ✅        | Changes per execution context |
| `trust.score`    | ✅        | Dynamic                       |
| `input_contract` | ✅        | Must be versioned             |
| `performance.*`  | ✅        | Aggregated continuously       |

---

### Prompt + Model Integration

* Prompts and models are treated as:

  * Input blocks with contracts
  * Nodes with execution metadata

#### Prompt Block Example

```yaml
id: prompt.codegen.uuid
text: "Write a Python function to validate a UUID."
tags: ["codegen", "validator"]
contracts:
  expected_output: code.text
```

---

### Benefits

* Transparent introspection of any node
* Agent-friendly discovery and routing
* Long-term trust evolution
* Replay and rollback supported

---

**Status:** Canonical structure for contract-first, metadata-driven nodes. Used by all validators, transformers, models, and agent-dispatchable components in ONEX.
