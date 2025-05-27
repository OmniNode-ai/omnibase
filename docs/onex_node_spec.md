# ONEX Node Specification and Linking Model

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the complete `.onex` node schema, linking model, URI format, trust and validation metadata, and the structure and behavior required for ONEX node discoverability, execution, and interconnectivity  
> **Audience:** Node authors, tool builders, runtime developers, CI engineers

---

## What is an ONEX Node?

An ONEX node is a self-contained, declarative, executable unit defined by a `.onex` metadata file. Nodes are:
- Discoverable via `.onextree` or registry
- Executable via a defined `entrypoint`
- Validated against schemas and CI rules
- Composable via `dependencies`, `protocols_supported`, and `base_class`
- Rated via a trust score stub
- Interoperable with ONEX runtimes and agents

---

## Canonical `.onex` Metadata Schema

Each node has a `node.onex.yaml` file located in its top-level directory.

```yaml
# node.onex.yaml (example)
schema_version: "0.1.0"
name: "extract_summary_block"
version: "1.0.0"
uuid: "65dfc205-96f3-4f86-8497-cf6d8a1c4b95"
author: "foundation"
created_at: 2025-05-17T10:05:00Z
last_modified_at: 2025-05-17T10:15:00Z
description: "Parses a metadata block and extracts summary and status fields for display."
state_contract: "state_contract://summary_block_schema.json"
lifecycle: "active"
hash: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
entrypoint:
  type: python
  target: src/omnibase/tools/cli_extract_summary_block.py
namespace: "omninode.tools.extract_summary_block"
meta_type: "tool"
runtime_language_hint: "python>=3.11"
tags: ["metadata", "docs", "summary"]
trust_score_stub:
  runs: 12
  failures: 0
  trust_score: 1.0
x-extensions: {}
protocols_supported: []
base_class:
  - validator://core.schema_validator@1.0.0
dependencies:
  - tool://tools.tree_generator@>=0.2.0
environment: []
license: "Apache-2.0"
# Optional field not shown: signature_block
```

## Protocol-Driven Stamping and Metadata Validation

- The ONEX Metadata Stamper is implemented as a protocol-driven, fixture-injectable engine. It injects and validates metadata blocks in `.onex` files according to the canonical schema above.
- All stamping and validation logic is defined by Python Protocols, enabling extensibility, testability, and context-agnostic execution.
- The stamper engine ensures that all required fields, formats, and schema constraints are enforced for every node.
- All dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture, never hardcoded.
- The protocol-driven design enables registry-driven, context-agnostic validation and stamping in CI, pre-commit, and developer workflows.
- See [docs/protocols.md](./protocols.md), [docs/tools/stamper.md](./tools/stamper.md), and [docs/testing.md](./testing.md) for details on protocol-driven stamping and validation.

---

## Canonical Linking Fields

### Current Fields

| Field             | Type     | Description                                            |
|------------------|----------|--------------------------------------------------------|
| `dependencies`    | list     | Other nodes this node requires at runtime             |
| `base_class`      | list     | Interface or abstract class this node adheres to      |
| `protocols_supported` | list | Protocols or standards this node conforms to          |

These fields **must use a standardized URI format** (see below).

---

## URI Format for Linking Fields

### Canonical Format

```
<type>://<namespace>@<version_spec>
```

- `<type>`: `tool`, `validator`, `agent`, `model`, `schema`, `plugin`
- `<namespace>`: Dot-delimited identifier (e.g. `core.schema_validator`)
- `<version_spec>`: Semver or constraint (e.g. `1.0.0`, `>=0.2.0`)

### Examples

```yaml
dependencies:
  - tool://tools.tree_generator@>=0.2.0
  - validator://core.schema_validator@1.0.0
base_class:
  - validator://core.base@^1.0
```

---

## File Layout (Recommended)

Each node should be self-contained in its own directory, named to match the `name` in the `.onex`.

```
extract_summary_block/
├── node.onex.yaml
├── src/
│   └── omnibase/
│       └── tools/
│           └── cli_extract_summary_block.py
├── tests/
│   └── test_extract_summary_block.py
├── README.md
```

This layout:
- Ensures tooling and CI can discover node boundaries
- Matches `.onextree` generation
- Keeps implementation, metadata, and tests co-located

---

## State Contract (Input/Output Interface)

The `state_contract` field links to a JSON Schema file that defines the node's expected input/output shape. Example:

