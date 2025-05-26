<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: CHANGELOG.md
version: 1.0.0
uuid: 30761954-f67b-49ec-9283-b6a6ddc53c46
author: OmniNode Team
created_at: 2025-05-25T15:13:46.033651
last_modified_at: 2025-05-25T19:21:33.373329
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: edaa6a22eb7eb4fe85703e03f0c20fc051a2758a7ebe5337cc70b285f9e1d89f
entrypoint: python@CHANGELOG.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.CHANGELOG
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Registry Loader Node Schema Changelog

> **Purpose:** Track all schema changes for registry loader node state models  
> **Last Updated:** 2025-05-25  
> **Schema Version:** 1.0.0

This changelog tracks all changes to the registry loader node state models (`RegistryLoaderInputState` and `RegistryLoaderOutputState`) following semantic versioning principles.

## Schema Versioning Strategy

### Version Format
State model schemas follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes that require migration (e.g., removing fields, changing field types)
- **MINOR**: Backward-compatible additions (e.g., new optional fields)
- **PATCH**: Bug fixes and clarifications without schema changes

### Compatibility Policy
- **Backward Compatibility**: Minor and patch versions maintain backward compatibility
- **Forward Compatibility**: Consumers should gracefully handle unknown optional fields
- **Migration Support**: Major version changes include migration utilities and documentation

---

## [1.0.0] - 2025-05-24

### Added
- **RegistryLoaderInputState**: Initial implementation with required fields
  - `version`: Schema version for input state (required)
  - `root_directory`: Root directory path to scan for ONEX artifacts (required)
  - `onextree_path`: Path to .onextree file (optional, auto-discovered if None)
  - `include_wip`: Whether to include work-in-progress artifacts (default: false)
  - `artifact_types`: Filter to specific artifact types (optional, loads all if None)

- **RegistryLoaderOutputState**: Initial implementation with required fields
  - `version`: Schema version for output state (required)
  - `status`: Overall loading status using OnexStatus enum (required)
  - `message`: Human-readable status message (required)
  - `artifacts`: List of all discovered artifacts (default: empty list)
  - `artifact_count`: Total number of artifacts found (default: 0)
  - `valid_artifact_count`: Number of valid artifacts (default: 0)
  - `invalid_artifact_count`: Number of invalid artifacts (default: 0)
  - `wip_artifact_count`: Number of WIP artifacts (default: 0)
  - `artifact_types_found`: List of artifact types discovered (default: empty list)
  - `root_directory`: Root directory that was scanned (required)
  - `onextree_path`: Path to .onextree file if found (optional)
  - `scan_duration_ms`: Time taken to scan in milliseconds (optional)
  - `errors`: List of non-fatal errors encountered (default: empty list)

- **Supporting Models**:
  - `ArtifactTypeEnum`: Enumeration of supported artifact types
  - `RegistryLoadingErrorTypeEnum`: Enumeration of registry loading error types
  - `RegistryLoadingError`: Model for tracking loading errors
  - `RegistryArtifact`: Model representing a single artifact in the registry

### Schema Contract
- **Input Version**: Must match the schema version from schema validator
- **Output Version**: Must match the input version for consistency
- **Status Values**: Uses OnexStatus enum for consistent status reporting
- **Error Handling**: Non-fatal errors are collected and reported in the errors list

---

## Migration Guidelines

### Adding New Fields (Minor Version)
When adding new optional fields:

1. Add field with appropriate default value
2. Update schema version (increment MINOR)
3. Update this changelog
4. Add tests for new field
5. Update documentation

### Removing Fields (Major Version)
When removing fields (breaking change):

1. Deprecate field in previous minor version
2. Create migration utility
3. Update schema version (increment MAJOR)
4. Update this changelog with migration notes
5. Provide backward compatibility period

### Changing Field Types (Major Version)
When changing field types (breaking change):

1. Create migration utility for data transformation
2. Update schema version (increment MAJOR)
3. Document transformation logic
4. Provide validation for both old and new formats during transition

---

## Validation Rules

### Version Field Validation
- Must be a valid semantic version string (e.g., "1.0.0")
- Must match the current schema version from schema validator
- Input and output versions must match for consistency

### Backward Compatibility Testing
- All schema changes must pass backward compatibility tests
- New optional fields must have appropriate defaults
- Existing field behavior must remain unchanged

### Forward Compatibility Guidelines
- Consumers should ignore unknown fields gracefully
- Optional fields should not break existing functionality
- Schema validation should be configurable (strict/lenient modes)

---

## Future Enhancements

### Planned for v1.1.0
- **Enhanced Filtering**: Add support for custom artifact filters and exclusions
- **Performance Metrics**: Add detailed timing and performance metadata
- **Caching Support**: Add support for incremental loading with caching

### Planned for v2.0.0
- **Multi-Registry Support**: Support for loading from multiple registry sources
- **Advanced Validation**: Enhanced artifact validation with custom rules
- **Plugin Support**: Extensible state models for plugin-specific data

---

## References

- [Registry Loader Node Implementation](v1_0_0/node.py)
- [ONEX Event Schema Specification](../../docs/protocol/onex_event_schema.md)
- [Milestone 1 Checklist](../../docs/milestones/milestone_1_checklist.md)
- [OnexStatus Enum](../../model/enum_onex_status.py)

---

**Note**: This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and semantic versioning principles. All schema changes must be documented here before implementation.
