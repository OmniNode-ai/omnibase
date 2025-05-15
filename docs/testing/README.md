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