# Foundation Schema Directory

This directory contains all canonical, project-wide schema files for OmniNode Foundation.

## Naming Convention
- **All schema files must use the `schema_` prefix.**
  - Example: `schema_treerules.yaml`, `schema_template.yaml`, `schema_metadata.yaml`
- This ensures discoverability, consistency, and automation support.

## Directory Policy
- This is the **only** canonical location for project-wide schemas.
- Validator- or test-specific schemas may exist in their respective submodules, but all shared schemas must be present here.

## Automation
- Pre-commit and CI checks should enforce the `schema_` prefix for all files in this directory.
- See `check_schema_prefix.sh` and `check_schema_prefix.py` for automation examples. 