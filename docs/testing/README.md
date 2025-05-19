<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 25641ef8-f10c-4aca-90df-4cac8550c2f3 -->
<!-- name: README.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:01.618805 -->
<!-- last_modified_at: 2025-05-19T16:20:01.618807 -->
<!-- description: Stamped Markdown file: README.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 5feeeaa70b07f197236b126a01a11b45d8cc471913875a30b2bc4b605b838f68 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'README.md'} -->
<!-- namespace: onex.stamped.README.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# ONEX Testing Guide

This directory contains canonical testing guidance for ONEX/OmniBase.

## Contents

- [Registry Swapping](./registry_swapping.md)
- [Canonical Tests](./canonical_tests.md)
- [Coverage Goals](./coverage_goals.md) *(optional)*

## Canonical Testing Philosophy

ONEX testing emphasizes:
- Directory structure mirroring `src/omnibase/`
- No test markers; use directory structure
- Registry swapping via fixtures
- Contract testing for protocol compliance

See [../nodes/developer_guide.md](../nodes/developer_guide.md) for more details.

---

*This guide will be expanded as the test suite matures. See split-out documents for specific examples and advanced topics.* 
