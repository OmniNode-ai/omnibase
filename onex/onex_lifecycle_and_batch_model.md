## ONEX Lifecycle and Batch Model

### Overview

This document captures how node-level lifecycles, batch coordination, and tuple enforcement operate within the ONEX architecture. These ideas originate from earlier orchestrator and validator designs, now adapted into the new ONEX execution framework.

---

### ✅ Key Concepts

#### 1. Node Lifecycle State

Each ONEX node or registry entry may carry a `lifecycle_status` value:

```yaml
lifecycle_status: active | frozen | legacy | pending | batch-complete
```

* `active`: The default state. Node is executable and mutable.
* `frozen`: The node’s metadata and schema are locked.
* `legacy`: Still usable, but no longer under active development.
* `pending`: Under validation or awaiting trust elevation.
* `batch-complete`: Finalized as part of a larger orchestrated unit.

These tags are enforced during validation, publishing, and CI/CD export.

---

#### 2. Tuple Enforcement via Lifecycle Enforcer

The **lifecycle enforcer** is a validation step or CLI plugin that:

* Checks for missing or invalid `lifecycle_status`
* Prevents updates to `frozen` entries unless explicitly overridden
* Requires that all entries in a `batch` agree on their lifecycle tag
* Warns on execution of `legacy` or `pending` nodes in critical paths

---

#### 3. Batch Coordination

A `BatchPlan` represents a logical collection of related ONEX components:

```yaml
batch_id: batch-validator-v1
description: "Validator refactor and enforcement milestone"
tuple_ids:
  - validator.format_check
  - validator.tree_check
  - tool.autogen_namegen
  - test.sanity_check.tree
dependency_graph: ... (optional)
required_status: frozen
```

Used in:

* Release gating
* CI planning
* Registry grouping
* Audit trails

---

#### 4. Versioning + Freeze Contracts

Nodes part of a `frozen` batch must:

* Declare a version tag (`version: 0.3.4`)
* Pass all conformance checks
* Be accompanied by signature or trust metadata

---

### 🧪 Example: Enforcer Result Schema

```json
{
  "batch_id": "validator-core-v1",
  "status": "failure",
  "errors": [
    {
      "tuple_id": "tool.validator.autofix",
      "reason": "Expected status: frozen; found: active"
    }
  ],
  "passed": ["test.tree.sanity"]
}
```

---

### 🛠 CLI Integration (Planned)

* `onex validate --enforce-lifecycle`
* `onex batch freeze batch-id.yaml`
* `onex publish --only-frozen`
* `onex report --include-lifecycle`

---

**Status:** Derived from legacy orchestrator lifecycle manager design. Recast as a core enforcement layer within the ONEX graph system.
