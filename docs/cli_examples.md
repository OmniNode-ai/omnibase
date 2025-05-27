<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: cli_examples.md
version: 1.0.0
uuid: 074819ab-949e-4cbd-94a2-872d0145f57f
author: OmniNode Team
created_at: 2025-05-27T06:03:05.800016
last_modified_at: 2025-05-27T17:26:51.933294
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 11270987d5469b121acffa1d395ce85708fbd5d356bfc850cf3d5bae7c898134
entrypoint: python@cli_examples.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.cli_examples
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX CLI Examples and Usage Patterns

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Provide practical, real-world examples of ONEX CLI usage patterns and command combinations  
> **Audience:** Node authors, developers, CI engineers, system administrators  
> **Companion:** [CLI Interface Specification](./cli_interface.md)

---

## Overview

This document provides comprehensive, practical examples of using the ONEX CLI tool. These examples demonstrate real-world usage patterns, command combinations, and workflows that developers and operators use daily.

---

## Basic Node Operations

### Running Nodes

```bash
# Run a node with automatic version resolution
onex run parity_validator_node

# Run with specific version
onex run stamper_node --version v1_0_0

# Run with arguments
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# Run with JSON arguments for complex parameters
onex run parity_validator_node --args='["--nodes-directory", "src/omnibase/nodes", "--format", "detailed", "--include-performance-metrics"]'

# Get node introspection
onex run stamper_node --introspect

# List available versions for a node
onex run stamper_node --list-versions
```

### Node Discovery and Information

```bash
# List all available nodes
onex list-nodes

# List nodes with filtering
onex list-nodes --type validator
onex list-nodes --lifecycle active
onex list-nodes --search "tree"

# Get detailed node information
onex node-info parity_validator_node
onex node-info stamper_node --version v1_0_0
onex node-info template_node --show-dependencies
```

---

## File Operations

### Stamping Files

```bash
# Stamp a single file
onex stamp file README.md

# Stamp multiple files with glob patterns
onex stamp file **/*.py
onex stamp file **/*.yaml
onex stamp file **/*.md

# Stamp specific file types
onex stamp file src/omnibase/nodes/**/*.py
onex stamp file src/omnibase/core/**/*.yaml

# Stamp with verbose output
onex stamp file --verbose src/omnibase/tools/cli_main.py

# Stamp and show what would be changed (dry run)
onex stamp file --dry-run **/*.py
```

### Validation

```bash
# Validate a single file
onex validate README.md

# Validate directories
onex validate src/omnibase/nodes/
onex validate src/omnibase/core/

# Validate with specific error categories
onex validate --error-categories SC,MD,LC src/omnibase/

# Validate and output JSON for CI
onex validate --format json src/omnibase/ > validation_report.json

# Validate with specific severity levels
onex validate --severity error,warning src/omnibase/
```

---

## Parity Validator Examples

### Basic Validation

```bash
# Validate all nodes in the ecosystem
onex run parity_validator_node

# Quick ecosystem health check
onex run parity_validator_node --args='["--format", "summary"]'

# Detailed validation report
onex run parity_validator_node --args='["--format", "detailed"]'

# JSON output for CI integration
onex run parity_validator_node --args='["--format", "json"]'
```

### Targeted Validation

```bash
# Validate specific node directory
onex run parity_validator_node --args='["--nodes-directory", "src/omnibase/nodes/logger_node"]'

# Validate specific validation types
onex run parity_validator_node --args='["--validation-types", "introspection_validity"]'
onex run parity_validator_node --args='["--validation-types", "metadata_compliance"]'
onex run parity_validator_node --args='["--validation-types", "file_structure"]'

# Multiple validation types
onex run parity_validator_node --args='["--validation-types", "introspection_validity,metadata_compliance"]'
```

### Advanced Validation

