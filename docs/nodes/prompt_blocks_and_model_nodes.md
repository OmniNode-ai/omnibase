# ONEX Node Architecture: Prompt Blocks and Model Nodes (as Functions)

> **Status:** Canonical
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation.

## 05 – Prompt Blocks and Model Nodes

### Context & Origin

This document outlines how prompts and model-backed nodes are treated as first-class components in ONEX, viewed through the lens of the [Node as a Function](docs/nodes/index.md) model. It stems from the core insight:

> "Prompts are just structured **input data**—and models are just **transformer functions**."

---

### Core Principles

#### ✅ Prompts Are Structured Input Data

* Every user or agent-issued prompt is wrapped in a `prompt_block` – a standardized data structure.
* Prompt blocks are hashable, cacheable, and versioned, allowing them to be treated as consistent, addressable pieces of **input state** (function arguments).
* They are handled consistently within the `state_contract` input passed to node functions, similar to how configuration or file inputs are structured.

#### ✅ Models Are Just Transformer Functions

* A model (e.g., an AI language model) is implemented or wrapped as an ONEX node with a `meta_type` indicating its role (typically `tool` or a more specific future `model` type).
* It functions as a **transformer function**:
    * It defines an input `state_contract` that specifies the expected structure of its input data, including prompt blocks (`prompt.text`, `prompt.image`, etc.).
    * It defines an output `state_contract` that specifies the structured output it produces (e.g., `code.text`, `text.completion`, `image.url`).
    * Its `.onex` metadata carries critical information about the function's properties (cost, context limit, latency, accuracy), which are used by the planner.

---

### Prompt Block Structure

The `prompt_block` is a canonical data structure used within a node's input `state_contract` to represent prompt data.

```yaml
# Example prompt_block structure (part of a node's input state_contract)
id: prompt.codegen.validate_uuid # Unique ID for this specific prompt block instance
text: "Write a Python function that validates a UUID." # The main prompt content
tags: ["codegen", "validator"] # Metadata tags
contracts: # Expected properties of the output from a function processing this prompt
  expected_output: code.text # Declares the expected type of output artifact
metadata: # Additional metadata about the prompt
  origin: user # e.g., user, agent, system
  submitted_by: jonah.gray
  timestamp: 2025-05-15T08:00:00Z
```

#### ✅ Prompt Contracts

* Prompt blocks can optionally declare `contracts` specifying the expected properties or types of the output `state_contract` that should be produced by a node function processing this prompt.
* Prompts can be scored by validator or judge nodes (functions that evaluate the output quality based on the prompt's expectations).
* Prompt blocks can be stored, reused, versioned, or used in tournament-based evaluations of different model function variants.

---

### Model Node Example (as a Transformer Function)

Here's an example of the metadata for a node that wraps a model, highlighting its function signature via contracts and its relevant properties.

```yaml
# node.onex.yaml (example for a model node / transformer function)
schema_version: "0.1.0"
name: "codegen_gpt4"
version: "1.0.0"
uuid: "..."
author: "..."
description: "Generates code from a text prompt using the GPT-4 model."
meta_type: "tool" # Or potentially 'model' in future
engine: "gpt-4-1" # Specific model implementation details
input_contract: "schema://contracts/transformer/text_prompt_input.json" # Schema for input state (includes prompt_block)
output_contract: "schema://contracts/transformer/code_output.json"   # Schema for output state
entrypoint:
  type: python # Or 'container', etc.
  target: src/omnibase/models/gpt4_codegen_adapter.py # The function implementation
# Metadata about the function's execution characteristics:
metadata:
  context_limit: 128000 # Token limit
# Performance and cost metadata linked or embedded (as in 06 - Performance):
performance:
  avg_latency_ms: 220
  success_rate: 0.93
model_profiles:
  - model: gpt-4-turbo
    cost_per_1k_tokens: 0.01
# Other standard .onex fields follow...
```

---

### Prompts as Drivers for Executable Planning Units

Prompt blocks are not just static data; they are active components that can drive the execution planning process. A prompt block can initiate a workflow by forming the initial input state for a node function call.

* A `prompt_block` is prepared (structured input state).
* This input state is passed to an initial **transformer node function** (e.g., a model wrapper).
* The output `state_contract` from the transformer function is then passed to subsequent **node functions** (e.g., validator functions, judge functions) to test and score the result against expectations defined in the prompt block's `contracts`.
* This sequence triggers a full execution pipeline where:
    * The prompt input is routed to the appropriate node function.
    * Variant model nodes (different function implementations) can compete to produce the best output.
    * The output is automatically validated or judged by downstream functions.

---

### Execution Profiles for Model Nodes (Transformer Functions)

As detailed in [06 - Performance, Memory, and Cost](docs/nodes/performance_memory_and_cost.md), model nodes (transformer functions) carry execution profiles.

```yaml
# Part of node.onex.yaml (derived from performance data and declarations)
execution_profile:
  speed: 7      # Relative speed of this function
  accuracy: 9   # Relative accuracy or quality of this function's output
  efficiency: 3 # Relative cost-efficiency of this function
```

When used within a composite node with `memoization_tier: deep`, model nodes contribute to subgraph-level caching and optimization. Their `execution_profile` metadata supports planner decisions about which variant to invoke when multiple transformer nodes share the same input/output contract. This makes model-backed transformer functions fully compatible with deep memoization strategies and cost-aware subgraph reuse.

---

### Prompt Reuse and Context Sharing

Prompt blocks, as structured input state components, can be stored persistently (e.g., in cold context).

* They can be shared and reused across different sessions, users, or agents.
* Stored prompt blocks can include origin metadata, historical responses from different node function calls, and score history from validation/judging nodes. This allows for rich tracking of how prompts are used and the quality of outputs they generate.

---

### Agent Planning + Prompt Scaffolding (Orchestrating Function Calls)

Agents in ONEX function as orchestrators that plan and direct workflows by initiating and managing node function calls.

* Agents can generate new prompt blocks (structured input state) from higher-level task descriptions.
* They can score responses from different node function calls based on validation outcomes.
* Agents can dynamically swap in cheaper/faster **transformer function variants** based on predefined thresholds or learned performance data.

---

**Status:** Canonical architecture for prompt-as-input and model-as-node design in ONEX, framing prompts as structured input data and models as executable transformer functions. Fully compatible with cost planning, trust metadata, execution profiles, and A/B node function tournaments.

---