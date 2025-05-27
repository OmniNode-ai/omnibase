# ONEX Node Author Quickstart Guide

Welcome to the ONEX/OmniBase Node Author Quickstart! This guide will help you create, document, and validate a new ONEX node using the canonical tools, schemas, and best practices.

---

## Prerequisites
- Python 3.11+ (use Poetry for environment management)
- Install dependencies:
  ```bash
  poetry install
  ```
- Familiarity with YAML/JSON and Markdown

---

## 1. Create a New Node

1. **Scaffold your node directory:**
   ```bash
   mkdir my_node && cd my_node
   ```

2. **Create a metadata file:**
   - Copy and edit the canonical template:
     ```bash
     cp ../src/omnibase/templates/node_metadata.yaml.tmpl node.onex.yaml
     ```
   - Fill in all required fields (see [onex_node.yaml](../src/omnibase/schemas/onex_node.yaml)).

3. **Create a state contract:**
   - Copy and edit the stub:
     ```bash
     cp ../src/omnibase/schemas/state_contract.yaml state_contract.yaml
     ```
   - Define your node's state structure as needed.

4. **Add your code and tests:**
   - Implement your node logic (e.g., `main.py`).
   - Add tests in a `tests/` subdirectory.

---

## 2. Validate Your Node

- **Validate metadata and state contract:**
  ```bash
  onex validate node.onex.yaml
  onex validate state_contract.yaml
  ```

- **Run all tests:**
  ```bash
  poetry run pytest
  ```

- **Check schema compliance:**
  - All metadata and state files must pass schema validation (see [schemas](../src/omnibase/schemas/)).

- **Run parity validation:**
  ```bash
  onex run parity_validator_node
  ```

---

## 3. Document Your Node

- **Generate Markdown docs for all schemas:**
  ```bash
  onex run schema_generator_node --args='["--output-dir", "docs/generated", "--verbose"]'
  ```

- **Review generated docs:**
  - See `docs/generated/` for up-to-date schema documentation.

---

## 4. CLI Commands Reference

### Basic Node Operations

```bash
# List all available nodes
onex list-nodes

# Get detailed info about a specific node
onex node-info my_node

# Run a node with arguments
onex run my_node --args='["arg1", "arg2"]'

# Get node introspection
onex run my_node --introspect

# Run with specific version
onex run my_node --version v1_0_0
```

### File Operations

```bash
# Stamp files with metadata
onex stamp file path/to/file.py
onex stamp file **/*.py
onex stamp file **/*.yaml

# Validate files
onex validate path/to/file.py
onex validate src/omnibase/nodes/
```

### System Information

```bash
# Get system info
onex info

# Get version
onex version

# List handlers
onex handlers list
```

---

## 5. Testing Your Node

### Run Tests with Different Contexts

```bash
# Run all tests
poetry run pytest

# Run only mock-tier tests (fast)
poetry run pytest -m "mock or (not integration and not external)"

# Run only integration-tier tests
poetry run pytest -m "integration"
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run all pre-commit hooks
pre-commit run --all-files

# Run specific hooks
pre-commit run metadata-stamper --all-files
pre-commit run onextree-generator --all-files
```

---

## 6. Node Structure Best Practices

### Directory Layout

```
my_node/
├── v1_0_0/
│   ├── node.py                 # Main node implementation
│   ├── node.onex.yaml         # Node metadata
│   ├── contract.yaml          # State contract
│   ├── adapters/              # CLI and other adapters
│   │   └── cli_adapter.py
│   ├── tests/                 # Node tests
│   │   ├── test_node.py
│   │   └── fixtures/
│   │       └── sample_input.yaml
│   └── README.md              # Node documentation
```

### Metadata Requirements

Your `node.onex.yaml` must include:

```yaml
metadata_version: "0.1.0"
protocol_version: "1.0.0"
schema_version: "1.1.0"
uuid: "your-unique-uuid-here"
name: "my_node"
namespace: "your.namespace.here"
version: "1.0.0"
author: "Your Name"
description: "Description of what your node does"
lifecycle: "active"
entrypoint:
  type: "python"
  target: "node.py"
runtime_language_hint: "python>=3.11"
meta_type: "tool"
```

---

## 7. Checklist for New Contributors

- [ ] All required metadata fields are present and valid
- [ ] State contract is defined and matches node logic
- [ ] All code and tests are present and passing
- [ ] Metadata and state files pass schema validation
- [ ] Documentation is generated and reviewed
- [ ] Follows naming conventions and directory structure
- [ ] Pre-commit hooks are installed and passing
- [ ] Node passes parity validation

---

## 8. Common Workflows

### After Making Changes

```bash
# 1. Regenerate .onextree
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# 2. Stamp new/modified files
onex stamp file path/to/modified/file.py

# 3. Run tests to verify changes
poetry run pytest

# 4. Run pre-commit hooks before committing
pre-commit run --all-files

# 5. Validate ecosystem compliance
onex run parity_validator_node
```

### Node Development Cycle

```bash
# 1. Create node structure
mkdir my_node/v1_0_0 && cd my_node/v1_0_0

# 2. Implement node
# ... write your code ...

# 3. Test node
poetry run pytest

# 4. Validate node
onex validate node.onex.yaml
onex run parity_validator_node --args='["--nodes-directory", "my_node"]'

# 5. Document node
onex run schema_generator_node

# 6. Commit changes
git add . && git commit -m "Add my_node implementation"
```

---

## 9. Resources & Canonical Docs

- [Canonical Schemas](../src/omnibase/schemas/)
- [Schema Documentation](./generated/)
- [Naming & Structural Standards](./standards.md)
- [Testing Philosophy](./testing.md)
- [Registry & Metadata Guide](./registry.md)
- [CLI Interface Reference](./cli_interface.md)
- [Core Protocols](./reference-protocols-core.md)
- [Registry Protocols](./reference-protocols-registry.md)

---

## 10. Getting Help

- **Documentation**: Start with [docs/index.md](./index.md) for the main documentation hub
- **CLI Help**: Use `onex --help` or `onex <command> --help` for command-specific help
- **Node Examples**: Look at existing nodes in `src/omnibase/nodes/` for reference implementations
- **Testing**: See [testing.md](./testing.md) for comprehensive testing guidelines

---

**Welcome to the ONEX ecosystem!**

For questions or to request a review, open a PR or contact the development team. 