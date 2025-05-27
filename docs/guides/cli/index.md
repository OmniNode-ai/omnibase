# ONEX CLI Guide

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Comprehensive guide to using the ONEX command-line interface  
> **Audience:** New users, developers, system administrators  

---

## Overview

This guide covers the ONEX command-line interface, including installation, quickstart, and advanced usage. The ONEX CLI is the primary way to interact with the ONEX ecosystem, providing powerful tools for node management, file operations, validation, and system administration.

---

## Quick Navigation

- **[Getting Started](../getting_started.md)** - Environment setup and first-run instructions
- **[CLI Quickstart](../cli_quickstart.md)** - Essential commands and workflows
- **[CLI Examples](../../cli_examples.md)** - Comprehensive usage examples

---

## CLI Overview

### Essential Commands

```bash
# Get general help
onex --help

# Show all available commands
onex list-nodes

# Get help for specific commands
onex run --help
onex validate --help
onex stamp --help
```

### Core Operations

```bash
# Run nodes
onex run parity_validator_node
onex run stamper_node --args='["file", "README.md"]'

# Validate files and metadata
onex validate path/to/file.py
onex validate src/omnibase/nodes/

# Stamp files with metadata
onex stamp file **/*.py
onex stamp file **/*.yaml
```

### System Information

```bash
# Get system information
onex info

# Get version information
onex version

# List available file handlers
onex handlers list
```

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Poetry (recommended) or pip

### Quick Install

```bash
# Using Poetry (recommended)
poetry install
poetry run onex --help

# Using pip
pip install -e .
onex --help
```

For detailed installation instructions, see the [Getting Started Guide](../getting_started.md).

---

## Basic Usage Examples

### Node Operations

```bash
# List all available nodes
onex list-nodes

# Get detailed information about a node
onex node-info stamper_node
onex node-info parity_validator_node --version v1_0_0

# Run a node with introspection
onex run stamper_node --introspect
onex run parity_validator_node --introspect

# List available versions for a node
onex run stamper_node --list-versions
```

### File Operations

```bash
# Stamp specific files
onex stamp file README.md
onex stamp file src/omnibase/core/registry.py

# Stamp multiple file types
onex stamp file **/*.py
onex stamp file **/*.yaml
onex stamp file **/*.md

# Validate files
onex validate path/to/file.py
onex validate src/omnibase/nodes/
onex validate src/omnibase/core/
```

### Validation Operations

```bash
# Run ecosystem validation
onex run parity_validator_node

# Validate with specific output format
onex run parity_validator_node --args='["--format", "summary"]'
onex run parity_validator_node --args='["--format", "detailed"]'
onex run parity_validator_node --args='["--format", "json"]'

# Validate specific types
onex run parity_validator_node --args='["--validation-types", "introspection_validity"]'
onex run parity_validator_node --args='["--validation-types", "metadata_compliance"]'
```

---

## Advanced Usage

### Output Formats

The ONEX CLI supports multiple output formats:

```bash
# Human-readable output (default)
onex run parity_validator_node

# JSON for automation
onex run parity_validator_node --args='["--format", "json"]'

# Detailed output for debugging
onex run parity_validator_node --args='["--format", "detailed", "--verbose"]'
```

### Performance and Debugging

```bash
# Include performance metrics
onex run parity_validator_node --args='["--include-performance-metrics"]'

# Verbose output with detailed logging
onex run parity_validator_node --args='["--verbose"]'

# Debug mode
onex --debug run node_name

# Combine options for comprehensive analysis
onex run parity_validator_node --args='["--format", "detailed", "--include-performance-metrics", "--verbose"]'
```

---

## Common Workflows

### Development Workflow

```bash
# 1. Check ecosystem health
onex run parity_validator_node --args='["--format", "summary"]'

# 2. Stamp modified files
onex stamp file path/to/modified/file.py

# 3. Regenerate project tree
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# 4. Validate changes
onex validate src/omnibase/nodes/my_node/

# 5. Run comprehensive validation
onex run parity_validator_node
```

### Node Development Workflow

