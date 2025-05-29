<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:25.975745'
description: Stamped by ONEX
entrypoint: python://cli_interface.md
hash: caed2ffc641031659d3b3f92813fdedd03e55cb0d5ef1d526f6d58c724b2e89c
last_modified_at: '2025-05-29T11:50:14.666925+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: cli_interface.md
namespace: omnibase.cli_interface
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 20221cc7-02e4-4a77-98e5-61751de6280b
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# OmniBase Canonical CLI Interface and Formatter Output

> **Status:** Canonical  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-21

> **Note:** This document is a technical reference for the CLI interface and output formatting. It is closely related to the [Orchestration Spec](./orchestration.md), [Error Handling Spec](./error_handling.md), and [Registry Spec](./registry.md).

---

## Overview

The CLI is the standard interface for invoking, composing, inspecting, and debugging OmniBase components. All CLI commands adhere to protocol-first interaction and unified output formatting.

---

## CLI Command Structure

```bash
omnibase <command> [subcommand] [options]
```

### Examples

- Run a tool:
  ```bash
  omnibase run tool fix_headers --input path/to/file.py
  ```

- Validate metadata:
  ```bash
  omnibase validate metadata tool_fix_headers.yaml
  ```

- List components:
  ```bash
  omnibase list tools --tag canary --lifecycle stable
  ```

- Visualize dependencies:
  ```bash
  omnibase visualize dependencies tool_fix_headers
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
omnibase stamp directory /path/to/dir --engine in_memory --fixture-context test
```

### Environment Variables

- You can also set `ONEX_ENGINE` and `ONEX_FIXTURE_CONTEXT` environment variables to control engine and fixture selection globally.

#### Example:

```bash
export ONEX_ENGINE=in_memory
export ONEX_FIXTURE_CONTEXT=test
omnibase stamp directory /path/to/dir
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

## Future CLI Enhancements

- [x] Standardized formatter registry with emoji-based human output
- [x] Protocol engine and fixture selection for testing
- [x] Safer defaults with dry run mode
- [ ] Pipeline editing interface
- [ ] Interactive scaffold wizard
- [ ] Registry diff and changelog tools
- [ ] Output compression (`--gzip`, `--zstd`)
- [ ] Offline cache display and management

---

## Metadata Block Formatting Rule

> **Rule:** All stamped files must have exactly one blank line between the closing delimiter of the metadata block and the first non-whitespace content. This is enforced by the ONEX Metadata Stamper and required for standards compliance.

**Example:**

```markdown

# First heading or content starts here
```

---

> Don't show me logs. Show me understanding.

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

## Extensibility

When adding new flags or options to any ONEX CLI tool:
- Always provide both long and short variants if user-facing
- Document the new flag in both this interface doc and cli_examples.md
- Ensure the flag follows the canonical naming and style conventions
- Update CLI help output accordingly
