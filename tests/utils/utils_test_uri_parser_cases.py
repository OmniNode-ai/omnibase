from typing import Any, Callable, Type
import pytest

from omnibase.core.errors import OmniBaseError  # type: ignore[import-untyped]
from omnibase.model.model_enum_metadata import UriTypeEnum  # type: ignore[import-untyped]
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