```bash
# Create new node structure
mkdir -p src/omnibase/nodes/my_node/v1_0_0

# Stamp new files
onex stamp file src/omnibase/nodes/my_node/v1_0_0/*.py
onex stamp file src/omnibase/nodes/my_node/v1_0_0/*.yaml

# Validate node structure
onex validate src/omnibase/nodes/my_node/

# Test node execution
onex run my_node --introspect
```

---

## Configuration

### CLI Configuration

The ONEX CLI can be configured through:

- Environment variables
- Configuration files
- Command-line options
- Runtime parameters

For detailed configuration options, see the [Configuration Guide](../../configuration.md).

### Environment Variables

```bash
# Set debug mode
export ONEX_DEBUG=true

# Set custom configuration path
export ONEX_CONFIG_PATH=/path/to/config

# Set verbose output
export ONEX_VERBOSE=true
```

---

## Troubleshooting

### Common Issues

#### Command Not Found
```bash
# Check if ONEX is installed
pip list | grep omnibase

# Verify Python environment
which python
python --version

# Try using full path
python -m omnibase.cli_tools.onex.v1_0_0.cli_main --help
```

#### Permission Errors
```bash
# Check file permissions
ls -la path/to/file

# Ensure write access to directories
chmod +w path/to/directory
```

#### Validation Failures
```bash
# Get detailed error information
onex run parity_validator_node --args='["--format", "detailed", "--verbose"]'

# Validate specific files
onex validate --schema node_metadata file.yaml

# Check system status
onex info
```

### Debug Commands

```bash
# Run with debug output
onex --debug run node_name

# Run with verbose output
onex --verbose run node_name

# Check system information
onex info

# Verify node availability
onex list-nodes
```

---

## Integration

### CI/CD Integration

```bash
#!/bin/bash
# CI validation script

# Run ecosystem validation
onex run parity_validator_node --args='["--format", "json"]' > validation_results.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Validation passed"
else
    echo "❌ Validation failed"
    cat validation_results.json
    exit 1
fi
```

### Pre-commit Integration

```bash
#!/bin/bash
# Pre-commit hook

# Stamp modified files
onex stamp file $(git diff --cached --name-only --diff-filter=AM | grep -E '\.(py|yaml|md)$')

# Run quick validation
onex run parity_validator_node --args='["--format", "summary"]'
```

---

## Advanced Topics

### Custom Templates

Future functionality for scaffolding new nodes and components:

```bash
# Scaffold new node (planned)
onex scaffold node my_new_node

# Scaffold new handler (planned)
onex scaffold handler my_handler
```

### Plugin Management

```bash
# List available plugins (planned)
onex plugins list

# Install plugin (planned)
onex plugins install my_plugin

# Configure plugin (planned)
onex plugins configure my_plugin
```

---

## Performance Tips

### Efficient Operations

```bash
# Use specific patterns instead of **/*
onex stamp file src/omnibase/nodes/**/*.py

# Validate specific directories
onex validate src/omnibase/nodes/specific_node/

# Use summary format for quick checks
onex run parity_validator_node --args='["--format", "summary"]'
```

### Batch Operations

```bash
# Stamp multiple file types efficiently
onex stamp file **/*.py **/*.yaml **/*.md

# Validate multiple directories
onex validate src/omnibase/nodes/ src/omnibase/core/

# Use specific validation types for faster execution
onex run parity_validator_node --args='["--validation-types", "file_structure"]'
```

---

## References

- **[Getting Started Guide](../getting_started.md)** - Complete setup and installation
- **[CLI Quickstart](../cli_quickstart.md)** - Essential commands and workflows
- **[CLI Examples](../../cli_examples.md)** - Comprehensive usage examples
- **[Configuration Guide](../../configuration.md)** - Configuration options and setup
- **[Developer Guide](../../developer_guide.md)** - Development best practices
- **[Error Handling](../../error_handling.md)** - Understanding error patterns

---

**Note:** This guide provides a comprehensive overview of the ONEX CLI. For specific examples and advanced usage patterns, see the linked documentation throughout this guide. 