# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: 37111f13-eec7-46bf-a526-440dd6327b9d
# author: OmniNode Team
# created_at: 2025-05-27T12:45:25.041559
# last_modified_at: 2025-05-27T16:48:17.239525
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 029bb80aff69ed21aa8ad6d7faad192d79e3012643e682d9039ccb6af65b2e7b
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.init
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ONEX Tests Package

This package contains all centralized tests for the ONEX/OmniBase system.
Tests are organized by functional area and follow the canonical testing standards
defined in docs/testing.md.

Directory Structure:
- core/: Core system tests (moved from src/omnibase/core/core_tests/)
- utils/: Utility tests (moved from src/omnibase/utils/utils_tests/)
- model/: Model and schema tests
- protocol/: Protocol compliance tests
- fixtures/: Test fixtures and mocks
- validation/: Validation system tests
- shared/: Shared test utilities
- schemas/: Schema validation tests
- runtime/: Runtime system tests
- ci_tests/: CI-specific tests
- data/: Test data files

Note: Node-local tests remain in their respective node directories following
the ONEX node architecture pattern.
"""
