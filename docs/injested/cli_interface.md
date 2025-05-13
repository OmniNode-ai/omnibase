# OmniBase Canonical CLI Interface and Formatter Output

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

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

---

## Output Format Flags

| Flag             | Audience             | Characteristics                          |
|------------------|----------------------|-------------------------------------------|
| `--format human` | Interactive (TTY)    | ANSI color, emoji, concise layout         |
| `--format json`  | CI and scripting     | Canonical structure, stable key order     |
| `--format yaml`  | Agents, debug users  | Readable, anchors and multiline support   |

Auto-selects based on `isatty`, with `json` as fallback if non-TTY.

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

> Don’t show me logs. Show me understanding.