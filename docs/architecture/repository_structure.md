<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: repository_structure.md
version: 1.0.0
uuid: bbddc8d3-c46e-461b-884d-f4236d1e8148
author: OmniNode Team
created_at: 2025-05-27T07:18:35.244863
last_modified_at: 2025-05-27T17:26:51.885175
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b5f4f97fa279036f743e0ac266351582519561a1274c3ba9c5e4cf6449f63077
entrypoint: python@repository_structure.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.repository_structure
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Repository Structure

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the repository structure and organization principles for the ONEX codebase  
> **Audience:** Developers, contributors, maintainers  
> **Companion:** [Development Standards](../standards.md), [Contributing Guidelines](../contributing.md)

---

## Overview

This document provides a comprehensive guide to the ONEX repository structure, explaining the organization principles, directory purposes, and rationale behind the codebase layout. The structure is designed to support scalability, maintainability, and clear separation of concerns.

---

## Repository Root Structure

```
omninode_clean/
├── .github/                    # GitHub-specific configuration
├── .cursor/                    # Cursor IDE configuration
├── docs/                       # Documentation (this directory)
├── examples/                   # Example implementations and tutorials
├── schema/                     # JSON/YAML schemas for validation
├── scripts/                    # Build, deployment, and utility scripts
├── src/                        # Source code (main implementation)
├── tests/                      # Test suites and test utilities
├── .gitignore                  # Git ignore patterns
├── .onexignore                 # ONEX-specific ignore patterns
├── .onextree                   # ONEX tree structure metadata
├── .onexversion                # ONEX version information
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── .tree                       # Tree structure cache
├── .yamllint                   # YAML linting configuration
├── CHANGELOG.md                # Version history and changes
├── CODE_OF_CONDUCT.md          # Community guidelines
├── LICENSE                     # License information
├── pyproject.toml              # Python project configuration
├── pytest.ini                 # Pytest configuration
└── README.md                   # Project overview and quick start
```

---

## Source Code Structure (`src/`)

### Main Source Directory

```
src/
└── omnibase/                   # Main package namespace
    ├── cli_tools/              # Command-line interface tools
    ├── core/                   # Core system components
    ├── nodes/                  # ONEX node implementations
    ├── protocols/              # Protocol definitions
    ├── templates/              # Code and documentation templates
    └── __init__.py             # Package initialization
```

### Core Components (`src/omnibase/core/`)

```
core/
├── __init__.py                 # Core package initialization
├── core_registry.py           # Central registry implementation
├── core_execution_context.py  # Execution context management
├── core_validation.py         # Core validation logic
├── core_metadata.py           # Metadata handling
├── core_lifecycle.py          # Lifecycle management
├── core_error_handling.py     # Error handling framework
├── core_security.py           # Security and authentication
├── core_monitoring.py         # Monitoring and observability
└── core_configuration.py      # Configuration management
```

**Purpose**: Contains the fundamental building blocks of the ONEX system. These components provide the essential services that all other parts of the system depend on.

**Naming Convention**: All files prefixed with `core_` to clearly identify them as core system components.

### CLI Tools (`src/omnibase/cli_tools/`)

```
cli_tools/
├── __init__.py
└── onex/                       # Main ONEX CLI tool
    └── v1_0_0/                 # Versioned CLI implementation
        ├── __init__.py
        ├── cli_main.py         # Main CLI entry point
        ├── cli_commands.py     # Command implementations
        ├── cli_output.py       # Output formatting
        ├── cli_validation.py   # CLI input validation
        └── cli_utils.py        # CLI utilities
```

**Purpose**: Command-line interface implementations. Organized by tool name and version to support multiple CLI versions and tools.

**Versioning**: Each CLI tool version is in its own directory (e.g., `v1_0_0`) to enable backward compatibility and gradual migration.

### Nodes (`src/omnibase/nodes/`)

```
nodes/
├── __init__.py
├── logger_node/                # Example: Logger node
│   ├── v1_0_0/                 # Versioned implementation
│   │   ├── __init__.py
│   │   ├── logger_node.py      # Main implementation
│   │   ├── logger_config.py    # Configuration
│   │   └── logger_utils.py     # Utilities
│   ├── metadata.yaml           # Node metadata
│   ├── test.py                 # Node tests
│   └── README.md               # Node documentation
├── stamper_node/               # Metadata stamper node
│   ├── v1_0_0/
│   │   ├── __init__.py
│   │   ├── stamper_node.py
│   │   ├── stamper_engine.py
│   │   └── stamper_handlers.py
│   ├── metadata.yaml
│   ├── test.py
│   └── README.md
└── template_node/              # Template for new nodes
    ├── v1_0_0/
    │   ├── __init__.py
    │   ├── template_node.py
    │   └── template_utils.py
    ├── metadata.yaml
    ├── test.py
    └── README.md
```

