<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:25.966073'
description: Stamped by ONEX
entrypoint: python://cli_examples.md
hash: 0822fe7390c650131d4162221ed0db8ec35d669afa807d0c333f4d535be577e2
last_modified_at: '2025-05-29T11:50:14.660559+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: cli_examples.md
namespace: omnibase.cli_examples
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 593497d2-57d1-4de1-8dd4-0de7d8f0c8cc
version: 1.0.0

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
