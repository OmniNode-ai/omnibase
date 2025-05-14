# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_logger_extra_validator"
# namespace: "omninode.tools.test_validate_logger_extra_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_validate_logger_extra_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import textwrap
from pathlib import Path

import pytest
from foundation.fixture.fixture_helper import TestHelper
from foundation.script.validate.python.python_validate_logger_extra import ProtocolLoggerExtraValidator
from foundation.script.validate.validate_registry import (
    get_fixture_by_interface,
    get_registered_fixture,
)
import foundation.fixture.directory.python.python_fixture_directory
import foundation.fixture.fixture_helper


# Use shared temp directory fixture from the registry
@pytest.fixture
def temp_py_dir():
    # Use the valid_container_yaml_fixture as a generic temp dir provider for now
    fixture_cls = get_registered_fixture("valid_container_yaml_fixture")
    return fixture_cls().get_fixture()


def write_py(path: Path, source: str):
    path.write_text(textwrap.dedent(source))


# Valid: logger call with make_logger_extra and all required fields


def test_logger_extra_validator_valid(temp_py_dir):
    f = temp_py_dir / "good.py"
    write_py(
        f,
        """
    from foundation.script.validate.common.common_logger_extra import make_logger_extra
    def foo(logger):
        logger.info("msg", extra=make_logger_extra(request_id="abc", user_id="u", session_id="s"))
    """,
    )
    validator = ProtocolLoggerExtraValidator()
    result = validator.validate(temp_py_dir)
    assert result.is_valid
    assert not result.errors


# Invalid: logger call with extra not from make_logger_extra


def test_logger_extra_validator_invalid_not_make(temp_py_dir):
    f = temp_py_dir / "bad.py"
    write_py(
        f,
        """
    def foo(logger):
        logger.info("msg", extra={"request_id": "abc"})
    """,
    )
    validator = ProtocolLoggerExtraValidator()
    result = validator.validate(temp_py_dir)
    assert not result.is_valid
    helper = get_registered_fixture("test_helper")()
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "make_logger_extra", str(f))


# Invalid: missing required fields


def test_logger_extra_validator_invalid_missing_required(temp_py_dir):
    f = temp_py_dir / "bad2.py"
    write_py(
        f,
        """
    from foundation.script.validate.common.common_logger_extra import make_logger_extra
    def foo(logger):
        logger.info("msg", extra=make_logger_extra(user_id="u"))
    """,
    )
    validator = ProtocolLoggerExtraValidator()
    result = validator.validate(temp_py_dir)
    assert not result.is_valid
    helper = get_registered_fixture("test_helper")()
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "missing required fields", str(f))


# Edge: syntax error file


def test_logger_extra_validator_syntax_error(temp_py_dir):
    f = temp_py_dir / "broken.py"
    f.write_text("def foo(:\n    pass")
    validator = ProtocolLoggerExtraValidator()
    result = validator.validate(temp_py_dir)
    assert not result.is_valid
    helper = get_registered_fixture("test_helper")()
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "Could not parse", str(f))


def test_logger_extra(tmp_path):
    # If TestHelper is not registered, instantiate directly
    helper = TestHelper()
    # .. rest of the test ..