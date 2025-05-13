# docs/milestones/05\_security\_model\_and\_sandbox.md

> **Milestone 05 – Security Model & Sandbox**
> *Target release: v0.5.0*
> *Estimated effort: 10 person‑days*
> *Owner(s):* security‑guild, foundation‑team

---

## 1  Purpose

Create the first production‑quality security layer for OmniBase. This layer enforces *least‑privilege execution*, provides *container‑level isolation* for agent‑generated code, and introduces an auditable *capability policy* system. The goal is to make arbitrary code execution safe by default while remaining developer‑friendly.

---

## 2  Scope & Deliverables

| #      | Deliverable                           | Description                                                                                                                      |
| ------ | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **D1** | `docs/security/threat_model.md`       | STRIDE‑style threat analysis covering registries, orchestration, artifact storage, and agent execution.                          |
| **D2** | `core/security/capabilities.py` (MVP) | Typed capability primitives (`Capability`, `CapabilitySet`, *etc.*) with pattern matching and enforcement helpers.               |
| **D3** | `core/sandbox/` prototype             | gVisor‑backed sandbox runner capable of executing Python scripts with configurable permissions & resource limits.                |
| **D4** | Policy language POC                   | JSON‑serialisable *Cedar‑style* policy documents that map OmniBase metadata ➜ capability grants.                                 |
| **D5** | CLI integration                       | `omnibase sandbox run <script> --capabilities <cap_file>` utility for manual testing.                                            |
| **D6** | Unit & integration tests              | Security regression suite (PyTest) validating confinement, denial of disallowed syscalls, network egress, secret leakage, *etc.* |
| **D7** | Audit logging hooks                   | Emit structured security events (`SandboxStart`, `CapabilityDenied`, …) to the global event bus.                                 |

Out‑of‑scope for this milestone:

* Full multi‑language sandbox support (container images, WASM, *etc.*) ↬ tracked for Milestone 08.
* Attribute‑based access control for remote registries ↬ Milestone 09.

---

## 3  Dependencies

* **Milestone 03 – Error Handling & Resilience** ⟶ retry decorators, circuit‑breaker errors must propagate through sandbox runner.
* **Milestone 04 – Registry MVP** ⟶ capability policies are stored & versioned via registry metadata extensions.

---

## 4  Design Overview

1. **Threat Model**

   * Identify attacker personas: *malicious agent function*, *compromised validator*, *rogue CI process*.
   * Assets: registry integrity, artifact confidentiality, host stability, secret stores.
2. **Sandbox Runner**

   * Implement thin wrapper around *gVisor* (`runsc`).
   * Hard resource quotas: CPU = 1, Mem = 256 MiB (tunable via `ExecutionContext`).
   * Network namespace isolated by default; explicit `NETWORK_CONNECT` capability required for egress.
3. **Capability Evaluation**

   * Incoming `CapabilitySet` compiled from: component metadata + runtime override flags.
   * Enforcement performed *inside* sandbox via side‑car daemon (agent) and *outside* via pre‑exec checks.
4. **Policy Language**

   * Cedar‑subset: principals = *component UUID*, resources = *capability tokens*, actions = `allow|deny`.
   * Stored at `registry/policies/<component_uuid>.cedar.json`.

---

## 5  Implementation Plan

1. **Week½ 1 (ws 1–5)**

   * Draft STRIDE document (D1).
   * Implement `Capability`, `CapabilitySet`, matching logic (D2) + unit tests.
2. **Week½ 2 (ws 6–8)**

   * Integrate *gVisor* via python‑subprocess wrapper (`core/sandbox/runner.py`).
   * Map capabilities ➜ gVisor flags (mount masks, seccomp rules, netns toggles).
   * Build CLI wrapper (`omnibase sandbox run …`).
3. **Week½ 3 (ws 9–10)**

   * Implement Cedar POC evaluator (`core/security/policy.py`).
   * Wire evaluator into registry loader.
   * Add audit logging + event bus hooks.
   * Finish integration & regression tests (D6).

---

## 6  Acceptance Criteria

* ✅ Running a simple untrusted Python script without capabilities cannot:

  * read `/etc/passwd` (blocked by FS mask);
  * open outbound TCP sockets (netns disabled);
  * exceed 50 MB RSS (cgroup enforced).
* ✅ Same script **with** `FILE_READ` capability on `/data/allowed.txt` *can* read that file—but not `/data/other.txt`.
* ✅ Attempting disallowed actions raises `SandboxViolationError` and is logged via event bus.
* ✅ All new code covered at ≥ 90 % statement coverage.

---

## 7  Risks & Mitigations

| Risk                         | Impact                               | Mitigation                                            |
| ---------------------------- | ------------------------------------ | ----------------------------------------------------- |
| gVisor performance overhead  | Slower validator runs                | Benchmark; allow opt‑out for *trusted* components.    |
| Policy complexity creep      | Hard to audit                        | Keep initial Cedar subset minimal; document patterns. |
| Capability mis‑configuration | False positives causing job failures | Provide dry‑run mode & verbose diagnostics.           |

---

## 8  Exit Criteria ‑ "Definition of Done"

1. All deliverables **D1–D7** merged to `main`.
2. Security regression suite passes in CI (*sandbox*, *policy*, *capabilities*).
3. Documentation published at `docs/security/` and linked from README.
4. Internal demo: run agent‑generated script with & without permissions.

---

*After Milestone 05 completes, the platform will safely execute untrusted code under tight controls, paving the way for multi‑language runtimes and advanced policy enforcement in upcoming milestones.*

