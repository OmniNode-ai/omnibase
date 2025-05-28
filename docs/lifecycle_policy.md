<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: lifecycle_policy.md
version: 1.0.0
uuid: 784b9a23-e6e3-4d79-8d1e-30c86bfb347c
author: OmniNode Team
created_at: 2025-05-28T12:40:26.459988
last_modified_at: 2025-05-28T17:20:04.533236
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2fabdfdec8025032e1891d2dda80fae728197dcd302600cdf8606f6bd9d40185
entrypoint: python@lifecycle_policy.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.lifecycle_policy
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Lifecycle Policy

> **Status:** Canonical
> **Last Updated:** 2025-05-25
> **Purpose:** Define the canonical lifecycle states, transitions, and governance rules for all ONEX nodes and artifacts
> **Audience:** Node authors, maintainers, CI/CD systems, registry managers
> **Enforcement:** This policy is enforced by CI validation and registry management tools

---

## Overview

All ONEX nodes and artifacts must declare a `lifecycle` field that indicates their current state in the development and maintenance cycle. This policy defines the four canonical lifecycle states, their meanings, transition rules, and enforcement mechanisms.

## Lifecycle States

### 1. `draft`
**Purpose:** Work-in-progress nodes under active development

**Characteristics:**
- ✅ **Allowed:** Frequent changes, incomplete functionality, experimental features
- ✅ **Allowed:** Missing or incomplete documentation
- ✅ **Allowed:** Breaking changes without notice
- ❌ **Restricted:** Cannot be used in production workflows
- ❌ **Restricted:** Not included in stable registry exports
- ❌ **Restricted:** No backward compatibility guarantees

**CI Requirements:**
- Must pass basic schema validation
- Must have valid metadata block
- May have relaxed test coverage requirements

**Transition Rules:**
- Can transition to `active` when ready for production use
- Can transition to `archived` if abandoned
- Cannot transition directly to `deprecated`

### 2. `active`
**Purpose:** Production-ready nodes available for general use

**Characteristics:**
- ✅ **Guaranteed:** Stable API and behavior
- ✅ **Guaranteed:** Comprehensive documentation
- ✅ **Guaranteed:** Full test coverage
- ✅ **Guaranteed:** Backward compatibility within major version
- ✅ **Guaranteed:** Security and performance standards met
- ❌ **Restricted:** Breaking changes require major version bump

**CI Requirements:**
- Must pass all validation tests
- Must have 100% test coverage for core functionality
- Must pass security and performance benchmarks
- Must have complete documentation

**Transition Rules:**
- Can transition to `deprecated` when replacement is available
- Can transition to `archived` in exceptional circumstances
- Cannot transition back to `draft`

### 3. `deprecated`
**Purpose:** Nodes marked for removal but still functional

**Characteristics:**
- ✅ **Guaranteed:** Continues to function as documented
- ✅ **Guaranteed:** Security patches will be applied
- ✅ **Required:** Must specify `deprecated_by` field with replacement UUID
- ✅ **Required:** Must specify deprecation timeline
- ❌ **Restricted:** No new features will be added
- ❌ **Restricted:** Performance improvements not guaranteed

**CI Requirements:**
- Must pass all existing validation tests
- Must have valid `deprecated_by` field pointing to replacement
- Must have deprecation notice in documentation

**Transition Rules:**
- Can transition to `archived` after deprecation period
- Cannot transition to `active` or `draft`
- Deprecation period minimum: 6 months for public APIs

### 4. `archived`
**Purpose:** Nodes that are no longer maintained or functional

**Characteristics:**
- ❌ **Restricted:** No longer executable
- ❌ **Restricted:** No maintenance or support
- ❌ **Restricted:** Not included in registry discovery
- ✅ **Preserved:** Metadata preserved for historical reference
- ✅ **Required:** Must specify `archived_reason` field

**CI Requirements:**
- Metadata validation only
- No functional testing required
- Must have valid `archived_reason` field

**Transition Rules:**
- Terminal state - no transitions allowed
- Can only be reached from `deprecated` or `draft`

## Governance Rules

### Lifecycle Transitions

| From | To | Approval Required | Notice Period |
|------|----|--------------------|---------------|
| `draft` → `active` | Node author + 1 reviewer | None |
| `active` → `deprecated` | Maintainer team | 30 days |
| `deprecated` → `archived` | Maintainer team | 14 days |
| `draft` → `archived` | Node author | None |
| Any → `active` | Maintainer team + security review | 7 days |

