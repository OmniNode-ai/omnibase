> **Status:** Canonical  
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation. 

## 05 – Prompt Blocks and Model Nodes

### Context & Origin

This document outlines how prompts and model-backed nodes are treated as first-class components in ONEX. It stems from:

> "Prompts are just input blocks—and models are just transformer nodes."

---

### Core Principles

#### ✅ Prompts Are Native Inputs

* Every user or agent-issued prompt is wrapped in a `prompt_block`
* Prompt blocks are hashable, cacheable, and versioned
* Treated the same way as config or file inputs

#### ✅ Models Are Just Nodes

* A model is a `transformer` node with:

  * Input contract (e.g. `prompt.text`)
  * Output contract (e.g. `code.text`)
  * Metadata (cost, context limit, latency, accuracy)

---

### Prompt Block Structure

```yaml
id: prompt.codegen.validate_uuid
text: "Write a Python function that validates a UUID."
tags: ["codegen", "validator"]
contracts:
  expected_output: code.text
metadata:
  origin: user
  submitted_by: jonah.gray
```

#### ✅ Prompt Contracts

* Expected outputs can be declared
* Prompts can be scored by validators or judge nodes
* Prompts can be reused, versioned, or tournamented

---

### Model Node Example

```yaml
id: transformer.codegen.gpt4
engine: gpt-4.1
type: transformer
input_contract:
  prompt.text: str
output_contract:
  code.text: str
metadata:
  context_limit: 128k
  cost_per_1k_tokens: 0.01
  avg_latency: 220ms
  success_rate: 93%
```

---

### Prompts as Executable Planning Units

* Prompt → transformer node → contract → test → score
* Can trigger full pipeline:

  * Prompt is routed
  * Variant model nodes compete
  * Output is validated or judged

---

### Execution Profiles for Model Nodes

```yaml
execution_profile:
  speed: 7
  accuracy: 9
  cost: 3
```

* Helps orchestrators pick appropriate transformer node
* Supports fallback chains and cost-aware dispatch

---

### Prompt Reuse and Context Sharing

* Prompt blocks can be stored in cold context
* Shared across sessions, users, or agents
* Can include origin metadata, response history, score history

---

### Agent Planning + Prompt Scaffolding

* Agents can:

  * Generate prompt blocks from task descriptions
  * Score responses from different nodes
  * Swap in cheaper/faster transformers based on thresholds

---

**Status:** Canonical architecture for prompt-as-input and model-as-node design in ONEX. Fully compatible with cost planning, trust metadata, and A/B node tournaments. 