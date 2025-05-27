# ONEX CLI Quickstart

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Quick introduction to using the ONEX CLI  
> **Audience:** New users, developers, system administrators  

---

## Overview

This guide provides a quick introduction to using the ONEX CLI. The ONEX command-line interface is the primary way to interact with the ONEX ecosystem, providing powerful tools for node management, file operations, validation, and system administration.

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

For detailed installation instructions, see the [Getting Started Guide](getting_started.md).

---

## Essential Commands

### Help and Discovery

```bash
# Get general help
onex --help

# Get help for specific commands
onex run --help
onex validate --help
onex stamp --help

# List all available nodes
onex list-nodes

# Get detailed information about a node
onex node-info stamper_node
onex node-info parity_validator_node --version v1_0_0
```

### Running Nodes

```bash
# Run a node with auto-discovery
onex run parity_validator_node
onex run stamper_node
onex run tree_generator_node

# Run with specific arguments
onex run stamper_node --args='["file", "README.md"]'
onex run parity_validator_node --args='["--format", "summary"]'

# Get node introspection
onex run stamper_node --introspect
onex run parity_validator_node --introspect

# List available versions for a node
onex run stamper_node --list-versions
```

### File Operations

```bash
# Stamp files with metadata
onex stamp file README.md
onex stamp file **/*.py
onex stamp file **/*.yaml
onex stamp file **/*.md

# Stamp directories
onex stamp directory src/

# Validate files
onex validate path/to/file.py
onex validate src/omnibase/nodes/
onex validate src/omnibase/core/
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

### File Maintenance Workflow

```bash
# Stamp all Python files
onex stamp file **/*.py

# Stamp all YAML files
onex stamp file **/*.yaml

# Stamp all Markdown files
onex stamp file **/*.md

# Validate stamped files
onex validate src/omnibase/
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

## Advanced Usage

### Validation with Specific Types

```bash
# Validate only introspection functionality
onex run parity_validator_node --args='["--validation-types", "introspection_validity"]'

# Validate only metadata compliance
onex run parity_validator_node --args='["--validation-types", "metadata_compliance"]'

# Validate only file structure
onex run parity_validator_node --args='["--validation-types", "file_structure"]'

# Validate multiple specific types
onex run parity_validator_node --args='["--validation-types", "introspection_validity,metadata_compliance"]'
```

### Output Formats

```bash
# Human-readable output (default)
onex run parity_validator_node --args='["--format", "summary"]'

# Detailed output
onex run parity_validator_node --args='["--format", "detailed"]'

# JSON output for automation
onex run parity_validator_node --args='["--format", "json"]'
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

## Output Formats

The ONEX CLI supports multiple output formats for different use cases:

### Human Format (Default)
- Colored, formatted output for terminal use
- Easy to read for developers
- Includes visual indicators and formatting

### JSON Format
- Machine-readable structured output
- Perfect for CI/CD pipelines and automation
- Consistent schema for parsing

### YAML Format
- Human-readable structured output
- Good for configuration and inspection
- Easy to edit and version control

### Example Usage

```bash
# Default human format
onex run parity_validator_node

# JSON for automation
onex run parity_validator_node --args='["--format", "json"]' > results.json

# YAML for inspection
onex run parity_validator_node --args='["--format", "yaml"]' > results.yaml
```

---

## Error Handling

### Common Error Patterns

```bash
# Check for specific error types
onex run parity_validator_node --args='["--validation-types", "metadata_compliance"]'

# Get detailed error information
onex run parity_validator_node --args='["--format", "detailed", "--verbose"]'

# Validate specific directories
onex run parity_validator_node --args='["--nodes-directory", "src/omnibase/nodes/problematic_node"]'
```

### Troubleshooting Commands

```bash
# Check system status
onex info

# Verify node availability
onex list-nodes

# Test specific node
onex run node_name --introspect

# Validate file handlers
onex handlers list
```

---

## Integration Examples

### CI/CD Pipeline

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

# Stamp any new files
onex stamp file **/*.py
onex stamp file **/*.yaml

# Regenerate tree
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'
```

### Pre-commit Hook

```bash
#!/bin/bash
# Pre-commit validation

# Stamp modified files
onex stamp file $(git diff --cached --name-only --diff-filter=AM | grep -E '\.(py|yaml|md)$')

# Run quick validation
onex run parity_validator_node --args='["--format", "summary"]'

# Check for validation errors
if [ $? -ne 0 ]; then
    echo "❌ Pre-commit validation failed"
    exit 1
fi

echo "✅ Pre-commit validation passed"
```

---

## Performance Tips

### Efficient File Operations

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

## Quick Reference

### Most Used Commands

```bash
# Daily development
onex run parity_validator_node              # Validate ecosystem
onex stamp file **/*.py                     # Stamp Python files
onex validate src/omnibase/nodes/           # Validate nodes

# Node operations
onex list-nodes                             # List available nodes
onex run node_name --introspect             # Get node info
onex node-info node_name                    # Detailed node info

# System operations
onex info                                   # System information
onex version                                # Version information
onex handlers list                          # Available handlers
```

### Command Patterns

```bash
# Pattern: onex [global-options] command [command-options] [arguments]
onex --debug run parity_validator_node --args='["--verbose"]'
onex --verbose stamp file **/*.py
onex validate --schema node_metadata file.yaml
```

---

## Next Steps

- **[Getting Started Guide](getting_started.md)** - Complete setup and installation
- **[CLI Examples](../cli_examples.md)** - Comprehensive usage examples
- **[Developer Guide](../developer_guide.md)** - Development best practices
- **[Error Handling](../error_handling.md)** - Understanding error patterns

---

**Note:** This quickstart covers the most common CLI operations. For comprehensive examples and advanced usage patterns, see the [CLI Examples](../cli_examples.md) documentation. 