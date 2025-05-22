<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: quickstart.md
version: 1.0.0
uuid: 5af92b4f-d6ec-4226-bc4b-7d8d196e4edc
author: OmniNode Team
created_at: 2025-05-22T17:18:16.692012
last_modified_at: 2025-05-22T21:19:13.545970
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b1fead6f179f12eddb493361c831591eab3b8170af657861826368427cc77224
entrypoint: python@quickstart.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.quickstart
meta_type: tool
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
