# OmniBase Canonical CLI Interface and Formatter Output

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Technical reference for the CLI interface and output formatting

> **Note:** This document is closely related to the [Orchestration Spec](./orchestration.md), [Error Handling Spec](./error_handling.md), and [Registry Spec](./registry.md).

---

## Overview

The CLI is the standard interface for invoking, composing, inspecting, and debugging OmniBase components. All CLI commands adhere to protocol-first interaction and unified output formatting.

---

## CLI Command Structure

```bash
onex <command> [subcommand] [options]
```

### Examples

- Run a node:
  ```bash
  onex run stamper_node --args='["file", "path/to/file.py"]'
  ```

- Validate metadata:
  ```bash
  onex validate path/to/file.py
  ```

- List components:
  ```bash
  onex list-nodes
  ```

- Get node information:
  ```bash
  onex node-info stamper_node
  ```

- Run with introspection:
  ```bash
  onex run parity_validator_node --introspect
  ```

See also: [Registry Spec](./registry.md) for component types and metadata.

---

## Output Format Flags

| Flag             | Audience             | Characteristics                          |
|------------------|----------------------|-------------------------------------------|
| `--format human` | Interactive (TTY)    | ANSI color, emoji, concise layout         |
| `--format json`  | CI and scripting     | Canonical structure, stable key order     |
| `--format yaml`  | Agents, debug users  | Readable, anchors and multiline support   |

Auto-selects based on `isatty`, with `json` as fallback if non-TTY.

## Protocol Engine and Fixture Selection

The CLI supports protocol-driven and fixture-injectable execution for tools like the metadata stamper. You can select the protocol engine and fixture context using flags or environment variables.

### Engine Selection

- Use `--engine` to select the protocol engine (e.g., `real`, `in_memory`, `hybrid`).
- Use `--fixture-context` to specify the fixture context for dependency injection (e.g., `test`, `integration`).
- These options are available for all protocol-driven tools and validators.

#### Example:

```bash
onex run stamper_node --args='["directory", "/path/to/dir"]' --engine in_memory --fixture-context test
```

### Environment Variables

- You can also set `ONEX_ENGINE` and `ONEX_FIXTURE_CONTEXT` environment variables to control engine and fixture selection globally.

#### Example:

```bash
export ONEX_ENGINE=in_memory
export ONEX_FIXTURE_CONTEXT=test
onex run stamper_node --args='["directory", "/path/to/dir"]'
```

See [docs/tools/stamper.md](./tools/stamper.md) and [docs/protocols.md](./protocols.md) for more details on protocol-driven and fixture-injectable architecture.

---

## Formatter Registry

All CLI outputs are routed through a central formatter registry that handles consistent formatting across all tools. Formatters are registered in:

```python
omnibase.cli.formatters.FORMATTERS: dict[str, Formatter]
```

Each formatter implements the `Formatter` Protocol:

```python
class Formatter(Protocol):
    def emit(result: Result) -> str: ...
```

### Adding Custom Formatters

To add a custom formatter, register it in the formatter registry:

```python
from omnibase.cli.formatters import FORMATTERS, Formatter
from omnibase.model.model_onex_result import OnexResult

class CustomFormatter(Formatter):
    def emit(self, result: OnexResult) -> str:
        # Custom formatting logic here
        return formatted_output

# Register the formatter
FORMATTERS["custom"] = CustomFormatter()
```

This allows for extensible output formats through a consistent interface.

See also: [Error Handling Spec](./error_handling.md) for result and error models.

---

## Human Output Mode

- Emoji status symbols (fallbacks for `TERM=dumb`)
- ≤100 char lines
- Header/title summaries
- Clear PASS/FAIL/WARN/SKIP block formatting

Emoji map:

| Status | Emoji |
|--------|-------|
| PASS   | ✅    |
| FAIL   | ❌    |
| WARN   | ⚠️    |
| SKIP   | ⏭️    |
| TIME   | ⏱️    |

---

