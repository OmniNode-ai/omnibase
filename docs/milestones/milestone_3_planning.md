<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:26.549880'
description: Stamped by ONEX
entrypoint: python://milestone_3_planning.md
hash: e3c524be291affa756998554e1c237ff58f9c890f452f5fbe4b6d322a68a3507
last_modified_at: '2025-05-29T11:50:15.032570+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: milestone_3_planning.md
namespace: omnibase.milestone_3_planning
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 3d82990f-08d7-48eb-8c67-569ceac0660b
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# Milestone 3: Agent Execution and MCP Integration

---

## Objective

Establish a working autonomous agent execution environment using the finalized message bus and foundation layers. This milestone introduces the MCP controller, enables local job execution via agents, supports registry bootstrap via metadata crawling, and executes real workflows using Magentic-One. It marks the first full vertical slice of OmniNode from job input to output.

---

## Scope

### 1. MCP Service (Controller)

- Finalize `mcp/` service container
- Accept job submissions via:
  - CLI (`mcp submit job.json`)
  - File-based watch directory (`jobs/`)
- Dispatch jobs to agents via internal message bus (Redis Streams)

---

### 2. Job Schema Definition

Define canonical job request structure (`JobRequest`) with support for:

<pre><code class="json">
{
  "job_id": "abc123",
  "task": "build a calculator",
  "agent_sequence": ["architect", "coder", "tester", "verifier"],
  "config": {
    "max_retries": 2,
    "trace": true,
    "context": ["python"]
  }
}
</code></pre>

- Schema must be CI-validated and versioned
- Jobs must conform to each agent’s declared `input_schema` and `output_schema`

---

### 3. Agent Orchestration (Magentic-One)

- Use Magentic-One for static role-based agent execution
- Support fallback and retry logic (per agent step)
- Agent sequence must match registered roles
- Each step logs outputs to:
  - MessageBus (status update topic)
  - Local disk (optional)
  - Ledger (via message transition logging)

Execution pattern: `Architect → Coder → Tester → Verifier`

---

### 4. Agent Registry Bootstrap via Metadata Crawler

- Implement `registry_crawler` utility
- Walk `src/`, `agents/`, or configured directory roots
- Parse files containing metadata blocks
- Register any agents, validators, or test modules discovered

Registry entries will include:

<pre><code class="yaml">
- name: github_sniper
  entrypoint: main.py
  role: discovery
  input_schema: schemas/sniper_input.json
  output_schema: schemas/sniper_output.json
  metadata_block: parsed_from_file
</code></pre>

- Crawler should optionally enforce canonical directory structure
- CI must validate registry consistency against source metadata

---

### 5. Message Bus Integration

- MCP dispatches tasks via Redis Streams
- Agents consume messages tagged with their role
- Envelope fields:
  - `source`: MCP
  - `target`: agent role
  - `node_id`: optional local routing ID
  - `protocol_version`: `v0.1`

- DLQ and ledger fallback must be enforced for all routed agent tasks

---

### 6. Multinode Local Support (Optional)

- Introduce support for multiple agent-capable containers
- Each agent node identifies via `node_id`
- Routing based on `target.node_id` in message envelope
- No dynamic discovery; use static config or `consul` stub
- Stand up minimal LLM service container (e.g. via Ollama) to simulate remote node

---

### 7. Logging and Observability

- Agents must emit:
  - `stdout`/`stderr` logs
  - MessageBus status updates
  - Ledger transitions (e.g., `received`, `executed`, `failed`)

- Include simple CLI tools:
  - `mcp status <job_id>`
  - `ledger view --job job_id`

---

## Exclusions / Deferred Items

Explicitly out of scope:
- ProxyFlow routing or prompt injection
- LangGraph-based orchestration
- Inter-node scheduling or trust mesh
- Streaming model execution
- Marketplace integration
- Federated registry sync
- External job queue ingestion

---

## Output Criteria

- MCP service is operational and CI-validated
- At least one end-to-end job executes via Magentic-One agent sequence
- MessageBus dispatch, DLQ fallback, and ledger logging are enforced
- Registry crawler populates agent, validator, and test registries from metadata
- CLI tools for job submission and status inspection are functional
- Multinode simulation (via local node_id) is working with at least two containers