```bash
# Include performance metrics
onex run parity_validator_node --args='["--include-performance-metrics"]'

# Verbose output with detailed logging
onex run parity_validator_node --args='["--verbose"]'

# Comprehensive validation with all options
onex run parity_validator_node --args='["--nodes-directory", "src/omnibase/nodes", "--format", "detailed", "--include-performance-metrics", "--verbose"]'

# Introspection compliance check for all nodes
onex run parity_validator_node --args='["--validation-types", "introspection_validity", "--format", "detailed"]'
```

---

## Tree Generator Examples

### Basic Tree Generation

```bash
# Generate .onextree for current directory
onex run tree_generator_node --args='["--root-directory", ".", "--output-path", ".onextree"]'

# Generate for specific directory
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", "src/.onextree"]'

# Generate with custom output format
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree", "--format", "yaml"]'
```

### Advanced Tree Generation

```bash
# Generate with specific file patterns
onex run tree_generator_node --args='["--root-directory", "src", "--include-patterns", "*.py,*.yaml", "--output-path", ".onextree"]'

# Generate excluding certain directories
onex run tree_generator_node --args='["--root-directory", ".", "--exclude-patterns", "tests/*,docs/*", "--output-path", ".onextree"]'

# Generate with validation
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree", "--validate"]'
```

---

## System Information

### Version and Info

```bash
# Get ONEX version
onex version

# Get detailed system information
onex info

# Get system info with environment details
onex info --verbose

# Check system health
onex info --health-check
```

### Handler Management

```bash
# List all file type handlers
onex handlers list

# List handlers for specific file type
onex handlers list --file-type python

# Get handler details
onex handlers info --handler-name python_stamper

# Test handler on file
onex handlers test --handler-name yaml_stamper --file config.yaml
```

---

## Development Workflows

### Daily Development Workflow

```bash
# 1. After making changes, regenerate .onextree
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# 2. Stamp new/modified files
onex stamp file src/omnibase/nodes/my_new_node.py

# 3. Validate changes
onex run parity_validator_node --args='["--format", "summary"]'

# 4. Run specific validation if needed
onex validate src/omnibase/nodes/my_new_node.py
```

### Pre-commit Workflow

```bash
# Run all pre-commit validations manually
onex run parity_validator_node
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'
onex stamp file **/*.py **/*.yaml **/*.md

# Quick validation before commit
onex run parity_validator_node --args='["--format", "summary"]'
```

### CI/CD Integration Examples

```bash
# CI validation pipeline
onex run parity_validator_node --args='["--format", "json", "--include-performance-metrics"]' > validation_report.json

# Check if .onextree is up to date
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree.tmp"]'
diff .onextree .onextree.tmp || echo "Tree file out of sync"

# Validate specific changed files (in CI)
onex validate $(git diff --name-only HEAD~1 HEAD | grep -E '\.(py|yaml|md)$')
```

---

## Debugging and Troubleshooting

### Debug Mode

```bash
# Run with debug output
onex --debug run parity_validator_node

# Run with verbose logging
onex --verbose run stamper_node --args='["file", "README.md"]'

# Combine debug and verbose
onex --debug --verbose run tree_generator_node --args='["--root-directory", "src"]'
```

### Introspection and Analysis

```bash
# Get detailed node introspection
onex run parity_validator_node --introspect

# Analyze node capabilities
onex node-info parity_validator_node --show-capabilities

# Check node dependencies
onex node-info stamper_node --show-dependencies --recursive

# Verify node metadata
onex validate src/omnibase/nodes/parity_validator_node/node.onex.yaml
```

### Error Investigation

```bash
# Validate with specific error codes
onex validate --error-codes SC002,MD001 src/omnibase/

# Get detailed error information
onex validate --format json --verbose src/omnibase/ | jq '.errors[] | select(.severity == "error")'

# Check for specific validation types
onex run parity_validator_node --args='["--validation-types", "metadata_compliance", "--format", "detailed"]'
```

---

## Advanced Usage Patterns

### Batch Operations

