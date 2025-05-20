<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: b7c57a77-7ffa-47df-a86a-15bb949ae3c6 -->
<!-- name: stamper.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:38:50.990411 -->
<!-- last_modified_at: 2025-05-19T16:38:50.990414 -->
<!-- description: Stamped Markdown file: stamper.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: bb756d637eb2b9f77ec5b775224cc9e4ea006efdc632c611a99ed685b48bf0dd -->
<!-- entrypoint: {'type': 'markdown', 'target': 'stamper.md'} -->
<!-- namespace: onex.stamped.stamper.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# ONEX Metadata Stamper Tool

> **Status:** Canonical
> **Last Updated:** 2025-05-20
> **Purpose:** Documentation for the ONEX Metadata Stamper Tool

## Overview

The ONEX Metadata Stamper Tool is a command-line utility for stamping metadata files with hashes, signatures, and other metadata. It can operate on individual files or recursively process directories, applying consistent metadata blocks to all eligible files.

## Protocol-Driven, Fixture-Injectable Architecture

The ONEX Metadata Stamper is implemented as a protocol-driven engine, enabling extensibility, testability, and context-agnostic operation. All core logic is defined by Python Protocols, and all dependencies (file I/O, ignore pattern sources, etc.) are injected via constructor or fixture.

### Protocol Registry and Engine Selection

- The stamper engine is registered in a protocol registry, allowing dynamic discovery and selection at runtime or via CLI.
- Multiple engine implementations are supported (e.g., real filesystem, in-memory for tests, hybrid).
- The CLI supports selecting the engine via flags (e.g., `--engine`, `--fixture-context`) or environment variables.

### Dependency Injection and Testability

- All dependencies are injected; no global state or hardcoded paths are used.
- The protocol-driven design enables context-agnostic, registry-driven tests. The same test suite can run against real, in-memory, or mock engines by swapping fixtures.
- See [docs/testing.md](../testing.md) and [docs/structured_testing.md](../structured_testing.md) for canonical patterns.

### CLI Options for Protocol/Fixture Selection

- Use `--engine` to select the protocol engine (e.g., `real`, `in_memory`, `hybrid`).
- Use `--fixture-context` or environment variables to control fixture injection for testability.
- Example:

```bash
poetry run onex stamp directory /path/to/directory --engine in_memory --fixture-context test
```

### Updated Usage and CI Integration

- All CLI and CI workflows now support protocol-driven and fixture-injectable execution.
- Example pre-commit hook:

```yaml
- repo: local
  hooks:
    - id: metadata-stamper
      name: ONEX Metadata Stamper
      entry: poetry run onex stamp directory
      language: system
      args: [--recursive, --engine real]
      types: [yaml, json]
      pass_filenames: false
```

- Example GitHub Actions step:

```yaml
- name: Validate metadata blocks
  run: |
    poetry run onex stamp directory . --recursive --engine real
```

For more details, see [docs/protocols.md](../protocols.md), [docs/registry.md](../registry.md), and [docs/testing.md](../testing.md).

## Installation

The stamper tool is included in the OmniBase package and is installed automatically when you install the package:

```bash
poetry install
```

## Basic Usage

### Stamping a Single File

To stamp a single file:

```bash
poetry run onex stamp /path/to/file.yaml
```

This will compute a trace hash for the file and display the result.

### Stamping a Directory (Recursive)

To stamp all eligible files in a directory and its subdirectories:

```bash
poetry run onex stamp directory /path/to/directory --recursive
```

By default, this will process all `.yaml`, `.yml`, and `.json` files in the directory and its subdirectories.

### Dry Run Mode

To check which files would be stamped without actually modifying them:

```bash
poetry run onex stamp directory /path/to/directory 
```

## Advanced Usage

### File Pattern Filtering

You can specify which files to include or exclude:

```bash
# Include only specific patterns
poetry run onex stamp directory /path/to/directory --include "*.yaml" --include "*.json"

# Exclude specific patterns
poetry run onex stamp directory /path/to/directory --exclude "**/temp/*" --exclude "*.draft.yaml"
```

### Ignore File

You can create a `.onexignore` file in your project root to specify patterns that should always be ignored. This file uses YAML format and supports tool-specific and global ignore patterns:

```
stamper:
  patterns:
    - .git/
    - __pycache__/
    - '*.tmp'
    - '*.draft.yaml'
```

A template `.onexignore` file is provided in the `src/omnibase/templates/` directory.

### Output Formats

The stamper supports multiple output formats:

```bash
# Text output (default)
poetry run onex stamp directory /path/to/directory

# JSON output
poetry run onex stamp directory /path/to/directory --format json
```

## CI Integration

### Pre-commit Hook

The stamper can be integrated with pre-commit to validate metadata blocks before commit. Add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: metadata-stamper
      name: ONEX Metadata Stamper
      entry: poetry run onex stamp directory
      language: system
      args: [--recursive]
      types: [yaml, json]
      exclude: ^(poetry\.lock|\.github/|\.git/|\.venv/|venv/|\.pytest_cache/|\.ruff_cache/|__pycache__/)
      pass_filenames: false
