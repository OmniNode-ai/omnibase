# YAML Validator Schemas Directory

This directory contains all YAML-based validator schemas for the OmniNode validation system.

## Usage
- Place each new validator schema as a `.yaml` or `.yml` file in this directory.
- Each schema **must** include a compliant OmniNode metadata block at the top (see below).
- The YAML-driven registry will automatically discover and load all schemas in this directory.

## Metadata Block Example
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

## Requirements
- All schemas must pass metadata and schema linting checks before merge.
- See the main validation README for more details and links to standards.
