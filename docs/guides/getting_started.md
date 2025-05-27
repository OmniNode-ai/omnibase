# Getting Started with ONEX

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Guide for setting up ONEX development environment and basic usage  
> **Audience:** New developers, contributors, system administrators  

---

## Overview

This guide will help you set up your development environment, install ONEX in editable mode, and verify your installation with basic commands and validation. Follow these steps to get up and running with ONEX quickly and efficiently.

---

## Prerequisites

- **Python 3.11+** - ONEX requires Python 3.11 or higher
- **Git** - For cloning the repository and version control
- **Poetry** (recommended) - For dependency management and virtual environments

---

## Installation Methods

### Method 1: Using Poetry (Recommended)

Poetry automatically handles virtual environment creation and dependency management:

```bash
# Clone the repository
git clone <repository-url>
cd omninode_clean

# Install dependencies and create virtual environment
poetry install

# Verify installation
poetry run onex --help
```

> 📝 **Note:** If you're using Poetry, you do **not** need to manually create a virtual environment. Poetry handles environment creation and isolation automatically. Use `poetry install` and `poetry run` to manage dependencies and run commands.

### Method 2: Using Virtual Environment

If you prefer manual virtual environment management:

#### Using venv (recommended)
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install ONEX in editable mode
pip install -e .

# Verify installation
onex --help
```

#### Using conda (optional)
```bash
# Create and activate conda environment
conda create -n onex python=3.11
conda activate onex

# Install ONEX in editable mode
pip install -e .

# Verify installation
onex --help
```

---

## Basic Usage

### 1. Explore Available Commands

```bash
# View all available commands
onex --help

# Get help for specific commands
onex run --help
onex validate --help
onex list-nodes --help
```

### 2. List Available Nodes

```bash
# List all available ONEX nodes
onex list-nodes

# Get detailed information about a specific node
onex node-info stamper_node
```

### 3. Run Your First Node

```bash
# Run a simple validation node
onex run parity_validator_node

# Run with specific arguments
onex run stamper_node --args='["file", "README.md"]'

# Get node introspection information
onex run stamper_node --introspect
```

### 4. Validate Files and Metadata

```bash
# Validate a specific file
onex validate path/to/file.py

# Validate node metadata
onex validate src/omnibase/nodes/stamper_node/

# Validate with specific schema
onex validate --schema node_metadata metadata.yaml
```

### 5. File Operations

```bash
# Stamp files with metadata
onex stamp file **/*.py
onex stamp file **/*.yaml
onex stamp file **/*.md

# Stamp specific files
onex stamp file README.md
onex stamp file src/omnibase/core/registry.py
```

---

## Development Setup

### 1. Install Pre-commit Hooks

Pre-commit hooks ensure code quality and consistency:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run metadata-stamper --all-files
```

### 2. Run Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_specific_module.py

# Run tests with coverage
poetry run pytest --cov=src/omnibase
```

### 3. Generate Documentation Tree

```bash
# Generate .onextree file
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# Validate tree structure
onex validate --schema tree_format .onextree
```

---

## Common Workflows

### Node Development Workflow

```bash
# 1. Create new node structure
mkdir -p src/omnibase/nodes/my_node/v1_0_0

# 2. Create node files
touch src/omnibase/nodes/my_node/v1_0_0/node.py
touch src/omnibase/nodes/my_node/v1_0_0/node.onex.yaml

# 3. Stamp the files
onex stamp file src/omnibase/nodes/my_node/v1_0_0/*.py
onex stamp file src/omnibase/nodes/my_node/v1_0_0/*.yaml

# 4. Validate the node
onex validate src/omnibase/nodes/my_node/

# 5. Test the node
onex run my_node --introspect
```

### File Maintenance Workflow

```bash
# 1. Update files
# ... make your changes ...

# 2. Re-stamp modified files
onex stamp file path/to/modified/file.py

# 3. Regenerate tree
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# 4. Run validation
onex run parity_validator_node

# 5. Run tests
poetry run pytest

# 6. Run pre-commit hooks
pre-commit run --all-files
```

---

## Troubleshooting

### Common Errors and Solutions

#### ModuleNotFoundError
**Problem:** Python can't find ONEX modules
**Solution:** 
- Ensure your virtual environment is activated
- Verify ONEX is installed in editable mode: `pip install -e .`
- Check Python path: `python -c "import sys; print(sys.path)"`

#### onex: command not found
**Problem:** ONEX CLI is not available
**Solution:**
- Make sure your Python environment's bin directory is in your PATH
- Verify installation completed successfully: `pip list | grep omnibase`
- Try using full path: `python -m omnibase.cli_tools.onex.v1_0_0.cli_main`

#### Pre-commit Hook Failures
**Problem:** Pre-commit hooks fail during commit
**Solution:**
- Run hooks manually: `pre-commit run --all-files`
- Fix reported issues before committing
- Check specific hook output for detailed error messages
- Ensure all files are properly stamped

#### Schema Validation Errors
**Problem:** Metadata files don't conform to schema
**Solution:**
- Check schema files in `src/omnibase/schemas/`
- Validate specific files: `onex validate --schema node_metadata file.yaml`
- Review error messages for specific field issues
- Update metadata to match current schema requirements

#### Permission Errors
**Problem:** Cannot write to files or directories
**Solution:**
- Check file permissions: `ls -la path/to/file`
- Ensure you have write access to the directory
- Run with appropriate permissions or change ownership

#### Performance Issues
**Problem:** Commands run slowly
**Solution:**
- Check system resources: `top` or `htop`
- Use `--verbose` flag to see detailed execution
- Profile specific operations: `onex --debug run node_name`
- Consider excluding large directories with `.onexignore`

---

## Next Steps

### Learning Resources

1. **[CLI Examples](../cli_examples.md)** - Comprehensive CLI usage examples
2. **[Developer Guide](../developer_guide.md)** - In-depth development guidelines
3. **[Testing Guide](../testing.md)** - Testing philosophy and practices
4. **[Node Specification](../onex_node_spec.md)** - Complete node development guide

### Advanced Topics

1. **[Registry Architecture](../registry_architecture.md)** - Understanding the ONEX registry
2. **[Error Handling](../error_handling.md)** - Error handling patterns and best practices
3. **[Security](../security.md)** - Security considerations and implementation
4. **[Monitoring](../monitoring.md)** - Observability and monitoring setup

### Community

- **Issues:** Report bugs and request features in the project repository
- **Discussions:** Join community discussions for questions and ideas
- **Contributing:** See [Contributing Guide](../contributing.md) for contribution guidelines

---

## Quick Reference

### Essential Commands

```bash
# Basic operations
onex --help                    # Show help
onex list-nodes               # List available nodes
onex run node_name            # Run a node
onex validate file.yaml       # Validate file

# File operations
onex stamp file **/*.py       # Stamp Python files
onex validate path/           # Validate directory

# Development
pre-commit run --all-files    # Run quality checks
poetry run pytest            # Run tests
onex run parity_validator_node # Validate ecosystem
```

### Important Paths

- **Nodes:** `src/omnibase/nodes/`
- **Schemas:** `src/omnibase/schemas/`
- **CLI Tools:** `src/omnibase/cli_tools/`
- **Documentation:** `docs/`
- **Tests:** `tests/`

---

**Note:** This guide covers the essential steps to get started with ONEX. For more detailed information on specific topics, refer to the linked documentation throughout this guide. 