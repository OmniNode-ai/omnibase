<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: bc66ea4e-f070-450e-8723-ce5bd37adc88
author: OmniNode Team
created_at: 2025-05-22T17:18:16.683453
last_modified_at: 2025-05-22T21:19:13.404363
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 5dc1558c4b1122eaea7c531589c9da6e53a53708c72c194e383ca89c7f2e1804
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.index
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
