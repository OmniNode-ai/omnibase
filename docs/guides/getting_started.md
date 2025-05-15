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
