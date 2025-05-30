<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: cli_examples.md
version: 1.0.0
uuid: 593497d2-57d1-4de1-8dd4-0de7d8f0c8cc
author: OmniNode Team
created_at: '2025-05-28T12:40:25.966073'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://cli_examples
namespace: markdown://cli_examples
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# ONEX CLI Examples Cookbook

> **Purpose:** This file is a living reference of real, working CLI commands for all major ONEX tools and nodes. It complements [cli_interface.md](./cli_interface.md), which defines the canonical interface and flag conventions. This file is for practical usage and should be updated as new features and tools are added.

---

## Stamper Node

### Generate a Canonical Metadata Block
- **Description:** Generate a canonical ONEX metadata block for YAML files
- **Command:**
  ```bash
  onex stamper -g -e yaml
  # or
  onex stamper --gen-block --ext yaml
  ```
- **Example Output:**
  ```yaml
  # === OmniNode:Metadata ===
  # schema_version: 1.0.0
  # name: example
  # ...
  # === /OmniNode:Metadata ===
  ```
- **Notes:**
  - See [cli_interface.md](./cli_interface.md) for flag/option standards and extensibility rules.
  - Use `-e py` or `-e md` for other formats (if supported).

---

## [Add more tools/nodes here]

- For each, include a description, command, output, and notes.
- Keep this file up to date as the CLI evolves.
