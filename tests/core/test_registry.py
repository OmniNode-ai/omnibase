# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.315687'
# description: Stamped by PythonHandler
# entrypoint: python://test_registry.py
# hash: 9e962b141e14a09c0ba4720a287fdedd376900d2dc1a445b099817c2eb57d98d
# last_modified_at: '2025-05-29T11:50:12.593461+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_registry.py
# namespace: omnibase.test_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: f897ad11-c9f3-4aaf-abcf-9d34e6a82336
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Canonical registry-driven test harness.

- Markerless: No test-level markers; context is handled by fixture injection only.
- All test cases (positive and negative) must be registered in CORE_REGISTRY_TEST_CASES with unique IDs.
- The registry is the single source of truth for test coverage and is designed for plugin/extensible import in future milestones (see docs/testing.md).
- Test runner files (e.g., test_registry.py) must not define test cases directly—import and parameterize over the registry only.
- IDs are surfaced in pytest output and CI reporting for coverage and review.
- See src/omnibase/core/tests/core_test_registry_cases.py for the canonical source of test cases.

MIGRATION NOTE: Updated to use registry_loader_context fixture which provides direct access
to registry loader node functionality without the old ProtocolRegistry interface layer.
"""

from typing import Any

import pytest

from tests.core.core_test_registry_cases import CORE_REGISTRY_TEST_CASES


@pytest.mark.parametrize(
    "test_case",
    list(CORE_REGISTRY_TEST_CASES.values()),
    ids=list(CORE_REGISTRY_TEST_CASES.keys()),
)
def test_registry_cases(registry_loader_context: Any, test_case: type) -> None:
    """Run a registry-driven test case from the canonical registry."""
    test_case().run(registry_loader_context)
