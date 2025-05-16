"""
Canonical registry-driven test harness.

- Markerless: No test-level markers; context is handled by fixture injection only.
- All test cases (positive and negative) must be registered in CORE_REGISTRY_TEST_CASES with unique IDs.
- The registry is the single source of truth for test coverage and is designed for plugin/extensible import in future milestones (see docs/testing.md).
- Test runner files (e.g., test_registry.py) must not define test cases directly—import and parameterize over the registry only.
- IDs are surfaced in pytest output and CI reporting for coverage and review.
- See tests/core/core_test_registry_cases.py for the canonical source of test cases.
"""

import pytest
from tests.core.core_test_registry_cases import CORE_REGISTRY_TEST_CASES

@pytest.mark.parametrize("test_case", list(CORE_REGISTRY_TEST_CASES.values()), ids=list(CORE_REGISTRY_TEST_CASES.keys()))
def test_registry_cases(registry, test_case):
    test_case().run(registry)