```json
{
  "title": "SummaryBlockState",
  "type": "object",
  "properties": {
    "summary": { "type": "string" },
    "status": { "type": "string" }
  },
  "required": ["summary", "status"]
}
```

- File is referenced via `state_contract: "state_contract://summary_block_schema.json"`
- Schema lives under `src/omnibase/schema/schemas/`
- Used for both runtime validation and CI enforcement

---

## Validation Rules

CI must enforce:

- All `.onex` files must pass schema validation (`onex_node.yaml`)
- `uuid` must be a valid v4 UUID
- `hash` must match file hash of `node.onex.yaml`
- `lifecycle` must be one of: `draft`, `active`, `deprecated`, `archived`
- `.onextree` file must reference this node correctly
- `entrypoint.target` must exist and be executable

Optional validation:
- Signature block validation
- Trust score consistency across executions
- URI parsing and dereferencing for dependency validation

---

## Trust and Signature Fields

Optional fields for enhanced security and trust:

- `trust_score_stub` records execution history
- `signature_block` enables cryptographic verification of the node metadata

### Trust Score Example

```yaml
trust_score_stub:
  runs: 150
  failures: 2
  trust_score: 0.987
  last_updated: 2025-01-27T10:30:00Z
  validation_history:
    - timestamp: 2025-01-27T09:00:00Z
      status: "success"
      duration_ms: 1250
    - timestamp: 2025-01-27T08:30:00Z
      status: "success"
      duration_ms: 980
```

### Signature Block Example

```yaml
signature_block:
  algorithm: "RSA-SHA256"
  public_key_id: "key-123"
  signature: "base64-encoded-signature"
  signed_fields: ["name", "version", "hash", "entrypoint"]
  timestamp: 2025-01-27T10:30:00Z
```

---

## Templates and Node Scaffolding

ONEX supports generation of nodes via reusable templates:

- Templates reside in `src/omnibase/templates/`
- Scaffold nodes generate compliant `.onex`, source, and test files
- Template system supports parameterization and customization

### Template Usage

```bash
# List available templates
onex template list

# Generate node from template
onex template generate validator_node \
  --name my_validator \
  --author "Your Name" \
  --description "Custom validator for my use case"

# Validate generated node
onex validate my_validator/node.onex.yaml
```

---

## .onextree Discovery Format

Each project or container should have a top-level `.onextree` file that enumerates valid nodes. Example:

```yaml
nodes:
  - name: extract_summary_block
    path: extract_summary_block/node.onex.yaml
    version: "1.0.0"
    type: tool
  - name: validate_tree_file
    path: tree_validator/node.onex.yaml
    version: "2.1.0"
    type: validator
```

### .onextree Generation

```bash
# Generate .onextree file
onex run tree_generator_node --args='["--root-directory", ".", "--output-path", ".onextree"]'

# Validate .onextree file
onex validate .onextree

# Update .onextree after changes
onex run tree_generator_node --args='["--update"]'
```

---

## Node Lifecycle Management

### Lifecycle States

| State | Description | Allowed Transitions |
|-------|-------------|-------------------|
| `draft` | Work in progress | → `active`, `archived` |
| `active` | Production ready | → `deprecated` |
| `deprecated` | Marked for removal | → `archived` |
| `archived` | No longer maintained | None (terminal) |

### Lifecycle Transitions

```bash
# Check lifecycle status
onex node-info my_node --show-lifecycle

# Transition lifecycle state
onex lifecycle transition my_node --from draft --to active

# List nodes by lifecycle
onex list-nodes --lifecycle active
onex list-nodes --lifecycle deprecated
```

---

## Node Execution

### Direct Execution

```bash
# Execute node directly
onex run extract_summary_block --args='["file.md"]'

# Execute with specific version
onex run extract_summary_block --version 1.0.0

# Execute with introspection
onex run extract_summary_block --introspect
```

### Execution Context

Nodes receive an execution context with:

- Configuration access
- Capability-based permissions
- Logging infrastructure
- Correlation IDs for tracing

```python
# Example node implementation
def execute(context: ExecutionContext, args: List[str]) -> Dict[str, Any]:
    logger = context.get_logger("extract_summary_block")
    config = context.get_config("extraction.settings", {})
    
    logger.info("Starting summary extraction", extra={
        "correlation_id": context.get_correlation_id(),
        "args": args
    })
    
    # Node implementation
    result = perform_extraction(args[0], config)
    
    logger.info("Extraction completed", extra={
        "result_size": len(result),
        "status": "success"
    })
    
    return result
```

---

## Node Testing

### Test Structure

