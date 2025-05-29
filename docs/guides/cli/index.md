<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.380605'
description: Stamped by ONEX
entrypoint: python://index.md
hash: e8efa295a3082e550e81af49f84f8cb7d3e50a9417be9c815f965b07b1bedca8
last_modified_at: '2025-05-29T11:50:14.946545+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: index.md
namespace: omnibase.index
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 25964514-03fe-407a-8d3c-17770db5918c
version: 1.0.0

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
