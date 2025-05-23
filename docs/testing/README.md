<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: README.md
version: 1.0.0
uuid: 1538f945-4399-4932-8cc6-50d36f3dd40d
author: OmniNode Team
created_at: 2025-05-22T17:18:16.694862
last_modified_at: 2025-05-22T21:19:13.386829
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: fb51c369560b70e921f8ea0c1195fe8b70c4fc392713f8188a70faf75b4603a5
entrypoint: python@README.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.README
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
