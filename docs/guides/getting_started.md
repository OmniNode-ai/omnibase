<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: getting_started.md
version: 1.0.0
uuid: 3a3b30b7-cd20-4e73-a101-747eb8338855
author: OmniNode Team
created_at: 2025-05-22T17:18:16.683698
last_modified_at: 2025-05-22T21:19:13.505587
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 0aa5c6712861abc696652d8ef429fc3a1f5c0fc1573a1708110838558d908ebd
entrypoint: python@getting_started.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.getting_started
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Getting Started with ONEX

This guide will help you set up your development environment, install ONEX in editable mode, and verify your installation with basic commands and validation.

---


> 📝 Note: If you're using Poetry, you do **not** need to manually create a virtual environment. Poetry handles environment creation and isolation automatically. Use `poetry install` and `poetry run` to manage dependencies and run commands.

## 1. Set Up a Virtual Environment

### Using venv (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Using conda (optional)
```bash
conda create -n onex python=3.11
conda activate onex
```

---

## 2. Install ONEX in Editable Mode

```bash
pip install -e .
```

---

## 3. Run the ONEX CLI

```bash
onex --help
```

---

## 4. Validate an Example Node

```bash
onex validate nodes/example_node/node.onex.yaml
```

---

## 5. Confirm Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

---

## 6. Common Errors and How to Resolve Them

- **ModuleNotFoundError:** Ensure your virtual environment is activated and ONEX is installed in editable mode.
- **onex: command not found:** Make sure your Python environment's bin directory is in your PATH, and that the install step completed successfully.
- **Pre-commit hook failures:** Run `pre-commit run --all-files` and fix any reported issues before committing.
- **Schema validation errors:** Check that your `.onex.yaml` files conform to the latest schema in `src/omnibase/schema/schemas/`.

---

For more help, see the [Developer Guide](../nodes/developer_guide.md) or ask in the project chat.
