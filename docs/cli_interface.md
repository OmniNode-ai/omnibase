<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: e84a8883-24d0-4c91-994a-4f77a5d4911c -->
<!-- name: cli_interface.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:02.503708 -->
<!-- last_modified_at: 2025-05-19T16:20:02.503713 -->
<!-- description: Stamped Markdown file: cli_interface.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 91cca9c643104758d015301dd5efb8f7d7faa650acd24153c7844a5d0854c419 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'cli_interface.md'} -->
<!-- namespace: onex.stamped.cli_interface.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# OmniBase Canonical CLI Interface and Formatter Output

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

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

Formatters are registered in:

```python
omnibase.cli.formatters.FORMATTERS: dict[str, Formatter]
```

Each formatter implements:

```python
class Formatter(Protocol):
    def emit(result: Result) -> str: ...
```

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

---

## JSON Output Example

```json
{
  "status": "fail",
  "messages": ["Missing license header"],
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
  ]
}
```

---

## YAML Output Example

```yaml
status: fail
messages:
  - Missing license header
errors:
  - error_code: VALIDATOR_ERROR_001
    message: Expected header
    severity: error
    location:
      file_path: src/main.py
      line_number: 1
```

---

## CLI Enforcement Rules

- All errors must go through formatter
- `print()` statements are disallowed in CLI subcommands
- CLI must respect config settings and env vars
- Formatter must support fallback if output stream is redirected

---

## Future CLI Enhancements

- [ ] Pipeline editing interface
- [ ] Interactive scaffold wizard
- [ ] Registry diff and changelog tools
- [ ] Output compression (`--gzip`, `--zstd`)
- [ ] Offline cache display and management

---

> Don't show me logs. Show me understanding. 
