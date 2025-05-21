<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: getting_started.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 68f37b4e-99a7-4ee7-a1a1-72594762d73e -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158416 -->
<!-- last_modified_at: 2025-05-21T16:42:46.085898 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 9aafcd89e8b471711a56a5c8bdab0adbe56572c17e7a49a3e80ebde57ec34f9e -->
<!-- entrypoint: {'type': 'python', 'target': 'getting_started.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.getting_started -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: getting_started.md -->
<!-- version: 1.0.0 -->
<!-- uuid: da9b8c4e-dec9-4778-8ab7-b92e445c4d64 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.433429 -->
<!-- last_modified_at: 2025-05-21T16:39:56.062843 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 301a1e82cd4fb87784bc98ca7545b0c3dc6b8aa49d1aea9073290217820eb3b4 -->
<!-- entrypoint: {'type': 'python', 'target': 'getting_started.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.getting_started -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: getting_started.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 6a9f93a8-e423-45fb-b0eb-0cbfa3976107 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.661722 -->
<!-- last_modified_at: 2025-05-21T16:24:00.297480 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 14484c7d1f3e7ffd6b7a47666141b4c1d6211876843ef823e1eba7e370b488bf -->
<!-- entrypoint: {'type': 'python', 'target': 'getting_started.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.getting_started -->
<!-- meta_type: tool -->
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
