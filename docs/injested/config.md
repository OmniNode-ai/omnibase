# OmniBase Config System & Environment Mapping

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase uses a layered, schema-validated configuration system with deterministic override behavior. This ensures consistent execution across environments while remaining flexible for runtime overrides and CI pipelines.

---

## Configuration Precedence

From highest to lowest:

1. CLI flags (`--config`, `--tag`, etc.)
2. Environment variables (`OMNIBASE_*`)
3. Project-level config (`./omnibase.yml`)
4. User config (`~/.config/omnibase/config.yml`)
5. System config (`/etc/omnibase/config.yml`)
6. Built-in defaults

---

## Merge Semantics

Follows RFC 7396 (JSON Merge Patch):

- Dictionaries are merged recursively
- Arrays are replaced (not appended)
- Null values delete keys

*Note:* The old `+array:` merge prefix has been removed.

---

## Example Config File

```yaml
validators:
  tags: ["pre-commit", "schema"]
  ignore:
    - "build/"
    - "tmp/"
registry:
  cache_ttl: 3600
formatters:
  human:
    color: true
    emoji: true
```

---

## Environment Variable Mapping

Variables follow a flat dot notation with prefix:

| Env Var | Maps To |
|---------|---------|
| `OMNIBASE_VALIDATORS_TAGS` | `validators.tags` |
| `OMNIBASE_FORMATTERS_HUMAN_EMOJI` | `formatters.human.emoji` |

All values are parsed using YAML syntax, so lists, booleans, and numbers are valid.

---

## Validation

Validated via a Pydantic schema:

```python
class ValidatorConfig(BaseModel):
    tags: List[str]
    ignore: List[str]

class FormatterConfig(BaseModel):
    color: bool = True
    emoji: bool = True

class OmniBaseConfig(BaseModel):
    validators: ValidatorConfig
    formatters: Dict[str, FormatterConfig]
    registry: Dict[str, Any]
```

Unknown keys are rejected (`extra = "forbid"`).

---

## Dynamic Reloading

A long-running service can hot-reload config:

```python
cfg_mgr = ConfigManager(path="omnibase.yml")
cfg = cfg_mgr.get_config()
```

File mtime is checked and new config is parsed if modified.

---

## CLI Integration

```bash
omnibase run --config ./custom.yml --format json
OMNIBASE_VALIDATORS_TAGS="['schema']" omnibase run
```

---

## Planned Enhancements

- [ ] Live config edit via CLI (`omnibase config set validators.ignore`)
- [ ] Config validation tool (`omnibase validate config`)
- [ ] Override diff view (`omnibase config diff`)
- [ ] Support `.env` files as source

---

> Config drives context. No assumptions are safe unless declared or overridden.