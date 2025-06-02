<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: CHANGELOG.md
version: 1.0.0
uuid: 1c57352c-4e25-419a-a223-19f512e8faa1
author: OmniNode Team
created_at: '2025-05-28T12:40:27.484017'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://CHANGELOG
namespace: markdown://CHANGELOG
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# ONEX Stamper Node Schema Changelog

> **Purpose:** Track all schema changes for stamper node state models  
> **Last Updated:** 2025-05-25  
> **Schema Version:** 1.1.0

This changelog tracks all changes to the stamper node state models (`StamperInputState` and `StamperOutputState`) following semantic versioning principles.

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

## [1.1.1] - 2025-05-25

### Fixed
- **Pydantic V2 Compatibility**: Migrated from deprecated Pydantic V1 syntax to V2 syntax
  - Replaced `@validator` with `@field_validator` and added `@classmethod` decorators
  - Updated `Field(example=...)` to `Field(json_schema_extra={"example": ...})`
  - Replaced class-based `Config` with `ConfigDict` using `model_config`
  - Replaced `schema_extra` with `json_schema_extra` in model configuration
- **Eliminated Deprecation Warnings**: Removed all Pydantic deprecation warnings from test output

### Technical Details
- All field validators now use Pydantic V2 `@field_validator` decorator with `@classmethod`
- Model configuration moved from nested `Config` class to `model_config = ConfigDict(...)`
- Field examples moved from `example` parameter to `json_schema_extra` for future compatibility
- Maintains full backward compatibility with existing state model contracts

---

## [1.1.0] - 2025-05-25

### Added
- **Schema Versioning System**: Implemented comprehensive schema versioning with changelog tracking
- **Version Validation**: Added validation to ensure version field consistency
- **Migration Framework**: Created foundation for future schema migrations
- **Status Value "error"**: Added "error" as a valid status value for compatibility with OnexStatus enum

### Enhanced
- **StamperInputState**: Enhanced documentation for version field usage
- **StamperOutputState**: Enhanced documentation for version field usage
- **Version Loading**: Improved integration with `OnexVersionLoader` for consistent versioning
- **Status Validation**: Updated to support "success", "failure", "warning", and "error" status values

### Documentation
- Created `CHANGELOG.md` for schema change tracking
- Enhanced state model documentation with versioning guidelines
- Added migration procedures for future schema changes

---

## [1.0.0] - 2025-05-22

### Added
- **StamperInputState**: Initial implementation with required fields
  - `version`: Schema version for input state (required)
  - `file_path`: Path to the file to be stamped (required)
  - `author`: Name or identifier of the user or process (default: "OmniNode Team")
  - `correlation_id`: Optional correlation ID for request tracking and telemetry

- **StamperOutputState**: Initial implementation with required fields
  - `version`: Schema version for output state (required)
  - `status`: Result status of the stamping operation (required)
  - `message`: Human-readable result or error message (required)
  - `correlation_id`: Optional correlation ID for request tracking and telemetry

### Schema Contract
- **Input Version**: Must match the schema version from `OnexVersionLoader`
- **Output Version**: Must match the input version for consistency
- **Correlation ID**: Propagated from input to output for telemetry tracking

---

## Migration Guidelines

### Adding New Fields (Minor Version)
When adding new optional fields:

1. Add field with appropriate default value
2. Update schema version (increment MINOR)
3. Update this changelog
4. Add tests for new field
5. Update documentation

Example:
```python
class StamperInputState(BaseModel):
    # ... existing fields
    new_optional_field: Optional[str] = None  # New in v1.2.0
```

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
- Must match the current schema version from `OnexVersionLoader`
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

### Planned for v1.2.0
- **Enhanced Error Handling**: Add structured error codes to output state
- **Performance Metrics**: Add optional timing and performance metadata
- **Batch Operations**: Support for batch stamping operations

### Planned for v2.0.0
- **State Persistence**: Add support for persistent state tracking
- **Advanced Correlation**: Enhanced correlation tracking with hierarchical relationships
- **Plugin Support**: Extensible state models for plugin-specific data

---

## References

- [ONEX Event Schema Specification](docs/protocol/onex_event_schema.md)
- [ONEX Event Schema Evolution Strategy](docs/protocol/onex_event_schema_evolution.md)
- [Milestone 1 Checklist](docs/milestones/milestone_1_checklist.md)
- [OnexVersionLoader Implementation](src/omnibase/runtimes/onex_runtime/v1_0_0/utils/onex_version_loader.py)

---

**Note**: This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and semantic versioning principles. All schema changes must be documented here before implementation.
