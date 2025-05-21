<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: README.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 38f98629-2efd-4d8d-a18b-9058859794d0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.162595 -->
<!-- last_modified_at: 2025-05-21T16:42:46.055419 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 867a8111a25897eb1d5be4aaeccb94dc56bdb01b79cf77ac4c03f81b82429a06 -->
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
<!-- uuid: 5b10bb37-2c24-4c1e-a9bd-c233bfc624e0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.437942 -->
<!-- last_modified_at: 2025-05-21T16:39:56.742521 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 33fefc36cc2b4d4b26cc19705445f5df686b57b3d920f30852f075d46ed8a92f -->
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
<!-- uuid: 2ca7ccca-168b-437d-b2c3-be3aad0f65d2 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.665149 -->
<!-- last_modified_at: 2025-05-21T16:24:00.310938 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 371af1317a13e22a02b98ba016ad48d0dbbb82a3e866f2e27fbaa324df84d463 -->
<!-- entrypoint: {'type': 'python', 'target': 'README.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.README -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

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