```

This hook will check that all eligible files in your project have valid metadata blocks.

### GitHub Actions

Example GitHub Actions workflow for validating metadata blocks:

```yaml
name: Validate Metadata Blocks

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    - name: Validate metadata blocks
      run: |
        poetry run onex stamp directory . --recursive
```

## Command-Line Reference

### Single File Stamping

```
Usage: onex stamp [OPTIONS] PATH

  Stamp an ONEX node metadata file with a hash and timestamp.

Arguments:
  PATH  Path to file to stamp  [required]

Options:
  -a, --author TEXT       Author to include in stamp
  -t, --template TEXT     Template type (minimal, full, etc.)
  -o, --overwrite         Overwrite existing metadata block
  -r, --repair            Repair malformed metadata block
  -f, --format TEXT       Output format (text, json)
  --help                  Show this message and exit.
```

### Directory Stamping

```
Usage: onex stamp directory [OPTIONS] DIRECTORY

  Process all eligible files in a directory, stamping each one.

  This command recursively traverses a directory, finds all YAML and JSON
  files, and stamps each file with a metadata block. Files can be filtered
  using include/exclude patterns or a .onexignore file.

  Example usage:
      onex stamp directory ./src --recursive
      onex stamp directory ./schemas --include "*.yaml" --include "*.json"

Arguments:
  DIRECTORY  Directory to process  [required]

Options:
  -r, --recursive        Recursively process subdirectories  [default: True]  
  -i, --include TEXT     File patterns to include (e.g., '*.yaml')
  -e, --exclude TEXT     File patterns to exclude
  --ignore-file PATH     Path to .onexignore file
  -t, --template TEXT    Template type (minimal, full, etc.)  [default: minimal]
  -a, --author TEXT      Author to include in stamp  [default: OmniNode Team]
  -o, --overwrite        Overwrite existing metadata blocks  [default: False]
  --repair               Repair malformed metadata blocks  [default: False]
  --force                Force overwrite of existing metadata blocks  [default: False]
  -f, --format TEXT      Output format (text, json)  [default: text]
  --help                 Show this message and exit.
```

# ONEX Metadata Stamper CLI

## Usage

The ONEX Metadata Stamper CLI supports stamping metadata blocks into eligible files. The following command-line arguments are supported:

### Required and Optional Arguments

- `directory <path>`: Directory to process (required for directory mode)
- `--recursive, -r`: Recursively process subdirectories (default: only top-level directory)
- `--write, -w`: Actually write changes to files (default: dry run; required for stamping to occur)
- `--include, -i <pattern>`: File patterns to include (e.g., `*.yaml`, `**/*.md`)
- `--exclude, -e <pattern>`: File patterns to exclude
- `--ignore-file <path>`: Path to a `.onexignore` file
- `--template, -t <type>`: Template type (`minimal`, `full`, etc.; default: `minimal`)
- `--author, -a <name>`: Author to include in the stamp (default: `OmniNode Team`)
- `--overwrite, -o`: Overwrite existing metadata blocks (default: false)
- `--repair`: Repair malformed metadata blocks (default: false)
- `--force`: Force overwrite of existing metadata blocks (default: false)
- `--format, -f <format>`: Output format (`text`, `json`; default: `text`)
- `--fixture <path>`: Path to JSON or YAML fixture for protocol-driven testing
- `--discovery-source <mode>`: File discovery source (`filesystem`, `tree`, `hybrid_warn`, `hybrid_strict`; default: `filesystem`)
- `--enforce-tree`: Error on drift between filesystem and .tree (alias for `hybrid_strict`)
- `--tree-only`: Only process files listed in .tree (alias for `tree`)

### Dry Run vs. Write Mode

- By default, the CLI runs in **dry run** mode and will only show what would be stamped.
- To actually write changes, you **must** specify the `--write` (or `-w`) flag.

### Example Usage

- Dry run (default):
  ```sh
  poetry run python -m omnibase.tools.cli_stamp directory .
  ```
- Actually write changes, recursively:
  ```sh
  poetry run python -m omnibase.tools.cli_stamp directory . --recursive --write
  ```
- Stamp only markdown files (dry run):
  ```sh
  poetry run python -m omnibase.tools.cli_stamp file '**/*.md'
  ```
- Stamp only YAML files, excluding testdata (write mode, recursively):
  ```sh
  poetry run python -m omnibase.tools.cli_stamp directory . --include '**/*.yaml' --exclude 'tests/**' --recursive --write
  ```
- Stamp a single file:
  ```sh
  poetry run python -m omnibase.tools.cli_stamp file docs/dev_logs/jonah/debug/debug_log_2025_05_18.md --author "jonah"
  ```

For more details, see the CLI help (`--help`) or the source code in `src/omnibase/tools/cli_stamp.py`. 