## JSON Output Example

```json
{
  "status": "fail",
  "messages": [
    {
      "summary": "Missing license header", 
      "details": "File must start with license header per policy P-001",
      "severity": "error"
    }
  ],
  "errors": [
    {
      "error_code": "VALIDATOR_ERROR_001",
      "message": "Expected header",
      "severity": "error",
      "location": {
        "file_path": "src/main.py",
        "line_number": 1
      }
    }
  ],
  "metadata": {
    "processed_files": 12,
    "passed": 11,
    "failed": 1
  }
}
```

---

## YAML Output Example

```yaml
status: fail
messages:
  - summary: Missing license header
    details: File must start with license header per policy P-001
    severity: error
errors:
  - error_code: VALIDATOR_ERROR_001
    message: Expected header
    severity: error
    location:
      file_path: src/main.py
      line_number: 1
metadata:
  processed_files: 12
  passed: 11
  failed: 1
```

---

## CLI Enforcement Rules

- All errors must go through formatter
- `print()` statements are disallowed in CLI subcommands
- CLI must respect config settings and env vars
- Formatter must support fallback if output stream is redirected
- Default to dry run mode to prevent accidental file modifications
- Use explicit `--write` or `-w` flag for tools that modify files

---

## Metadata Block Formatting Rule

> **Rule:** All stamped files must have exactly one blank line between the closing delimiter of the metadata block and the first non-whitespace content. This is enforced by the ONEX Metadata Stamper and required for standards compliance.

**Example:**

```markdown
<!-- === /OmniNode:Metadata === -->

# First heading or content starts here
```

---

## Canonical CLI Flag and Option Conventions

All ONEX CLI tools must provide both long and short flag variants for all user-facing options. For example:
- `--gen-block`/`-g` for generating a canonical metadata block
- `--ext`/`-e` for specifying file extension/format
- `--write`/`-w` for enabling file modification
- `--engine` for protocol engine selection
- `--fixture-context` for dependency injection context
- `--format` for output format selection

Use double-dash for long flags and single-dash for short flags. Use kebab-case for multi-word flags. All flags must be documented in the CLI help output.

## CLI Examples Reference

For real, working command lines and usage patterns, see [cli_examples.md](./cli_examples.md). This file is the canonical source for practical CLI usage, while this document defines the interface standards and conventions. Both must be kept in sync as the CLI evolves.

## Node Operations

### Basic Node Commands

```bash
# List all available nodes
onex list-nodes

# Get detailed info about a specific node
onex node-info parity_validator_node
onex node-info stamper_node --version v1_0_0

# Run any node with automatic version resolution
onex run parity_validator_node
onex run stamper_node
onex run tree_generator_node

# Run with specific version
onex run stamper_node --version v1_0_0

# Run with arguments (JSON format)
onex run parity_validator_node --args='["--format", "summary"]'
onex run stamper_node --args='["file", "README.md"]'

# Get node introspection
onex run parity_validator_node --introspect
onex run stamper_node --introspect

# List available versions for a node
onex run stamper_node --list-versions
```

### File Operations

```bash
# Stamp files
onex stamp file path/to/file.py
onex stamp file **/*.py
onex stamp file **/*.yaml
onex stamp file **/*.md

# Validate files
onex validate path/to/file.py
onex validate src/omnibase/nodes/
onex validate src/omnibase/core/
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

## Extensibility

When adding new flags or options to any ONEX CLI tool:
- Always provide both long and short variants if user-facing
- Document the new flag in both this interface doc and cli_examples.md
- Ensure the flag follows the canonical naming and style conventions
- Update CLI help output accordingly

---

## Performance Features

- **Fast execution:** Pre-commit hooks run in 1-2 seconds
- **Auto-discovery:** Instant node discovery and version resolution
- **Professional UX:** Commands comparable to major cloud platforms (AWS, GCP, etc.)
- **Zero-maintenance versioning:** Latest versions auto-resolved, explicit versions still supported 