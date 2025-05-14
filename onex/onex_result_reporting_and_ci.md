## ONEX Result Reporting and CI Integration

### Overview

This document defines how execution results, batch output, and validator feedback are captured and exported within the ONEX architecture. It builds on the legacy `UnifiedBatchResultModel` and introduces structured output for CI, dashboards, and registry publication.

---

### ✅ Result Output Goals

* Consistent structure across all node types
* Human- and machine-readable
* Compatible with CI pipelines and dashboards
* Supports metadata for trust, signature, and batch lifecycle

---

### 1. Result Model Schema

```python
class NodeExecutionResult(BaseModel):
    node_id: str
    input_hash: str
    output_hash: Optional[str]
    success: bool
    execution_time_ms: Optional[int]
    metadata: Dict[str, Any]
    errors: Optional[List[str]]
    warnings: Optional[List[str]]
    status: Literal["success", "failure", "skipped", "partial"]
```

---

### 2. Batch Result Summary

```python
class BatchExecutionResult(BaseModel):
    batch_id: str
    status: Literal["success", "partial", "failure"]
    results: List[NodeExecutionResult]
    started_at: datetime
    completed_at: datetime
    coverage_percent: Optional[float]
    trust_delta: Optional[float]
    trust_notes: Optional[str]
```

---

### 3. Output Format

* Recommended export format: `.json` or `.ndjson`
* Supports filters: `--only-failed`, `--only-regression`, `--include-coverage`
* Optional YAML snapshot for inclusion in GitOps or registry commits

---

### 4. Trust + CI Metadata

```yaml
ci_run:
  triggered_by: pre-merge
  policy: trust_gate
  node_count: 11
  trust_enforced: true
  minimum_coverage_required: 90
  runtime_flags: [sandboxed, registry-synced]
  failed_nodes:
    - validator.linter.namegen
```

---

### 🧪 Example Output

```json
{
  "batch_id": "validator_patch_v3",
  "status": "partial",
  "results": [
    {
      "node_id": "validator.check.format",
      "success": true,
      "execution_time_ms": 101,
      "status": "success"
    },
    {
      "node_id": "validator.check.deprecated",
      "success": false,
      "status": "failure",
      "errors": ["Unexpected global import"]
    }
  ],
  "trust_delta": -0.02,
  "started_at": "2025-05-14T08:01:12Z",
  "completed_at": "2025-05-14T08:01:23Z"
}
```

---

### 🛠 CLI Integration

* `onex run --output batch_result.json`
* `onex validate --export=ci_output.ndjson`
* `onex report --summary --only-failed`
* `onex badge generate --trust-level`

---

**Status:** Consolidated from legacy CI/test result model and refactored for structured, trust-aware reporting in ONEX batch and CI flows.
