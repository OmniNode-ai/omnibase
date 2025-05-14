# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_code_quality"
# namespace: "omninode.tools.test_python_code_quality"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_python_code_quality.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from pathlib import Path

import pytest
from foundation.script.validate.validate_registry import get_registered_fixture


@pytest.fixture
def code_quality_validator() -> object:
    fixture_cls = get_registered_fixture()["code_quality_validator_fixture"]
    return fixture_cls().get_fixture()


def test_good_code(code_quality_validator: object) -> None:
    good_path = (
        Path(__file__).parent / "test_cases" / "code_quality" / "valid" / "good_code.py"
    )
    assert code_quality_validator.validate(
        good_path
    ), "Expected good_code.py to pass code quality validation"


def test_bad_code(code_quality_validator: object) -> None:
    bad_path = (
        Path(__file__).parent
        / "test_cases"
        / "code_quality"
        / "invalid"
        / "bad_code.py"
    )
    result = code_quality_validator.validate(bad_path)
    # Should be valid (only warnings for docstrings/type hints)
    assert result.is_valid, "Expected bad_code.py to be valid (warnings only)"
    warnings = result.warnings
    assert any(
        "missing type hints" in w.message for w in warnings
    ), "Expected type hints warning"
    assert any(
        "Missing docstring" in w.message for w in warnings
    ), "Expected docstring warning"


def test_warning_code(tmp_path: Path, code_quality_validator: object) -> None:
    warning_code = """
# TODO: Refactor this function

def long_line_function(a, b):
    x = a + b  # This is a very long comment that will exceed eighty characters but not the hard limit
    return x

def complex_function(a):
    if a > 0:
        if a > 1:
            if a > 2:
                if a > 3:
                    return a
    return 0

def long_func(a):
    x = 0
    for i in range(45):
        x += i
    return x
"""
    warning_file = tmp_path / "warning_code.py"
    warning_file.write_text(warning_code)
    result = code_quality_validator.validate(warning_file)
    # Should be invalid due to line exceeding hard max
    assert (
        not result.is_valid
    ), "Expected warning_code.py to be invalid due to line length error"
    warnings = result.warnings
    assert any("TODO" in w.message for w in warnings), "Expected TODO warning"
    assert any(
        "missing type hints" in w.message for w in warnings
    ), "Expected type hints warning"
    assert any(
        "Missing docstring" in w.message for w in warnings
    ), "Expected docstring warning"