```bash
# Stamp all Python files in multiple directories
find src/omnibase -name "*.py" -exec onex stamp file {} \;

# Validate multiple node directories
for dir in src/omnibase/nodes/*/; do
  echo "Validating $dir"
  onex run parity_validator_node --args='["--nodes-directory", "'$dir'"]'
done

# Generate multiple tree files
onex run tree_generator_node --args='["--root-directory", "src/omnibase/nodes", "--output-path", "nodes.onextree"]'
onex run tree_generator_node --args='["--root-directory", "src/omnibase/core", "--output-path", "core.onextree"]'
```

### Pipeline Integration

```bash
# Validation pipeline with error handling
onex run parity_validator_node --args='["--format", "json"]' | \
  jq -r '.summary.total_errors' | \
  xargs -I {} sh -c 'if [ {} -gt 0 ]; then exit 1; fi'

# Conditional stamping based on file changes
git diff --name-only HEAD~1 HEAD | grep -E '\.(py|yaml|md)$' | \
  xargs -I {} onex stamp file {}

# Generate reports for multiple formats
onex run parity_validator_node --args='["--format", "json"]' > report.json
onex run parity_validator_node --args='["--format", "detailed"]' > report.txt
```

### Performance Monitoring

```bash
# Time node execution
time onex run parity_validator_node

# Monitor resource usage during validation
onex run parity_validator_node --args='["--include-performance-metrics", "--format", "json"]' | \
  jq '.performance_metrics'

# Profile specific operations
onex --verbose run tree_generator_node --args='["--root-directory", "src/omnibase"]' 2>&1 | \
  grep -E "(duration|time|performance)"
```

---

## Configuration Examples

### Environment-Specific Commands

```bash
# Development environment
export ONEX_ENV=development
onex run parity_validator_node --args='["--format", "detailed", "--verbose"]'

# Production environment
export ONEX_ENV=production
onex run parity_validator_node --args='["--format", "json"]'

# CI environment
export ONEX_ENV=ci
onex run parity_validator_node --args='["--format", "json", "--include-performance-metrics"]'
```

### Custom Configuration

```bash
# Use custom configuration file
onex --config custom-config.yaml run parity_validator_node

# Override specific configuration values
onex run parity_validator_node --args='["--config-override", "validation.strict_mode=true"]'

# Use configuration from environment
export ONEX_VALIDATION_STRICT_MODE=true
onex run parity_validator_node
```

---

## Output Formatting Examples

### JSON Output for Automation

```bash
# Get JSON output for parsing
onex run parity_validator_node --args='["--format", "json"]' | jq '.'

# Extract specific information
onex list-nodes --format json | jq '.nodes[] | select(.type == "validator")'

# Filter validation results
onex validate --format json src/omnibase/ | jq '.errors[] | select(.severity == "error")'
```

### Human-Readable Output

```bash
# Detailed human-readable output
onex run parity_validator_node --args='["--format", "detailed"]'

# Summary output for quick overview
onex run parity_validator_node --args='["--format", "summary"]'

# Table format for structured data
onex list-nodes --format table

# Verbose output with additional context
onex --verbose run stamper_node --args='["file", "README.md"]'
```

---

## Error Handling Examples

### Graceful Error Handling

```bash
# Continue on errors
onex validate src/omnibase/ || echo "Validation failed but continuing..."

# Exit on first error
set -e
onex run parity_validator_node

# Capture and analyze errors
onex validate --format json src/omnibase/ > validation.json
if [ $(jq '.summary.total_errors' validation.json) -gt 0 ]; then
  echo "Validation errors found:"
  jq '.errors[] | select(.severity == "error")' validation.json
  exit 1
fi
```

### Error Recovery

```bash
# Retry on failure
for i in {1..3}; do
  onex run parity_validator_node && break
  echo "Attempt $i failed, retrying..."
  sleep 5
done

# Fallback to alternative approach
onex run parity_validator_node --args='["--format", "json"]' || \
  onex run parity_validator_node --args='["--format", "summary"]'
```

---

## Integration with Other Tools

### Git Integration

