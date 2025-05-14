# OmniBase/ONEX Naming Conventions and Standards

> **Status:** Canonical
> **Last Updated:** 2025-05-17
> **Purpose:** Define and enforce naming conventions and standards for all files, directories, and code artifacts in the project. All contributors must follow these rules for consistency, maintainability, and discoverability.

---

## 1. General File and Directory Naming
- Use all-lowercase with underscores for Python files and directories. Prefix each module filename with its parent directory or functional scope for disambiguation:  
  - `core_registry.py`, `core_schema_loader.py` for files in `core/`  
  - `protocol_registry.py`, `protocol_validate.py` for files in `protocol/`  
  - `cli_validator.py`, `cli_stamp.py` for CLI tools in `tools/`  
- Avoid camelCase or PascalCase in filenames. Prefer plural directory names for related modules: `schemas/`, `tools/`, `tests/`, `protocol/`.

```
Example:
src/omnibase/
├── core/
│   └── core_registry.py
│   └── core_schema_loader.py
├── protocol/
│   └── protocol_registry.py
│   └── protocol_validate.py
├── tools/
│   └── cli_validator.py
│   └── cli_stamp.py
```

## 2. Protocols and Interfaces
- Place all protocol files in `src/omnibase/protocol/`.
- Protocol file names: lowercase, underscores, prefixed with `protocol_` (e.g., `protocol_registry.py`, `protocol_validate.py`).
- Protocol class names: PascalCase, prefixed with `Protocol` (e.g., `ProtocolRegistry`).
- Each protocol file should contain only one protocol class unless tightly coupled.
  
This aligns protocol files with other module naming patterns for consistency and avoids namespace conflicts.

## 3. Test Files
- All test files must start with `test_` and use descriptive, lowercase names: `test_registry.py`, `test_validator.py`.
- Parametrized or data-driven test files may use suffixes: `test_registry_parametrized.py`.
- Place all tests under the `tests/` directory, organized by module or feature.

## 4. Templates and Example Files
- Use `template_` prefix for all template files: `template_validator.py`, `template_registry.py`.
- Place templates in a dedicated `templates/` directory under `src/omnibase/`.

## 5. CLI Tools and Entry Points
- CLI tool files should be named with the `cli_` prefix after the command they expose, all lowercase: `cli_validate.py`, `cli_stamp.py`, `cli_main.py`.
- Document the mapping between file and CLI command in the README or CLI help text.

## 6. Utilities
- Place utility modules in a `utils/` directory and name for their function: `hashing.py`, `file_io.py`, `string_normalization.py`.

## 7. Schema and Data Files
- Use all-lowercase, hyphen-separated for YAML/JSON schema files: `onex-node.yaml`, `metadata-schema.json`.
- Place all schemas in the canonical location: `src/omnibase/schema/schemas/`.

## 8. Versioning and Migration
- For versioned files (schemas, protocols), use a suffix: `registry_v1.py`, `onex-node-v1.yaml`.
- For deprecated or legacy files, use a `legacy_` prefix or move to a `legacy/` directory.

## 9. Doc and Markdown Files
- Use lowercase, hyphen-separated names for markdown files: `testing.md`, `migration-log.md`, `milestone-0-bootstrap.md`.
- Place all documentation in the `docs/` directory.

## 10. Enforcement and Documentation
- All naming conventions must be documented in this file and referenced in `README.md` and `docs/testing.md`.
- Add a checklist item to each milestone to enforce naming conventions in code review and CI (optionally via a linter or pre-commit hook).
- Any changes to naming conventions must be reviewed and versioned in this document.
- The parent-directory-prefixed filename convention (e.g., `core_registry.py`) is a deliberate deviation from standard Python naming to avoid filename collisions and improve clarity when multiple modules with similar names exist across different directories.

---

> This document is canonical. All contributors must follow these standards for all new and existing files. Deviations must be justified and reviewed. 
## 11. Reserved Naming Prefixes

To ensure clarity and avoid conflicts across modules, the following prefixes must be used consistently:

| Prefix         | Usage                              |
|----------------|-------------------------------------|
| `core_`        | Core internal logic and registries  |
| `protocol_`    | Protocol definitions and interfaces |
| `cli_`         | CLI tools or entrypoints in `tools/` directory            |
| `test_`        | All test files                      |
| `template_`    | Template files                      |
| `legacy_`      | Deprecated or transitional modules  |

These prefixes must appear at the start of the filename, matching the directory the file lives in.