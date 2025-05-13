# OmniBase Configuration System & Cascading Strategy

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase uses a hierarchical, mergeable configuration system with support for CLI, environment variables, project/user/system configs, and defaults. Configuration is schema-validated and runtime-aware.

---

## Configuration Precedence (Highest to Lowest)

1. **CLI Arguments**
2. **Environment Variables** (prefixed `OMNIBASE_`)
3. **Project-level Config** (`./omnibase.yml`)
4. **User Config** (`~/.config/omnibase/config.yml`)
5. **System Config** (`/etc/omnibase/config.yml`)
6. **Hardcoded Defaults**

---

## Example Configuration

```yaml
# ./omnibase.yml
validators:
  tags:
    - pre-commit
    - schema
  ignore:
    - build/
    - tmp/
formatters:
  human:
    color: true
    emoji: true
registry:
  cache_ttl: 3600
```

---

## Schema

```python
from pydantic import BaseModel, Field
from typing import List

class ValidatorConfig(BaseModel):
    tags: List[str] = Field(default_factory=list)
    ignore: List[str] = Field(default_factory=list)
    concurrency: int = 4

class FormatterConfig(BaseModel):
    color: bool = True
    emoji: bool = True

class OmniBaseConfig(BaseModel):
    validators: ValidatorConfig
    formatters: dict
    registry: dict

    class Config:
        extra = "forbid"
```

---

## Environment Variable Mapping

Environment variables map to config fields using dot notation:

| Env Var                         | Maps to                   |
|----------------------------------|----------------------------|
| `OMNIBASE_VALIDATORS_TAGS`       | `validators.tags`         |
| `OMNIBASE_FORMATTERS_HUMAN_EMOJI`| `formatters.human.emoji`  |
| `OMNIBASE_REGISTRY_CACHE_TTL`    | `registry.cache_ttl`      |

---

## RFC 7396 Merge Semantics

OmniBase uses [RFC 7396](https://tools.ietf.org/html/rfc7396) (JSON Merge Patch) to apply config overrides. This eliminates the need for ad-hoc merging rules.

Behavior:

- Primitive values are replaced
- Arrays are fully replaced (not merged)
- `null` removes keys

---

## Dynamic Reloading

Long-running services monitor config files for changes:

```python
class ConfigManager:
    def get_config(self) -> OmniBaseConfig:
        # Re-parse if modified since last load
        ...
```

Used for:

- Background orchestrators
- Registry daemons
- Validator runners

---

## CLI Override Example

```bash
omnibase run --validators.tags canary --formatters.human.emoji false
```

---

## Future Enhancements

- [ ] Config schema documentation (`omnibase config describe`)
- [ ] Config linting (`omnibase config lint`)
- [ ] Config diff and preview tools
- [ ] Policy enforcement on config values (e.g. forbidden keys, required tags)

---

> Configuration is code—typed, traceable, layered, and overrideable.