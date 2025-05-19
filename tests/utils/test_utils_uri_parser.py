# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: c6f78640-dd14-4af6-ba81-24ddfdb594a9
# name: test_utils_uri_parser.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:57.395610
# last_modified_at: 2025-05-19T16:19:57.395612
# description: Stamped Python file: test_utils_uri_parser.py
# state_contract: none
# lifecycle: active
# hash: 34659f16c7440e0e6636e9078f2ce6c9a7105d057fd4cce9640bb12f4d1de89f
# entrypoint: {'type': 'python', 'target': 'test_utils_uri_parser.py'}
# namespace: onex.stamped.test_utils_uri_parser.py
# meta_type: tool
# === /OmniNode:Metadata ===

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

from typing import Any

import pytest

from omnibase.utils.utils_uri_parser import CanonicalUriParser
from tests.utils.utils_test_uri_parser_cases import URI_PARSER_TEST_CASES


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request: pytest.FixtureRequest) -> Any:  # type: ignore[no-any-return]
    # Return type is Any due to pytest param mechanics; see ONEX test standards
    return request.param


@pytest.mark.parametrize(
    "context", ["mock", "integration"], ids=["mock", "integration"]
)
@pytest.mark.parametrize(
    "test_case",
    list(URI_PARSER_TEST_CASES.values()),
    ids=list(URI_PARSER_TEST_CASES.keys()),
)
def test_utils_uri_parser_cases(test_case: type, context: str) -> None:
    """Test URI parser cases for both mock and integration contexts."""
    parser = CanonicalUriParser()
    test_case().run(parser, context)


# TODO: Protocol-based extension and negative/edge cases in M1+


def get_uri_type(uri: str) -> str:
    """Return the type of the given URI as a string (stub for standards compliance)."""
    return "mock_type"


# Remove parse_uri if not used or if it causes type issues
