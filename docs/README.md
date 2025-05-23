<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: 59785c61-bf82-4f0a-96f0-66b0e71e1f5f
author: OmniNode Team
created_at: 2025-05-22T17:18:16.674130
last_modified_at: 2025-05-22T21:19:13.631314
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 0d70322e52ffed6720844e39f0f9e40cb047cbc97f2a18c5afa8f01c3bf19e07
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.README
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase / ONEX Documentation

Welcome to the OmniBase (ONEX) documentation. This is the canonical source for architecture, onboarding, and reference materials for the ONEX node execution protocol.

---

## Bootstrap Milestone (M0)
- **Purpose:** Establish the foundational structure, protocols, and CLI for ONEX.
- **Includes:**
  - Canonical directory structure
  - Protocol and registry stubs
  - CLI entrypoint (`onex`)
  - Example templates and schemas
  - Onboarding and architecture docs

---

## Directory Structure

```
/ (repo root)
├── README.md                # Project summary and onboarding
├── docs/                    # Documentation (this folder)
│   ├── guides/              # Getting started, CLI, advanced usage
│   ├── nodes/               # Node Architecture Series
│   ├── milestones/          # Milestone checklists and overviews
│   ├── onex/                # ONEX protocol primer and index
│   └── testing/             # Canonical testing guidance
├── src/omnibase/            # Source code (core, protocol, tools, etc.)
└── tests/                   # Test suite (mirrors src/omnibase/)
```

---

## Running the CLI and Tests

1. **Install dependencies:**
   - With Poetry: `poetry install`
   - Or see [guides/getting_started.md](guides/getting_started.md)
2. **Run the ONEX CLI:**
   ```bash
   poetry run onex --help
   ```
3. **Validate an example node:**
   ```bash
   poetry run onex validate nodes/example_node/node.onex.yaml
   ```
4. **Run tests:**
   ```bash
   poetry run pytest
   ```

---

## Key Documentation
- [ONEX Protocol Primer](onex/index.md)
- [Node Architecture Series](nodes/index.md)
- [Milestone Overview](milestones/overview.md)
- [Developer Guide](nodes/developer_guide.md)

For more, see the [project README](../README.md) or ask in the project chat.
