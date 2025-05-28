# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: f5009d39-2de7-4f4f-a827-46e64366e4ab
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.825239
# last_modified_at: 2025-05-28T17:20:04.016469
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2e2305fef4acb5be16718a2d40d8ce8b45a3b5276c6088b0b67dcd71e5559e59
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.init
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
