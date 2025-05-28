<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: 25964514-03fe-407a-8d3c-17770db5918c
author: OmniNode Team
created_at: 2025-05-28T12:40:26.380605
last_modified_at: 2025-05-28T17:20:03.768468
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 325c469860ea25e417e84bcf926ff93e8efc28f7e323a46bdd6079ae9eb42595
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.index
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX CLI Guide

This guide covers the ONEX command-line interface, including installation, quickstart, and advanced usage.

## Quickstart

See [../getting_started.md](../getting_started.md) for environment setup and first-run instructions.

## CLI Overview

- `onex --help` — Show all available commands
- `onex validate <path>` — Validate a node metadata file
- `onex scaffold ...` — Scaffold new nodes and components (future)

## Usage Examples

```bash
onex validate nodes/example_node/node.onex.yaml
```

## Advanced Topics

- CLI configuration (TBD)
- Custom templates (TBD)
- Debugging and troubleshooting (TBD)

---

*This guide will be expanded as the CLI matures. For now, see the [Developer Guide](../../nodes/developer_guide.md) and [Getting Started](../getting_started.md) for more details.*
