"""
Standards-Compliant Test File for ONEX/OmniBase URI Parser

This file follows the canonical test pattern as demonstrated in tests/utils/test_node_metadata_extractor.py. It demonstrates:
- Naming conventions: test_ prefix, lowercase, descriptive
- Context-agnostic, registry-driven, fixture-injected testing
- Use of both mock (unit) and integration (real) contexts via pytest fixture parametrization
- No global state; all dependencies are injected
- Registry-driven test case execution pattern
- Compliance with all standards in docs/standards.md and docs/testing.md

All new URI parser tests should follow this pattern unless a justified exception is documented and reviewed.
"""

import pytest

from omnibase.utils.utils_uri_parser import CanonicalUriParser
from tests.utils.utils_test_uri_parser_cases import URI_PARSER_TEST_CASES


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request):
    return request.param


@pytest.mark.parametrize(
    "context", ["mock", "integration"], ids=["mock", "integration"]
)
@pytest.mark.parametrize(
    "test_case",
    list(URI_PARSER_TEST_CASES.values()),
    ids=list(URI_PARSER_TEST_CASES.keys()),
)
def test_utils_uri_parser_cases(test_case, context):
    """Test URI parser cases for both mock and integration contexts."""
    parser = CanonicalUriParser()
    test_case().run(parser, context)


# TODO: Protocol-based extension and negative/edge cases in M1+
