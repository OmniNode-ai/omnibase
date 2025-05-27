<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: lifecycle_policy.md
version: 1.0.0
uuid: 65e52213-cb36-4f34-89fa-c8e7010dd171
author: OmniNode Team
created_at: 2025-05-27T05:48:00.776237
last_modified_at: 2025-05-27T17:26:51.909833
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 5421f20f4cb2c0d941d17a1bc4f318832d7780305020fedc39276b996625609c
entrypoint: python@lifecycle_policy.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.lifecycle_policy
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Lifecycle Policy

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
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
archived_date: "2025-05-27"
```

## CLI Integration

### Lifecycle Management Commands

```bash
# Check node lifecycle status
onex node-info my_node --show-lifecycle

# List nodes by lifecycle
onex list-nodes --lifecycle active
onex list-nodes --lifecycle deprecated

# Validate lifecycle compliance
onex run parity_validator_node --args='["--validation-types", "lifecycle_compliance"]'

# Transition node lifecycle (requires approval)
onex lifecycle transition my_node --from draft --to active

# Check transition requirements
onex lifecycle check my_node --target active
```

### Registry Filtering

```bash
# Production registry (active + deprecated only)
onex list-nodes --registry production

# Development registry (includes draft)
onex list-nodes --registry development

# Show archived nodes (metadata only)
onex list-nodes --include-archived
```

## Migration Guide

### For Node Authors

1. **New Nodes:** Start with `lifecycle: draft`
   ```yaml
   lifecycle: draft
   name: my_new_node
   version: 0.1.0
   description: "New node under development"
   ```

2. **Production Ready:** Transition to `lifecycle: active` with full documentation
   ```bash
   # Ensure all requirements are met
   onex lifecycle check my_node --target active
   
   # Request transition
   onex lifecycle transition my_node --from draft --to active
   ```

3. **Deprecating:** Add `deprecated_by` field and transition to `lifecycle: deprecated`
   ```yaml
   lifecycle: deprecated
   deprecated_by: "uuid-of-replacement-node"
   deprecation_date: "2025-06-01"
   end_of_life_date: "2025-12-01"
   ```

4. **Archiving:** Add `archived_reason` and transition to `lifecycle: archived`
   ```yaml
   lifecycle: archived
   archived_reason: "Replaced by modern implementation"
   archived_date: "2025-05-27"
   ```

### For CI/CD Systems

1. **Validation:** Implement lifecycle validation in CI pipelines
   ```bash
   # Add to CI pipeline
   onex run parity_validator_node --args='["--validation-types", "lifecycle_compliance"]'
   ```

2. **Registry:** Filter nodes by lifecycle for different environments
   ```bash
   # Production deployment
   onex list-nodes --lifecycle active --format json > production_nodes.json
   
   # Development deployment
   onex list-nodes --lifecycle draft,active --format json > dev_nodes.json
   ```

3. **Monitoring:** Track lifecycle transitions and compliance
   ```bash
   # Generate lifecycle report
   onex lifecycle report --format json > lifecycle_status.json
   ```

### For Users

1. **Discovery:** Use only `active` nodes for production
   ```bash
   onex list-nodes --lifecycle active
   ```

2. **Migration:** Plan migration when nodes become `deprecated`
   ```bash
   # Find deprecated nodes and their replacements
   onex list-nodes --lifecycle deprecated --show-replacements
   ```

3. **Testing:** Use `draft` nodes only in development environments
   ```bash
   onex list-nodes --lifecycle draft --registry development
   ```

## Best Practices

### For Node Development

1. **Start with draft**: Always begin new nodes in `draft` lifecycle
2. **Document thoroughly**: Complete documentation before transitioning to `active`
3. **Test comprehensively**: Ensure 100% test coverage for `active` nodes
4. **Plan deprecation**: Provide clear migration paths when deprecating nodes
5. **Archive responsibly**: Include clear reasons when archiving nodes

### For Lifecycle Management

1. **Follow approval process**: Obtain required approvals for lifecycle transitions
2. **Provide notice**: Give adequate notice for deprecation and archival
3. **Maintain compatibility**: Preserve backward compatibility in `active` nodes
4. **Monitor compliance**: Regularly check lifecycle compliance across the ecosystem
5. **Update documentation**: Keep lifecycle documentation current

### For Registry Management

1. **Filter appropriately**: Use lifecycle filters for environment-specific deployments
2. **Monitor transitions**: Track lifecycle changes and their impact
3. **Enforce policies**: Use CI validation to enforce lifecycle policies
4. **Plan capacity**: Consider lifecycle distribution when planning registry resources
5. **Audit regularly**: Review lifecycle compliance and transition patterns

## Integration with ONEX CLI

### Lifecycle Commands

```bash
# Lifecycle status and management
onex lifecycle status my_node
onex lifecycle history my_node
onex lifecycle transition my_node --to active
onex lifecycle validate --all

# Registry lifecycle filtering
onex list-nodes --lifecycle active,deprecated
onex node-info my_node --include-lifecycle-history

# Compliance checking
onex run parity_validator_node --args='["--validation-types", "lifecycle_compliance"]'
```

### Automated Lifecycle Management

```bash
# Bulk lifecycle operations
onex lifecycle bulk-transition --from draft --to active --pattern "validator_*"
onex lifecycle bulk-validate --lifecycle active
onex lifecycle report --format yaml > lifecycle_report.yaml
```

---

## References

- [Node Metadata Schema](../schemas/onex_node.yaml)
- [Semantic Versioning Specification](https://semver.org/)
- [docs/metadata.md](./metadata.md) - Metadata specification
- [docs/registry.md](./registry.md) - Registry management
- [docs/contributing.md](./contributing.md) - Contribution guidelines

---

**Enforcement:** This policy is enforced by CI validation and is mandatory for all ONEX nodes and artifacts.
