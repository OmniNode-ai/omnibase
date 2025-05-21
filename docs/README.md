<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: README.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 44cd275b-239a-4e70-b11b-590554bccd1a -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.155492 -->
<!-- last_modified_at: 2025-05-21T16:42:46.066377 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a0f309a459c24c2a27d6d364b16f4529e8e02b9016c52605af8214f536c75c58 -->
<!-- entrypoint: {'type': 'python', 'target': 'README.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.README -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: README.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 54ba9f6b-17af-42dd-9788-fea6fcc64fcd -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.430501 -->
<!-- last_modified_at: 2025-05-21T16:39:55.718402 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 3bafc7a0fc2b694d13b9c85f977357b9618fca2ff09af5cb94352371ed06dfcc -->
<!-- entrypoint: {'type': 'python', 'target': 'README.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.README -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: README.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 0443984b-449e-4c25-9dd5-017c4d498cf3 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.658903 -->
<!-- last_modified_at: 2025-05-21T16:24:00.305447 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 7e34e1e8d27f9a28eb8470c79fd55e05e2b2d64e9321ea4233be5cbdecbbb0b6 -->
<!-- entrypoint: {'type': 'python', 'target': 'README.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.README -->
<!-- meta_type: tool -->
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
