import pytest

from omnibase.utils.utils_uri_parser import CanonicalUriParser
from tests.utils.utils_test_uri_parser_cases import URI_PARSER_TEST_CASES


@pytest.mark.parametrize(
    "test_case",
    list(URI_PARSER_TEST_CASES.values()),
    ids=list(URI_PARSER_TEST_CASES.keys()),
)
def test_uri_parser_cases(test_case):
    parser = CanonicalUriParser()
    test_case().run(parser)


# TODO: Protocol-based extension and negative/edge cases in M1+
