# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: f18f02a0-d75e-4875-8012-65c00e7633c8
# name: test_registry.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:00.556380
# last_modified_at: 2025-05-19T16:20:00.556383
# description: Stamped Python file: test_registry.py
# state_contract: none
# lifecycle: active
# hash: 35b8909b3885172a8d97bafb97f3c1439caf39427f7a8b67ff19bfda52bf7837
# entrypoint: {'type': 'python', 'target': 'test_registry.py'}
# namespace: onex.stamped.test_registry.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Canonical registry-driven test harness.

- Markerless: No test-level markers; context is handled by fixture injection only.
- All test cases (positive and negative) must be registered in CORE_REGISTRY_TEST_CASES with unique IDs.
- The registry is the single source of truth for test coverage and is designed for plugin/extensible import in future milestones (see docs/testing.md).
- Test runner files (e.g., test_registry.py) must not define test cases directly—import and parameterize over the registry only.
- IDs are surfaced in pytest output and CI reporting for coverage and review.
- See tests/core/core_test_registry_cases.py for the canonical source of test cases.
"""

from typing import Any

import pytest

from tests.core.core_test_registry_cases import CORE_REGISTRY_TEST_CASES


@pytest.mark.parametrize(
    "test_case",
    list(CORE_REGISTRY_TEST_CASES.values()),
    ids=list(CORE_REGISTRY_TEST_CASES.keys()),
)
def test_registry_cases(registry: dict[str, Any], test_case: type) -> None:
    """Run a registry-driven test case from the canonical registry."""
    test_case().run(registry)