**Purpose**: Individual ONEX node implementations. Each node is self-contained with its own versioning, tests, and documentation.

**Structure Rules**:
- Each node has its own directory
- Versioned implementations in subdirectories (e.g., `v1_0_0`)
- Required files: `metadata.yaml`, `test.py`, `README.md`
- Main implementation file named after the node (e.g., `logger_node.py`)

### Protocols (`src/omnibase/protocols/`)

```
protocols/
├── __init__.py                 # Protocol package initialization
├── protocol_execution.py      # Execution protocols
├── protocol_registry.py       # Registry protocols
├── protocol_validation.py     # Validation protocols
├── protocol_handlers.py       # File handler protocols
├── protocol_security.py       # Security protocols
├── protocol_monitoring.py     # Monitoring protocols
└── protocol_lifecycle.py      # Lifecycle protocols
```

**Purpose**: Protocol definitions that define interfaces and contracts throughout the system. These are the foundation of the protocol-first architecture.

**Naming Convention**: All files prefixed with `protocol_` to clearly identify them as protocol definitions.

### Templates (`src/omnibase/templates/`)

```
templates/
├── __init__.py
├── nodes/                      # Node templates
│   ├── basic_node.tmpl         # Basic node template
│   ├── validation_node.tmpl    # Validation node template
│   └── processing_node.tmpl    # Processing node template
├── docs/                       # Documentation templates
│   ├── node_readme.tmpl        # Node README template
│   ├── api_doc.tmpl            # API documentation template
│   └── spec_doc.tmpl           # Specification template
├── tests/                      # Test templates
│   ├── unit_test.tmpl          # Unit test template
│   ├── integration_test.tmpl   # Integration test template
│   └── e2e_test.tmpl           # End-to-end test template
└── dev_logs/                   # Development log templates
    ├── debug_log.tmpl          # Debug log template
    ├── pr_description.tmpl     # PR description template
    └── velocity_log.tmpl       # Velocity log template
```

**Purpose**: Templates for generating consistent code, documentation, and other artifacts. Supports rapid development and maintains consistency across the codebase.

---

## Documentation Structure (`docs/`)

### Main Documentation

```
docs/
├── index.md                    # Documentation hub
├── README.md                   # Documentation overview
├── quickstart.md               # Quick start guide
├── contributing.md             # Contribution guidelines
├── testing.md                  # Testing philosophy
├── standards.md                # Development standards
├── reference-security-overview.md # Security overview
├── guide-security-implementation.md # Security implementation
├── architecture-security-design.md # Security design
├── guide-security-monitoring.md # Security monitoring
├── guide-incident-response.md  # Incident response
├── monitoring.md               # Monitoring specification
├── infrastructure.md           # Infrastructure requirements
├── changelog.md                # Change log
├── cli_examples.md             # CLI usage examples
├── cli_interface.md            # CLI interface specification
├── configuration.md            # Configuration system
├── developer_guide.md          # Developer guidelines
├── error_handling.md           # Error handling specification
├── error_taxonomy.md           # Error classification
├── execution_context.md        # Execution context specification
├── reference-handlers-protocol.md     # Handler protocols and interfaces
├── reference-handlers-registry.md     # Handler registry API and management
├── guide-handlers-implementation.md   # Handler implementation examples
├── lifecycle_policy.md         # Lifecycle management
├── metadata.md                 # Metadata specification
├── metrics_dashboard.md        # Metrics and dashboards
├── onex_node_spec.md           # Node specification
├── orchestration.md            # Orchestration specification
├── reference-protocols-core.md     # Core protocol definitions
├── reference-protocols-registry.md # Registry protocols
├── reference-data-models.md        # Data models
├── reference-protocols-core.md     # Core protocol definitions
├── reference-protocols-registry.md # Registry protocols  
├── reference-data-models.md        # Data models
├── registry.md                 # Registry specification
├── registry_architecture.md    # Registry architecture
├── structured_testing.md       # Testing framework
└── architectural_scrutiny.md   # Architecture analysis
```

