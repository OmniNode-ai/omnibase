# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.471349'
# description: Stamped by PythonHandler
# entrypoint: python://utils_test_uri_parser_cases.py
# hash: 43a5e1323fba7472219872a18578aeddaf3b43bfbdd0364d1465017cb34970f7
# last_modified_at: '2025-05-29T13:51:24.282597+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: utils_test_uri_parser_cases.py
# namespace: py://omnibase.tests.utils.utils_test_uri_parser_cases_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 26419909-0a31-4a14-aa79-d42e3470c34f
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Callable

import pytest

from omnibase.enums import UriTypeEnum  # type: ignore[import-untyped]
from omnibase.exceptions import OmniBaseError  # type: ignore[import-untyped]
from omnibase.model.model_uri import OnexUriModel  # type: ignore[import-untyped]

URI_PARSER_TEST_CASES: dict[str, type] = {}


def register_uri_parser_test_case(name: str) -> Callable[[type], type]:
    """Decorator to register a test case class in the URI parser test case registry."""

    def decorator(cls: type) -> type:
        URI_PARSER_TEST_CASES[name] = cls
        return cls

    return decorator


@register_uri_parser_test_case("valid_tool_uri")
class ValidToolUriCase:
    def run(self, parser: Any, context: Any) -> None:
        uri = "tool://core.schema_validator@1.0.0"
        result = parser.parse(uri)
        assert isinstance(result, OnexUriModel)
        assert result.type == UriTypeEnum.TOOL
        assert result.namespace == "core.schema_validator"
        assert result.version_spec == "1.0.0"
        assert result.original == uri


@register_uri_parser_test_case("valid_validator_uri")
class ValidValidatorUriCase:
    def run(self, parser: Any, context: Any) -> None:
        uri = "validator://core.base@^1.0"
        result = parser.parse(uri)
        assert isinstance(result, OnexUriModel)
        assert result.type == UriTypeEnum.VALIDATOR
        assert result.namespace == "core.base"
        assert result.version_spec == "^1.0"
        assert result.original == uri


@register_uri_parser_test_case("invalid_type_uri")
class InvalidTypeUriCase:
    def run(self, parser: Any, context: Any) -> None:
        uri = "notatype://foo.bar@1.0.0"
        with pytest.raises(OmniBaseError):
            parser.parse(uri)


@register_uri_parser_test_case("missing_version_uri")
class MissingVersionUriCase:
    def run(self, parser: Any, context: Any) -> None:
        uri = "tool://core.schema_validator"
        with pytest.raises(OmniBaseError):
            parser.parse(uri)


# TODO: Protocol-based extension and negative/edge cases in M1+
