# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_logging_coverage_validator"
# namespace: "omninode.tools.test_validate_logging_coverage_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_logging_coverage_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import textwrap
from pathlib import Path

import pytest
from foundation.script.validation.validate_logging_coverage import (
    LoggingCoverageValidator,
)
from foundation.script.validation.validator_registry import get_registered_fixture


# Use shared temp directory fixture from the registry
@pytest.fixture
def temp_py_dir():
    fixture_cls = get_registered_fixture()["valid_container_yaml_fixture"]
    return fixture_cls().get_fixture()


def write_py(path: Path, source: str):
    path.write_text(textwrap.dedent(source))


# Valid: each function has required log levels


def test_logging_coverage_validator_valid(temp_py_dir):
    f = temp_py_dir / "good.py"
    write_py(
        f,
        """
    def foo(logger):
        logger.info("msg", extra={"correlation_id": "abc"})
        logger.warning("warn", extra={"context_id": "def"})
        logger.error("err", extra={"correlation_id": "ghi"})
    """,
    )
    validator = LoggingCoverageValidator()
    result = validator.validate(temp_py_dir)
    assert not result.errors


# Invalid: missing required log level


def test_logging_coverage_validator_invalid_structured_and_context(temp_py_dir):
    f = temp_py_dir / "bad.py"
    write_py(
        f,
        """
    def foo(logger):
        logger.info("msg")
        logger.warning("warn")
    """,
    )
    validator = LoggingCoverageValidator()
    result = validator.validate(temp_py_dir)
    assert any(
        "does not use structured/contextual logging" in e.message for e in result.errors
    )
    assert any(
        "does not include a correlation_id or context_id" in e.message
        for e in result.errors
    )


# Edge: syntax error file


def test_logging_coverage_validator_syntax_error(temp_py_dir):
    f = temp_py_dir / "broken.py"
    f.write_text("def foo(:\n    pass")
    validator = LoggingCoverageValidator()
    result = validator.validate(temp_py_dir)
    assert any("Could not parse" in w.message for w in result.warnings)


# NOTE: Log level enforcement is not currently implemented in LoggingCoverageValidator.
# If implemented in the future, add a test for missing required log levels here.