### Specialized Documentation

```
docs/
├── architecture/               # Architecture documentation
│   ├── registry_backend_choices.md
│   └── repository_structure.md
├── error_handling/             # Error handling details
│   ├── index.md
│   ├── observability.md
│   └── retry.md
├── generated/                  # Auto-generated documentation
│   ├── execution_result.md
│   ├── onex_node.md
│   ├── state_contract.md
│   └── tree_format.md
├── guides/                     # User guides
│   ├── cli_quickstart.md
│   ├── getting_started.md
│   └── cli/
│       └── index.md
├── metadata/                   # Metadata documentation
│   ├── index.md
│   ├── dependency.md
│   ├── lineage.md
│   └── validation.md
├── security/                   # Security documentation
│   ├── index.md
│   └── threat_model.md
├── standards/                  # Standards documentation
│   └── canonical_file_types.md
├── templates/                  # Documentation templates
│   ├── README.md
│   ├── schema_doc.md.j2
│   └── template_validator.py
├── testing/                    # Testing documentation
│   ├── README.md
│   ├── fixtures_guidelines.md
│   └── node_testing_guidelines.md
└── tools/                      # Tool documentation
    └── stamper.md
```

---

## Test Structure (`tests/`)

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_core/              # Core component tests
│   │   ├── test_registry.py
│   │   ├── test_execution.py
│   │   └── test_validation.py
│   ├── test_nodes/             # Node tests
│   │   ├── test_logger_node.py
│   │   └── test_stamper_node.py
│   └── test_protocols/         # Protocol tests
│       ├── test_execution_protocol.py
│       └── test_registry_protocol.py
├── integration/                # Integration tests
│   ├── __init__.py
│   ├── test_cli_integration.py
│   ├── test_node_workflows.py
│   └── test_registry_integration.py
├── e2e/                        # End-to-end tests
│   ├── __init__.py
│   ├── test_full_workflows.py
│   └── test_user_scenarios.py
├── fixtures/                   # Test fixtures and data
│   ├── __init__.py
│   ├── sample_nodes/
│   ├── test_data/
│   └── mock_objects/
└── utils/                      # Test utilities
    ├── __init__.py
    ├── test_helpers.py
    └── mock_factories.py
```

**Purpose**: Comprehensive test suite organized by test type and scope. Follows the testing philosophy outlined in the documentation.

---

## Schema Structure (`schema/`)

```
schema/
├── node_metadata_schema.json   # Node metadata validation schema
├── execution_context_schema.json # Execution context schema
├── registry_schema.json        # Registry data schema
├── configuration_schema.json   # Configuration validation schema
├── error_response_schema.json  # Error response schema
├── test_result_schema.json     # Test result schema
└── cli_config_schema.json      # CLI configuration schema
```

**Purpose**: JSON schemas for validating data structures throughout the system. Ensures consistency and enables validation.

---

## Scripts Structure (`scripts/`)

```
scripts/
├── build/                      # Build scripts
│   ├── build.sh                # Main build script
│   ├── package.sh              # Packaging script
│   └── validate.sh             # Validation script
├── deploy/                     # Deployment scripts
│   ├── deploy.sh               # Main deployment script
│   ├── setup_env.sh            # Environment setup
│   └── health_check.sh         # Health check script
├── dev/                        # Development scripts
│   ├── setup_dev.sh            # Development environment setup
│   ├── run_tests.sh            # Test execution script
│   └── format_code.sh          # Code formatting script
└── utils/                      # Utility scripts
    ├── generate_docs.sh         # Documentation generation
    ├── update_schemas.sh        # Schema update script
    └── cleanup.sh               # Cleanup script
```

**Purpose**: Automation scripts for building, testing, deploying, and maintaining the codebase.

---

## Examples Structure (`examples/`)

```
examples/
├── README.md                   # Examples overview
├── basic_usage/                # Basic usage examples
│   ├── hello_world_node.py
│   ├── simple_validation.py
│   └── basic_cli_usage.sh
├── advanced/                   # Advanced examples
│   ├── custom_protocols.py
│   ├── complex_workflows.py
│   └── advanced_configuration.yaml
├── integrations/               # Integration examples
│   ├── ci_cd_pipeline.yaml
│   ├── docker_deployment/
│   └── kubernetes_manifests/
└── tutorials/                  # Step-by-step tutorials
    ├── getting_started.md
    ├── building_first_node.md
    └── advanced_patterns.md
