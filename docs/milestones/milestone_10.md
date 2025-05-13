## Milestone 10 — Agent‑as‑Reviewer Pipeline

> **Goal:** Enable an end‑to‑end workflow in which an LLM‑powered agent reviews proposed code or configuration changes, cross‑references OmniBase validation results, and produces structured, actionable feedback that can be surfaced in PRs or CI.

### 1 • Scope & Description

The pipeline ingests a *change set* (git diff, PR, or artifact delta), runs it through existing OmniBase validators, then triggers an **Agent Reviewer** component that:

1. Reads validator/test outcomes and failure contexts.
2. Pulls the relevant code fragments / metadata blobs.
3. Generates human‑readable review comments with inline suggestions.
4. Publishes the review back to VCS (PR comments) **and** stores structured feedback objects (JSON) in the registry for future analytics.

### 2 • Objectives & Success Metrics

| Objective                    | KPI / Metric                                                |
| ---------------------------- | ----------------------------------------------------------- |
| Reduce human review load     | ≥ 30 % decrease in average human review time per PR         |
| Raise early defect detection | ≥ 20 % more defects caught pre‑merge compared with baseline |
| Feedback precision           | ≥ 80 % agent comments marked “useful” by humans             |
| Latency                      | P95 agent review turnaround < 2 min for < 500 LOC changes   |

### 3 • Key Deliverables

* **AgentReviewer service** implementing `AsyncRunnable` and integrating with OpenAI/GPT via capability‑grant model.
* **FeedbackSchema v1** for structured review objects (stored in registry).
* **VCS Adapter** (GitHub first) to post PR comments and status checks.
* **CI Orchestrator Hook** that chains `validators -> AgentReviewer -> publish`.
* **Telemetry dashboards** tracking KPIs above.
* **Security policy** for outbound model calls & PII redaction.

### 4 • Dependencies / Prerequisites

* Milestone 7 (capability‑based security) complete.
* Milestone 8 (graph extraction APIs) complete.
* Milestone 9 (differential testing & RL feedback loop) providing training data for reviewer fine‑tuning.
* Registry read/write endpoints for Feedback objects.

### 5 • Risks & Mitigations

| Risk                              | Impact | Mitigation                                                                   |
| --------------------------------- | ------ | ---------------------------------------------------------------------------- |
| Hallucinated / unsafe suggestions | Medium | Run agent output through validator + content‑policy filter before publishing |
| Latency spikes with large diffs   | Medium | Shard diff by file; stream reviews incrementally                             |
| Sensitive data leakage to LLM     | High   | Inline redaction + context window scrubbing based on capability tags         |
| Developer trust adoption          | Medium | Beta rollout, collect thumbs‑up/down signals, iterate                        |

### 6 • Timeline

| Phase                         | Duration | Outputs                          |
| ----------------------------- | -------- | -------------------------------- |
| Design spec & API contracts   | 1 wk     | ADR + Protobuf/JSON Schema       |
| Prototype agent module        | 2 wks    | Local CLI POC                    |
| VCS integration & CI hook     | 2 wks    | GitHub App, status checks        |
| Hardening & security review   | 1 wk     | Threat‑model doc, pentest report |
| Beta rollout (selected repos) | 2 wks    | KPI dashboard, user feedback     |
| GA release                    | 1 wk     | Docs, migration guide            |

### 7 • Definition of Done

* All deliverables merged to `main` with ✅ passing CI.
* KPI dashboard shows latency & precision targets in staging.
* Security review signed off by Foundation‑Security.
* Documentation published under `docs/pipelines/agent_reviewer.md` including quick‑start & troubleshooting.
* At least one real PR in *omnibase* repo successfully reviewed by the AgentReviewer with positive human feedback.
