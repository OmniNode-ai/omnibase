<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:27.185805'
description: Stamped by ONEX
entrypoint: python://README.md
hash: 1d261f1c270363f5b1abbf6a2a6f5e02891461be7839299a54b4ec7f7fd851c0
last_modified_at: '2025-05-29T11:50:15.380840+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: README.md
namespace: omnibase.README
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 76ca23ce-9d51-419c-bc4e-4cfc3e28ab4e
version: 1.0.0

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
