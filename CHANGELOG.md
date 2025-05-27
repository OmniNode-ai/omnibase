<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: CHANGELOG.md
version: 1.0.0
uuid: 9b9605c5-938b-4a2a-a568-671825370f46
author: OmniNode Team
created_at: 2025-05-22T17:18:16.672842
last_modified_at: 2025-05-22T21:19:13.392077
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b5d9a51011a0cf47a97662236564a8a6cb017b17e7c4f01be143ac93b770f0b7
entrypoint: python@CHANGELOG.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.CHANGELOG
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase / ONEX – CHANGELOG

All notable changes to this project will be documented in this file. This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and is intended for contributors and users of the open source OmniBase/ONEX project.

---

## [Unreleased]
- Project is in active foundational development. See the [project roadmap](README.md#roadmap) for planned features.

## [v0.1.0] – Milestone 0: Bootstrap (2025-05-19)
### Added
- Canonical directory structure and packaging (PEP 517/518, Poetry)
- Protocol definitions and registry stubs for ONEX node model
- CLI entrypoint (`onex`) and protocol-compliant CLI tools
- Canonical templates for node metadata, CLI, and test scaffolding
- Canonical test suite: registry-driven, markerless, fixture-injected, protocol-first
- Error taxonomy and base error class (`OmniBaseError`)
- Example schemas and loader with YAML/JSON support
- Documentation: architecture, onboarding, testing philosophy, and milestone checklist
- Velocity log automation and PR description tooling

### Changed
- Migrated legacy code to `legacy/` (now removed from history for open source release)
- Updated all documentation and templates to match canonical ONEX standards

### Removed
- All sensitive/internal files and legacy code from repository and git history

### References
- See the [project documentation](docs/README.md) for implementation details
- See the [changelog](docs/changelog.md) for detailed version history

---

## [Upcoming]
- Milestone 1: Validation engine, registry, and execution runtime
- Milestone 2: Planning, caching, trust, and composite graph support
- Milestone 3+: Federation, P2P, and interop

For more details, see the [project documentation](docs/README.md).

# Changelog

All notable changes to the ONEX system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Handler metadata enforcement in CI pipeline
- Comprehensive handler introspection capabilities
- Plugin development documentation and examples

### Changed
- Enhanced FileTypeHandlerRegistry with metadata support
- Improved error handling in handler registration

### Fixed
- Handler discovery edge cases in CI enforcement tests

## [1.0.0] - 2025-05-25

### Added
- **Handler & Registry API v1.0.0** - Complete plugin/override system for file type handlers
- **Required Handler Metadata** - All handlers must implement 8 metadata properties
- **FileTypeHandlerRegistry** - Central registry with priority-based conflict resolution
- **Plugin System** - Runtime handler registration with source attribution
- **CI Enforcement** - Automated validation of handler metadata compliance
- **Universal Node Support** - All nodes support `handler_registry` parameter
- **Comprehensive Documentation** - Complete API docs, migration guides, and examples
- **Handler Introspection** - Rich metadata for plugin management and debugging

### Changed
- **BREAKING**: `ProtocolFileTypeHandler` interface requires metadata properties
- **BREAKING**: All handler methods must return `OnexResultModel` instances
- **BREAKING**: File paths must be `pathlib.Path` objects, not strings
- Enhanced `FileTypeHandlerRegistry.list_handlers()` with metadata support
- Updated all existing handlers (Python, Markdown, YAML, Ignore) with metadata
- Improved error handling and validation throughout handler system

### Fixed
- Handler registration conflicts and priority resolution
- Type safety issues in handler method signatures
- Import consistency across handler implementations

### Migration Required
- Update custom handlers to implement required metadata properties
- Update method signatures to use `Path` and `OnexResultModel`
- Update handler registration to use new `register_handler()` API

### Documentation
- [Handler Registry](docs/reference-handlers-registry.md)
- [Handler Implementation Guide](docs/guide-handlers-implementation.md)
- [Handler Protocols](docs/reference-handlers-protocol.md)

## [0.9.0] - 2025-05-24

### Added
- Protocol & Models consolidation and governance
- Comprehensive test coverage for Event Bus Protocol
- Handler consolidation and shared fixtures
- Import standardization across all handlers

### Changed
- Moved duplicate handlers to shared fixtures
- Enhanced test infrastructure with dedicated protocol/model directories
- Improved import patterns for consistency

### Fixed
- Cross-node import violations
- Test coverage gaps in protocol implementations
- Handler duplication across node tests

## [0.8.0] - 2025-05-23

### Added
- Complete CI & Enforcement infrastructure
- Schema evolution test cases (21 comprehensive tests)
- Node lifecycle policy documentation
- Canonical error taxonomy (90 standardized error codes)
- Testing standards compliance with registry-driven patterns

### Changed
- Enhanced pre-commit hooks with comprehensive validation
- Improved error handling consistency across ONEX tools
- Updated testing patterns to be protocol-first and fixture-injected

### Fixed
- Schema validation edge cases
- Lifecycle validation enforcement
- .onextree synchronization issues

## [0.7.0] - 2025-05-22

### Added
- Runtime & Event Execution Layer
- OnexEvent model and EventBusProtocol
- In-memory event bus implementation
- NodeRunner for node execution with event emissions
- PostgresEventStore for event durability
- CLI command `onex run <node>`

### Changed
- All nodes now emit standard events (NODE_START, NODE_SUCCESS, NODE_FAILURE)
- Enhanced event-driven architecture throughout system
- Improved integration with ledger persistence

## [0.6.0] - 2025-05-21

### Added
- Runtime Directory Refactor
- Canonical subdirectories (filesystem/, io/, crypto/)
- Shared execution utilities migration
- Comprehensive documentation for runtime structure

### Changed
- Migrated all shared utilities with updated imports
- Removed duplicate copies across nodes and tools
- Improved runtime organization and discoverability

## [0.5.0] - 2025-05-20

### Added
- Protocol & Interface Remediation
- Canonical Protocols for all core interfaces
- FileTypeHandlerRegistry, SchemaExclusionRegistry protocols
- DirectoryTraverser and hash utilities protocols
- Strong typing and conformance testing

### Changed
- Refactored all core interfaces to use Protocols
- Enhanced hash utilities with canonical Enums
- Improved type safety across protocol implementations

## [0.4.0] - 2025-05-19

### Added
- Tree Generator Node Implementation
- Canonical directory structure following stamper patterns
- TreeGeneratorEngine with core logic (274 lines)
- Comprehensive .onextree validation tests
- Constants file with centralized status management

### Changed
- Reduced node.py from 419 to 191 lines (54% reduction)
- Standardized node function with proper event emission
- Fixed OnexStatus enum usage for MyPy compliance
- Updated tests to use status-based assertions

### Fixed
- Import patterns for MyPy compliance
- Hardcoded string maintenance issues
- Test fragility with string parsing

## [0.3.0] - 2025-05-18

### Added
- Stamper Node Implementation
- Complete stamper node with canonical structure
- Comprehensive test suite and documentation
- CLI integration and event emission
- Versioned node structure with proper imports

### Changed
- Migrated all artifacts to registry-centric directories
- Enhanced metadata files and source code organization
- Improved directory restructuring patterns

## [0.2.0] - 2025-05-17

### Added
- Schema & Protocol Definition
- Canonical schemas for .onex metadata and .onextree structure
- Dual-format (YAML/JSON) support with validation
- Schema changelogs and versioning policies
- CI validation for node metadata and state contracts

### Changed
- Enhanced schema validation and enforcement
- Improved documentation with usage examples
- Comprehensive unit/integration test coverage

## [0.1.0] - 2025-05-16

### Added
- Registry Node Conversion
- Complete migration from legacy registry infrastructure
- Registry loader node implementation
- Bootstrap registry and bridge pattern
- Zero breaking changes during transition

### Changed
- Removed 1,600+ lines of legacy code
- Enhanced protocol-driven testing patterns
- Improved project structure with cleanup

### Fixed
- Registry infrastructure reliability
- Test coverage maintenance during migration
- Configuration and dependency issues

---

## Version Numbering

ONEX follows semantic versioning (semver) with the following conventions:

- **Major version** (X.0.0): Breaking changes to public APIs or core architecture
- **Minor version** (0.X.0): New features, backward compatible additions
- **Patch version** (0.0.X): Bug fixes, documentation updates, backward compatible changes

## Breaking Changes Policy

Breaking changes are clearly marked with **BREAKING** labels and include:
- Migration guides and examples
- Deprecation notices in advance when possible
- Clear documentation of required changes
- Automated migration tools when feasible

## Release Process

1. **Development**: Features developed in feature branches
2. **Integration**: Changes merged to main branch with CI validation
3. **Release Candidate**: Tagged RC versions for testing
4. **Release**: Final version tagged and documented
5. **Post-Release**: Documentation updates and community notification

## Support Policy

- **Current Major Version**: Full support with bug fixes and security updates
- **Previous Major Version**: Security updates only for 6 months
- **Older Versions**: Community support only

---

For detailed API changes and migration guides, see:
- [Handler Registry](docs/reference-handlers-registry.md)
- [Handler Implementation Guide](docs/guide-handlers-implementation.md)
- [Architecture Documentation](docs/architecture/)
- [Handler Protocols](docs/reference-handlers-protocol.md)
