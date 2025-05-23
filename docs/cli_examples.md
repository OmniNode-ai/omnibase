<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: cli_examples.md
version: 1.0.0
uuid: c8d2799b-2311-449d-b7de-c3a5a670f36d
author: OmniNode Team
created_at: 2025-05-22T06:13:42.301217
last_modified_at: 2025-05-22T21:19:13.557192
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2f6f6b2788c642068d55fc862e18246827025ba77ad891332af02dbf1cafd718
entrypoint: python@cli_examples.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.cli_examples
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
