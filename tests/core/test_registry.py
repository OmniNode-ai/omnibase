# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: test_registry.py
# version: 1.0.0
# uuid: 4ac79dba-c3ed-4213-ad90-5989aebbf629
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.170314
# last_modified_at: 2025-05-21T16:42:46.087613
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 335732d3a85705df8a6f83c2824611f6917a007643011c99aaebadd19729364c
# entrypoint: python@test_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_registry
# meta_type: tool
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
