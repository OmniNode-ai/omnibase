# OmniBase Registry & Discovery Protocols

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

The registry subsystem provides structured discovery, indexing, and resolution of all OmniBase components. All validators, tools, tests, and artifacts must be registered and queryable via a uniform protocol.

---

## Component Types

| Type        | Description                              |
|-------------|------------------------------------------|
| Validator   | Stateless function that asserts a rule   |
| Tool        | Transformation or mutation operation     |
| Test        | Declarative, expected-output evaluator   |
| Artifact    | Typed input/output unit in CAS           |
| Pipeline    | Ordered chain of tools/validators        |

All are stored in the registry with UUIDs, SemVer, metadata blocks, and dependency graph links.

---

## Discovery Protocol

```python
class Registry(Protocol):
    def find(self, query: RegistryQuery) -> list[RegistryEntry]: ...
    def resolve(self, uuid: str, version: Optional[str] = None) -> RegistryEntry: ...
    def search(self, filters: dict[str, Any]) -> list[RegistryEntry]: ...
    def register(self, entry: RegistryEntry) -> None: ...
```

---

## Query Fields

| Field          | Description                        |
|----------------|------------------------------------|
| `uuid`         | Global identifier                  |
| `name`         | Human-readable label               |
| `tags`         | Filter execution stages, CLI runs  |
| `type`         | Validator, tool, test, etc.        |
| `version_spec` | SemVer range (`>=0.1.0,<0.2.0`)     |
| `capabilities` | Required permissions               |
| `status`       | `active`, `deprecated`, `draft`    |
| `lifecycle`    | `canary`, `stable`, `experimental` |

---

## Version Resolution

- Uses Pubgrub-compatible SemVer resolver
- Honors upper/lower bounds
- Rejects mixed-major inputs unless forced
- Registry maintains a `resolved_versions.json` file for reproducibility

---

## Federation Strategy (Planned)

- Future registries can sync with one another
- Priority order controlled by trust/config
- Conflicts resolved using `source_precedence`
- Components may be promoted/demoted based on validation success

---

## CLI Discovery Examples

```bash
omnibase list --type tool --tags canary
omnibase search --filter 'name=fix_header,type=tool'
omnibase resolve validator:abc123
omnibase inspect uuid-of-component
```

---

## Planned Enhancements

- [ ] GraphQL adapter for registry access
- [ ] Federation metadata schema (`registry_remote.yaml`)
- [ ] Trust scoring for source registries
- [ ] Differential sync for CI pipelines

---

> A system that can’t find its own parts can’t build anything. Registry is how OmniBase remembers.