### Required Fields by Lifecycle

| Field | `draft` | `active` | `deprecated` | `archived` |
|-------|---------|----------|--------------|------------|
| `name` | ✅ | ✅ | ✅ | ✅ |
| `version` | ✅ | ✅ | ✅ | ✅ |
| `description` | ⚠️ | ✅ | ✅ | ✅ |
| `deprecated_by` | ❌ | ❌ | ✅ | ❌ |
| `archived_reason` | ❌ | ❌ | ❌ | ✅ |
| `state_contract` | ⚠️ | ✅ | ✅ | ⚠️ |

Legend: ✅ Required, ⚠️ Recommended, ❌ Not applicable

### Version Management

- **Draft nodes:** Can use any version scheme
- **Active nodes:** Must follow semantic versioning (semver)
- **Deprecated nodes:** Version frozen at deprecation
- **Archived nodes:** Version preserved for reference

## CI Enforcement

### Validation Rules

```yaml
# CI validation enforces these rules
lifecycle_validation:
  draft:
    - schema_validation: required
    - test_coverage: optional
    - documentation: optional
  active:
    - schema_validation: required
    - test_coverage: 100%
    - documentation: complete
    - security_scan: passed
  deprecated:
    - schema_validation: required
    - deprecated_by: required
    - deprecation_notice: required
  archived:
    - schema_validation: required
    - archived_reason: required
```

### Automated Checks

1. **Lifecycle Field Validation**
   - Must be one of: `draft`, `active`, `deprecated`, `archived`
   - Must be present in all metadata blocks

2. **Transition Validation**
   - Validates allowed transitions
   - Checks required fields for target lifecycle state
   - Enforces approval requirements

3. **Registry Integration**
   - Only `active` and `deprecated` nodes included in production registry
   - `draft` nodes available in development registry only
   - `archived` nodes excluded from discovery but metadata preserved

## Error Taxonomy

### Lifecycle Validation Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `LC001` | Invalid lifecycle value | Use one of: draft, active, deprecated, archived |
| `LC002` | Missing required field for lifecycle state | Add required field (see table above) |
| `LC003` | Invalid lifecycle transition | Follow allowed transition rules |
| `LC004` | Missing approval for transition | Obtain required approvals |
| `LC005` | Deprecated node missing replacement | Add `deprecated_by` field with valid UUID |
| `LC006` | Archived node missing reason | Add `archived_reason` field |

## Examples

### Draft Node
```yaml
lifecycle: draft
name: experimental_feature
version: 0.1.0
description: "Experimental feature under development"
# state_contract optional for draft
```

### Active Node
```yaml
lifecycle: active
name: text_processor
version: 1.2.0
description: "Production text processing node"
state_contract: "state_contract://text_processor/v1"
# Full documentation and tests required
```

### Deprecated Node
```yaml
lifecycle: deprecated
name: legacy_parser
version: 2.1.0
description: "Legacy parser - use new_parser instead"
deprecated_by: "550e8400-e29b-41d4-a716-446655440000"
deprecation_date: "2025-06-01"
end_of_life_date: "2025-12-01"
```

### Archived Node
```yaml
lifecycle: archived
name: obsolete_tool
version: 1.0.0
description: "Obsolete tool no longer maintained"
archived_reason: "Replaced by modern implementation"
archived_date: "2025-01-15"
```

## Migration Guide

### For Node Authors

1. **New Nodes:** Start with `lifecycle: draft`
2. **Production Ready:** Transition to `lifecycle: active` with full documentation
3. **Deprecating:** Add `deprecated_by` field and transition to `lifecycle: deprecated`
4. **Archiving:** Add `archived_reason` and transition to `lifecycle: archived`

### For CI/CD Systems

1. **Validation:** Implement lifecycle validation in CI pipelines
2. **Registry:** Filter nodes by lifecycle for different environments
3. **Monitoring:** Track lifecycle transitions and compliance

### For Users

1. **Discovery:** Use only `active` nodes for production
2. **Migration:** Plan migration when nodes become `deprecated`
3. **Testing:** Use `draft` nodes only in development environments

---

## References

- [Node Metadata Schema](../schemas/onex_node.yaml)
- [CI Enforcement Documentation](../ci/enforcement.md)
- [Registry Management Guide](../registry/management.md)
- [Semantic Versioning Specification](https://semver.org/)

---

**Enforcement:** This policy is enforced by CI validation and is mandatory for all ONEX nodes and artifacts.