```

**Purpose**: Practical examples and tutorials to help users understand and adopt the ONEX system.

---

## Configuration Files

### Root Configuration Files

| File | Purpose | Description |
|------|---------|-------------|
| `pyproject.toml` | Python project configuration | Dependencies, build settings, tool configuration |
| `pytest.ini` | Pytest configuration | Test discovery, markers, output settings |
| `.pre-commit-config.yaml` | Pre-commit hooks | Code quality checks, formatting, validation |
| `.gitignore` | Git ignore patterns | Files and directories to exclude from version control |
| `.onexignore` | ONEX ignore patterns | Files to exclude from ONEX processing |
| `.yamllint` | YAML linting rules | YAML formatting and style rules |

### ONEX-Specific Files

| File | Purpose | Description |
|------|---------|-------------|
| `.onextree` | Tree structure metadata | Complete file tree with metadata |
| `.onexversion` | Version information | Current ONEX version and compatibility |
| `.tree` | Tree cache | Cached tree structure for performance |

---

## Naming Conventions

### File Naming

| Pattern | Usage | Examples |
|---------|-------|----------|
| `core_*.py` | Core system components | `core_registry.py`, `core_execution.py` |
| `protocol_*.py` | Protocol definitions | `protocol_execution.py`, `protocol_registry.py` |
| `cli_*.py` | CLI components | `cli_main.py`, `cli_commands.py` |
| `test_*.py` | Test files | `test_registry.py`, `test_execution.py` |
| `*_node.py` | Node implementations | `logger_node.py`, `stamper_node.py` |

### Directory Naming

| Pattern | Usage | Examples |
|---------|-------|----------|
| `snake_case` | All directories | `cli_tools`, `error_handling` |
| `v{major}_{minor}_{patch}` | Version directories | `v1_0_0`, `v2_1_3` |
| `{node_name}_node` | Node directories | `logger_node`, `stamper_node` |

---

## Organization Principles

### 1. Separation of Concerns

- **Core**: Fundamental system components
- **Protocols**: Interface definitions
- **Nodes**: Business logic implementations
- **CLI**: User interface layer
- **Tests**: Validation and verification

### 2. Versioning Strategy

- **Semantic Versioning**: Major.Minor.Patch format
- **Directory Versioning**: Each version in separate directory
- **Backward Compatibility**: Multiple versions can coexist

### 3. Self-Contained Modules

- Each node is completely self-contained
- All dependencies explicitly declared
- Independent testing and deployment

### 4. Clear Dependencies

- Core components have minimal dependencies
- Protocols define clear interfaces
- Dependency injection for loose coupling

### 5. Documentation Co-location

- README.md in each major directory
- Inline documentation in code
- Comprehensive docs/ directory

---

## Development Workflow

### Adding New Components

1. **Core Components**: Add to `src/omnibase/core/`
2. **Protocols**: Add to `src/omnibase/protocols/`
3. **Nodes**: Create new directory in `src/omnibase/nodes/`
4. **CLI Tools**: Add to `src/omnibase/cli_tools/`
5. **Tests**: Add corresponding tests in `tests/`
6. **Documentation**: Update relevant docs

### File Creation Checklist

- [ ] Follow naming conventions
- [ ] Include appropriate metadata
- [ ] Add corresponding tests
- [ ] Update documentation
- [ ] Run validation scripts
- [ ] Update `.onextree` if needed

---

## Maintenance Guidelines

### Regular Maintenance Tasks

1. **Update Dependencies**: Keep dependencies current
2. **Validate Structure**: Run structure validation scripts
3. **Clean Up**: Remove obsolete files and directories
4. **Update Documentation**: Keep docs synchronized with code
5. **Review Naming**: Ensure consistent naming conventions

### Quality Assurance

- **Pre-commit Hooks**: Automated quality checks
- **CI/CD Pipeline**: Continuous validation
- **Code Reviews**: Manual quality verification
- **Documentation Reviews**: Keep docs current

---

## References

- [Development Standards](../standards.md)
- [Contributing Guidelines](../contributing.md)
- [Testing Philosophy](../testing.md)
- [CLI Interface](../cli_interface.md)
- [Node Specification](../onex_node_spec.md)

---

**Note:** This repository structure is designed to scale with the project while maintaining clarity and organization. Regular reviews and updates ensure the structure continues to serve the project's needs effectively.
