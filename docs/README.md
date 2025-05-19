<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 3df61d3e-6324-4c40-a4f0-8d580b02b206 -->
<!-- name: README.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:52.027600 -->
<!-- last_modified_at: 2025-05-19T16:19:52.027606 -->
<!-- description: Stamped Markdown file: README.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: deafe2fcab38f498d8324a33673a68af0c4be24c542ac7c465eb7225c559a8d3 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'README.md'} -->
<!-- namespace: onex.stamped.README.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
