<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: 76ca23ce-9d51-419c-bc4e-4cfc3e28ab4e
author: OmniNode Team
created_at: 2025-05-28T12:40:27.185805
last_modified_at: 2025-05-28T17:20:03.923572
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 8e6404bb4413961f8d027ab024dcacc694dcddc7f1d609a2e86411c003d4c1a5
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.README
meta_type: tool
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
