# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: db49a89a-9245-4427-87f3-c32d362b2b2d
# name: utils_test_uri_parser_cases.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.237828
# last_modified_at: 2025-05-19T16:19:55.237830
# description: Stamped Python file: utils_test_uri_parser_cases.py
# state_contract: none
# lifecycle: active
# hash: 7b76a90d9b6afc7f0bb2710a329b693779c8c014458968dc22596c01afc63656
# entrypoint: {'type': 'python', 'target': 'utils_test_uri_parser_cases.py'}
# namespace: onex.stamped.utils_test_uri_parser_cases.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any, Callable

import pytest

from omnibase.core.errors import OmniBaseError  # type: ignore[import-untyped]
from omnibase.model.model_enum_metadata import (
    UriTypeEnum,  # type: ignore[import-untyped]
)
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
