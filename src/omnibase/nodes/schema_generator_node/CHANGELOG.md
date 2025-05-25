<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: CHANGELOG.md
version: 1.0.0
uuid: 277dbc85-cad3-4f93-b61e-672ef198d912
author: OmniNode Team
created_at: 2025-05-25T15:37:47.718519
last_modified_at: 2025-05-25T19:48:02.871292
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b9a670190189e8216cffe0f0fadddc6316f6a9af8c9b0a90a9777b3737bb4c62
entrypoint: python@CHANGELOG.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.CHANGELOG
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Changelog - Schema Generator Node

All notable changes to the schema generator node will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added
- Initial implementation of schema generator node
- JSON schema generation from Pydantic state models
- Support for all ONEX node state models (stamper, tree generator, registry loader, template)
- Configurable output directory with default to `src/schemas/`
- Optional metadata inclusion in generated schemas
- Selective model generation (can specify which models to generate)
- CLI interface with argparse for standalone execution
- Comprehensive input/output state models with validation
- Factory functions for consistent state creation
- Field validators using Pydantic V2 syntax
- Schema versioning integration with semantic version validation
- Proper error handling and status reporting
- Correlation ID support for request tracking
- Verbose logging support

### Schema Version
- **State Schema Version**: 1.0.0
- **Input State**: `SchemaGeneratorInputState` with fields for output directory, model selection, metadata options
- **Output State**: `SchemaGeneratorOutputState` with generation results and file listings

### Features
- **All Model Support**: Generates schemas for stamper, tree generator, registry loader, and template nodes
- **Flexible Generation**: Can generate all schemas or specific subset based on input
- **Metadata Control**: Optional JSON Schema metadata ($schema, $id) inclusion
- **Directory Management**: Automatic creation of output directories
- **Error Handling**: Graceful failure handling with detailed error messages
- **CLI Integration**: Can be run standalone or integrated into workflows

### Technical Details
- Uses Pydantic V2 `model_json_schema()` method for schema generation
- Follows ONEX node patterns with proper state models and validation
- Integrates with schema version validator utility
- Supports correlation IDs for telemetry and tracking
- Implements proper logging with configurable levels

### Usage Examples
```bash
# Generate all schemas to default location
poetry run python -m omnibase.nodes.schema_generator_node.v1_0_0.node

# Generate specific schemas
poetry run python -m omnibase.nodes.schema_generator_node.v1_0_0.node --models stamper_input stamper_output

# Custom output directory
poetry run python -m omnibase.nodes.schema_generator_node.v1_0_0.node --output-directory custom/schemas

# Without metadata
poetry run python -m omnibase.nodes.schema_generator_node.v1_0_0.node --no-metadata
```

### Integration
- Can be integrated into CI/CD pipelines for schema validation
- Supports ONEX runtime execution patterns
- Compatible with existing node infrastructure
- Follows established naming conventions and project standards

## Versioning Strategy

This node follows semantic versioning:
- **MAJOR**: Breaking changes to state models or core functionality
- **MINOR**: New features, additional model support, or enhanced functionality
- **PATCH**: Bug fixes, documentation updates, or minor improvements

## Migration Guidelines

### From Standalone Script
If migrating from the standalone `scripts/generate_schemas.py`:
1. Replace script calls with node execution
2. Use input state models instead of command-line arguments
3. Process output state instead of direct file system checks
4. Integrate with ONEX runtime for better observability

### Future Versions
- State model changes will be documented here
- Breaking changes will increment major version
- Backward compatibility will be maintained where possible