```bash
# Pre-commit hook example
#!/bin/bash
# Stamp changed files
git diff --cached --name-only | grep -E '\.(py|yaml|md)$' | xargs onex stamp file

# Validate changed files
git diff --cached --name-only | grep -E '\.(py|yaml|md)$' | xargs onex validate

# Update .onextree if needed
if git diff --cached --name-only | grep -q '\.py$'; then
  onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'
  git add .onextree
fi
```

### Docker Integration

```bash
# Run ONEX in Docker container
docker run --rm -v $(pwd):/workspace onex/cli:latest run parity_validator_node

# Use Docker for isolated validation
docker run --rm -v $(pwd):/workspace onex/cli:latest validate /workspace/src/omnibase/

# Docker-based CI pipeline
docker run --rm -v $(pwd):/workspace onex/cli:latest run parity_validator_node --args='["--format", "json"]'
```

### Make Integration

```makefile
# Makefile targets
.PHONY: validate stamp tree

validate:
	onex run parity_validator_node --args='["--format", "summary"]'

stamp:
	onex stamp file **/*.py **/*.yaml **/*.md

tree:
	onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

ci: tree stamp validate
	@echo "CI pipeline completed successfully"
```

---

## Performance Tips

### Optimizing Command Execution

```bash
# Use specific node directories for faster validation
onex run parity_validator_node --args='["--nodes-directory", "src/omnibase/nodes/specific_node"]'

# Use summary format for quick checks
onex run parity_validator_node --args='["--format", "summary"]'

# Parallel execution where possible
onex run parity_validator_node --args='["--parallel"]' &
onex run tree_generator_node --args='["--root-directory", "src"]' &
wait
```

### Caching and Incremental Operations

```bash
# Only stamp changed files
git diff --name-only HEAD~1 HEAD | grep -E '\.(py|yaml|md)$' | xargs onex stamp file

# Incremental validation
onex validate $(find src/omnibase -name "*.py" -newer .last_validation)
touch .last_validation

# Cache validation results
onex run parity_validator_node --args='["--format", "json"]' > .validation_cache.json
```

---

## Troubleshooting Common Issues

### Node Discovery Issues

```bash
# Check if node is discoverable
onex list-nodes | grep my_node

# Verify node metadata
onex node-info my_node --verbose

# Check .onextree file
onex validate .onextree

# Regenerate .onextree if corrupted
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'
```

### Validation Failures

```bash
# Get detailed error information
onex validate --format json --verbose problematic_file.py

# Check specific error categories
onex validate --error-categories SC,MD problematic_file.py

# Validate with introspection
onex run parity_validator_node --args='["--validation-types", "introspection_validity", "--verbose"]'
```

### Performance Issues

```bash
# Profile node execution
time onex run parity_validator_node --args='["--include-performance-metrics"]'

# Check system resources
onex info --health-check

# Use targeted validation
onex run parity_validator_node --args='["--nodes-directory", "specific/path"]'
```

---

## Best Practices

### Command Organization

1. **Use consistent formatting**: Always use the same argument format for similar operations
2. **Leverage automation**: Create scripts for common command combinations
3. **Monitor performance**: Use performance metrics to optimize workflows
4. **Handle errors gracefully**: Always include error handling in scripts
5. **Document custom workflows**: Create team-specific documentation for complex workflows

### Development Workflow

1. **Validate early and often**: Run validation after each significant change
2. **Keep .onextree updated**: Regenerate after adding/removing files
3. **Use appropriate output formats**: JSON for automation, detailed for debugging
4. **Leverage introspection**: Use `--introspect` to understand node capabilities
5. **Monitor CI performance**: Track validation times and optimize as needed

---

## References

- [CLI Interface Specification](./cli_interface.md)
- [Testing Standards](./testing.md)
- [Error Handling](./error_handling.md)
- [Node Specification](./onex_node_spec.md)

---

**Note:** This document provides practical examples of ONEX CLI usage. For interface specifications and formal command definitions, see the [CLI Interface Specification](./cli_interface.md).
