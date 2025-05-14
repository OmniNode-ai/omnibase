# Validation Scripts

This directory contains all validators, linters, and checkers for the project. These scripts enforce standards for Dockerfiles, service structure, documentation, code quality, and more.

## Key Scripts
- `check_dockerfile.py` — Validates Dockerfile against project standards
- `check_docker_compose.py` — Checks docker-compose.yml against standardization templates
- `check_service_structure.py` — Validates service directory structure
- `documentation_validator.py` — Validates documentation and markdown files
- `code_quality_validator.py` — Checks code quality metrics
- `container_validator.py` — Validates container structure and metadata
- `test_coverage_validator.py` — Checks test coverage requirements
- (See other scripts in this directory for additional checks)

## Template Usage
All validation scripts that require templates (e.g., for Dockerfiles, README.md, pyproject.toml, etc.) should reference files in the `{project root}/templates/` directory.

## Usage
Run any script directly with Python, e.g.:
```bash
python scripts/validation/check_dockerfile.py
```

See each script's help or docstring for details on usage and options.

# Validation System Documentation

This directory contains documentation for all code and configuration validators in the project.

## System Overview
- The validator system is modular, class-based, and uses Foundation's dependency injection (DI) and schema registry.
- Validators are registered using the `@register_validator` decorator or `ValidatorRegistry().register(...)` and must subclass `ProtocolValidate`.
- All validator schemas are registered with Foundation's schema registry and support versioned retrieval.
- Validators are auto-discovered and orchestrated via the registry and DI container.
- The Python API provides `run_validator(name, target, config)` and `list_validators()`.
- See [VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md) for full standards and patterns.

## YAML Schema Directory (schemas/)
- All YAML-based validator schemas should be placed in the `schemas/` subdirectory of this folder.
- The new YAML-driven registry will automatically discover and load all `.yaml` and `.yml` files in this directory.
- Each schema must include a compliant OmniNode metadata block at the top.
- Contributors should add new validator schemas here and ensure they pass metadata and schema linting checks.

## Registering a New Validator
- Subclass `ProtocolValidate` and implement required methods (`validate`, `get_name`, `metadata`).
- Register the validator using the `@register_validator` decorator, providing name, version, group, and description.
- Define a Pydantic config model for validator configuration.
- Example:

```python
@register_validator(name="my_validator", version="v1", group="custom", description="Describe what this validator does.")
class MyValidator(ProtocolValidate):
    ...
```

## Using the Orchestrator CLI
- The main orchestrator is `scripts/validation/run_validators.py`.
- Run as a module for correct import resolution:

```bash
python3 -m scripts.validation.run_validators --list
python3 -m scripts.validation.run_validators --validators code_quality,solid_checker --target containers/foundation
python3 -m scripts.validation.run_validators --group quality --output json
```
- CLI options include:
  - `--validators` (comma-separated list)
  - `--group` (profile/group)
  - `--target` (path/container)
  - `--output` (text, json, html, sarif)
  - `--auto-fix`, `--dry-run`, `--describe`, `--list`, `--version`

## Foundation DI Patterns & Protocol Inheritance
- All validators should inherit from `ProtocolValidate` and use Foundation's DI patterns.
- See [docs/standards/REGISTRY_METADATA_STANDARD.md](../standards/REGISTRY_METADATA_STANDARD.md) for registry and metadata standards.
- Use absolute imports and ensure all modules are Python packages.

## Metadata Requirements for Validator Schemas

All validator YAML schemas must include a compliant OmniNode metadata block at the top level. This block is required for discoverability, registry integration, and automation.

### Required Fields
- `metadata_version`: Version of the metadata schema (e.g., "0.1")
- `name`: Human-readable name of the validator
- `namespace`: Unique namespace for the validator (e.g., "validators.config")
- `version`: Version of the validator (semantic versioning recommended)
- `entrypoint`: Entrypoint function or script name
- `protocols_supported`: List of supported protocols (e.g., ["omninode_v1"])
- `owner`: Team or individual responsible for the validator

### Sample Metadata Block
```yaml
metadata_version: "0.1"
name: "Example Validator"
namespace: "validators.config"
version: "1.0.0"
entrypoint: "validate_config"
protocols_supported:
  - "omninode_v1"
owner: "validator-team"
```

### Rationale
- Ensures all validators are discoverable and can be managed by the registry and CLI tools.
- Provides accountability and contact information via the `owner` field.
- Enables versioning, deprecation, and compatibility checks.

**All new and updated validator schemas must include this block.**

## Schema Versioning Policy

All validator schemas must include a `version` field in their metadata block. The following policy applies:

- **Semantic Versioning:**
  - Use `MAJOR.MINOR.PATCH` format (e.g., `1.0.0`).
  - Increment MAJOR for breaking changes, MINOR for new features, PATCH for bug fixes or minor updates.
- **Deprecation Workflow:**
  - Deprecated schemas must be marked with a `deprecated: true` field and a `deprecation_message` (optional).
  - Deprecation and removal must be announced in the changelog and documentation.
- **Version Enforcement:**
  - All schemas must have a valid `version` field.
  - The registry and validators will enforce version uniqueness and compliance.

### Example
```yaml
version: "1.2.0"
deprecated: true
deprecation_message: "This schema will be removed in v2.0.0. Use 'new_validator' instead."
```

**All new and updated schemas must comply with this versioning policy.**

# Validator Refactoring Checklist (Schema/Template/Base Conformance)

- [ ] scripts/validation/ast_visitors.py (TestVisitor, ImplementationVisitor)
- [ ] scripts/validation/validate_logger_extra.py (LoggerCallVisitor)
- [ ] scripts/validation/common/test_metrics.py (TestAnalyzer)
- [ ] scripts/validation/common/logger_extra.py (LoggerExtraError)
- [ ] templates/validator.py (TemplateValidator)
- [ ] base/testing_base.py (BaseAsyncTest, BaseIntegrationTest, BaseAPITest)

*Remove each item after inspection/refactor.*
