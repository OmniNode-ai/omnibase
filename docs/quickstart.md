<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:27.012631'
description: Stamped by ONEX
entrypoint: python://quickstart.md
hash: da4c68dd51783826c596ceff71d95ce8a89f41afda2903f37588b350b0ca10ca
last_modified_at: '2025-05-29T11:50:15.283184+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: quickstart.md
namespace: omnibase.quickstart
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 1680469e-7c76-4369-a7be-898753293457
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# ONEX Node Author Quickstart Guide

Welcome to the ONEX/OmniBase Node Author Quickstart! This guide will help you create, document, and validate a new ONEX node using the canonical tools, schemas, and best practices.

---

## Prerequisites
- Python 3.11 (use Poetry for environment management)
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
  poetry run python src/omnibase/tools/cli_validate.py node.onex.yaml
  poetry run python src/omnibase/tools/cli_validate.py state_contract.yaml
  ```
- **Run all tests:**
  ```bash
  poetry run pytest
  ```
- **Check schema compliance:**
  - All metadata and state files must pass schema validation (see [schemas](../src/omnibase/schemas/)).

---

## 3. Document Your Node

- **Generate Markdown docs for all schemas:**
  ```bash
  poetry run python src/omnibase/tools/docstring_generator.py --output-dir docs/generated --verbose
  ```
- **Review generated docs:**
  - See `docs/generated/` for up-to-date schema documentation.

---

## 4. Checklist for New Contributors

- [ ] All required metadata fields are present and valid
- [ ] State contract is defined and matches node logic
- [ ] All code and tests are present and passing
- [ ] Metadata and state files pass schema validation
- [ ] Documentation is generated and reviewed
- [ ] Follows naming conventions and directory structure ([standards](./standards.md))

---

## 5. Resources & Canonical Docs
- [Canonical Schemas](../src/omnibase/schemas/)
- [Schema Documentation](./generated/)
- [Naming & Structural Standards](./standards.md)
- [Testing Philosophy](./testing.md)
- [Registry & Metadata Guide](./registry.md)

---

**Welcome to the ONEX ecosystem!**

For questions or to request a review, open a PR or contact the Foundation team.
