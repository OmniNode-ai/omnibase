# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.825239'
# description: Stamped by PythonHandler
# entrypoint: python://__init__.py
# hash: 7ed52fe69db99fad23586dc613ae4c8e1740ee55a0b190aa978af211f7b603cb
# last_modified_at: '2025-05-29T13:51:23.002291+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: py://omnibase.tests.__init___py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: f5009d39-2de7-4f4f-a827-46e64366e4ab
# version: 1.0.0
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
