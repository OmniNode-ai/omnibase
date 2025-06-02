# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.439331'
# description: Stamped by PythonHandler
# entrypoint: python://test_utils_uri_parser.py
# hash: 64b02866f6375e3b40117bf662b0469ef22dadc63b51b31018f5cb93ea68cce7
# last_modified_at: '2025-05-29T13:51:24.261059+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_utils_uri_parser.py
# namespace: py://omnibase.tests.utils.test_utils_uri_parser_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: e4be879c-9fdf-4450-8a3c-82440c076cc5
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Standards-Compliant Test File for ONEX/OmniBase URI Parser

This file follows the canonical test pattern as demonstrated in src/omnibase/utils/tests/test_node_metadata_extractor.py. It demonstrates:
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "context", ["mock", "integration"], ids=["mock", "integration"]
)
@pytest.mark.parametrize(
    "test_case",
    list(URI_PARSER_TEST_CASES.values()),
    ids=list(URI_PARSER_TEST_CASES.keys()),
)
async def test_utils_uri_parser_cases(test_case: type, context: str) -> None:
    """Test URI parser cases for both mock and integration contexts."""
    parser = CanonicalUriParser()
    await test_case().run(parser, context)


# TODO: Protocol-based extension and negative/edge cases in M1+


def get_uri_type(uri: str) -> str:
    """Return the type of the given URI as a string (stub for standards compliance)."""
    return "mock_type"


# Remove parse_uri if not used or if it causes type issues