```
my_node/
├── node.onex.yaml
├── src/
│   └── my_node.py
├── tests/
│   ├── test_my_node.py
│   ├── fixtures/
│   │   ├── input_data.json
│   │   └── expected_output.json
│   └── integration/
│       └── test_integration.py
└── README.md
```

### Test Implementation

```python
# tests/test_my_node.py
import pytest
from unittest.mock import Mock
from my_node import execute

def test_node_execution_success():
    # Mock execution context
    context = Mock()
    context.get_logger.return_value = Mock()
    context.get_config.return_value = {}
    context.get_correlation_id.return_value = "test-123"
    
    # Test execution
    result = execute(context, ["test_input"])
    
    # Assertions
    assert result is not None
    assert "status" in result
    assert result["status"] == "success"

def test_node_execution_with_invalid_input():
    context = Mock()
    context.get_logger.return_value = Mock()
    
    with pytest.raises(ValueError):
        execute(context, [])
```

---

## Node Registry Integration

### Registration

```bash
# Register node in local registry
onex registry register my_node/node.onex.yaml

# Register with remote registry
onex registry register my_node/node.onex.yaml --remote https://registry.example.com

# Verify registration
onex registry verify my_node
```

### Discovery

```bash
# Discover nodes
onex list-nodes

# Search nodes
onex list-nodes --search "validator"

# Get node information
onex node-info my_node --version 1.0.0
```

---

## Schema Extensions

### Extension Points

The ONEX node schema supports extensions via:

- `x-extensions` field for custom metadata
- Schema versioning for backward compatibility
- Plugin-specific fields with reserved namespaces

### Custom Extensions

```yaml
# Custom extensions example
x-extensions:
  my-org:
    deployment_target: "kubernetes"
    resource_requirements:
      cpu: "500m"
      memory: "1Gi"
    monitoring:
      metrics_enabled: true
      alerts:
        - name: "high_error_rate"
          threshold: 0.05
```

---

## Security Considerations

### Node Validation

- All nodes must pass schema validation
- Cryptographic signatures verify node integrity
- Trust scores track execution history
- Capability-based permissions limit node access

### Secure Execution

```yaml
# Security configuration
security:
  sandbox_enabled: true
  allowed_capabilities:
    - "file.read:/tmp/*"
    - "network.connect:api.example.com"
  denied_capabilities:
    - "file.write:/etc/*"
    - "process.execute:*"
  execution_timeout: 300
  memory_limit: "1Gi"
```

---

## Performance Optimization

### Node Caching

```yaml
# Caching configuration
caching:
  enabled: true
  ttl: 3600  # 1 hour
  cache_key_fields:
    - "input_hash"
    - "node_version"
  cache_backend: "redis"
```

### Parallel Execution

```bash
# Execute multiple nodes in parallel
onex run --parallel node1,node2,node3

# Execute with resource limits
onex run my_node --max-memory 512M --max-cpu 2
```

---

## Integration Examples

### CI/CD Integration

```yaml
# .github/workflows/onex.yml
name: ONEX Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup ONEX
        run: |
          pip install onex-cli
          onex version
      
      - name: Validate nodes
        run: |
          onex run parity_validator_node
          onex validate --all
      
      - name: Run tests
        run: |
          onex test --coverage
```

### Docker Integration

```dockerfile
# Dockerfile for ONEX node
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY node.onex.yaml .
COPY src/ ./src/
COPY tests/ ./tests/

# Validate node on build
RUN onex validate node.onex.yaml

ENTRYPOINT ["onex", "run"]
CMD ["my_node"]
```

---

## Cross-References

- [ONEX Node Schema](../schemas/onex_node.yaml)
- [Execution Result Schema](../schemas/execution_result.json)
- [State Contract Schema](../schemas/state_contract.json)
- [Lifecycle Policy](./lifecycle_policy.md)
- [Registry Architecture](./registry.md)
- [Testing Standards](./testing.md)

---

## Schema Evolution

### Version Management

- All schemas include `schema_version` field
- Additive changes allowed in minor versions
- Breaking changes require new major version
- Backward compatibility maintained for deprecated fields

### Migration Support

```bash
# Check schema compatibility
onex schema check --target-version 0.2.0

# Migrate node to new schema version
onex schema migrate my_node --to-version 0.2.0

# Validate migration
onex validate my_node --schema-version 0.2.0
```

---

**Note:** This specification defines the current ONEX node model and will evolve as the platform matures. All changes follow semantic versioning and maintain backward compatibility where possible. 