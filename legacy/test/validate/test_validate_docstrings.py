# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_docstrings"
# namespace: "omninode.tools.test_validate_docstrings"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:13+00:00"
# last_modified_at: "2025-05-05T13:00:13+00:00"
# entrypoint: "test_validate_docstrings.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTest']
# base_class: ['BaseTest']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from pathlib import Path

import pytest
from foundation.base.testing_base import BaseTest
from foundation.script.validation.validate_docstrings import DocstringValidator

# Helper functions to collect test case files


def get_valid_docstring_files():
    valid_dir = Path(__file__).parent / "test_cases" / "docstrings" / "valid"
    return list(valid_dir.glob("*.py"))


def get_invalid_docstring_files():
    invalid_dir = Path(__file__).parent / "test_cases" / "docstrings" / "invalid"
    return list(invalid_dir.glob("*.py"))


@pytest.fixture(scope="module")
def pydocstyle_config():
    # Search upward from this file for .pydocstyle
    current = Path(__file__).resolve()
    for parent in current.parents:
        config_path = parent / ".pydocstyle"
        if config_path.exists():
            return str(config_path)
    raise FileNotFoundError(".pydocstyle config not found in any parent directory.")


class TestDocstringValidator(BaseTest):
    @pytest.mark.parametrize(
        "file_path", [pytest.param(f, id=f.name) for f in get_valid_docstring_files()]
    )
    def test_validate_docstrings_good(self, file_path, pydocstyle_config):
        validator = DocstringValidator(config={"pydocstyle_config": pydocstyle_config})
        is_valid = validator.validate(file_path)
        assert (
            is_valid
        ), f"Expected validation to pass for {file_path}. Errors: {validator.errors}"
        assert (
            not validator.errors
        ), f"Expected no errors for {file_path}. Got: {validator.errors}"

    @pytest.mark.parametrize(
        "file_path", [pytest.param(f, id=f.name) for f in get_invalid_docstring_files()]
    )
    def test_validate_docstrings_bad(self, file_path, pydocstyle_config):
        validator = DocstringValidator(config={"pydocstyle_config": pydocstyle_config})
        is_valid = validator.validate(file_path)
        assert not is_valid.is_valid, f"Expected validation to fail for {file_path}."
        assert (
            validator.errors
        ), f"Expected errors for missing docstring in {file_path}."
        assert any(
            "D103" in str(e) or "Missing docstring" in str(e) for e in validator.errors
        ), f"Expected docstring error in output for {file_path}. Errors: {validator.errors}"


TEST_CASES_DIR = Path(__file__).parent / "test_cases" / "docstrings"


def test_valid_docstrings():
    valid_files = collect_test_case_files(TEST_CASES_DIR / "valid")
    validator = DocstringValidator()
    for file_path in valid_files:
        result = validator.validate(file_path)
        assert result.is_valid
        assert result.errors == []


def test_invalid_docstrings():
    invalid_files = collect_test_case_files(TEST_CASES_DIR / "invalid")
    validator = DocstringValidator()
    for file_path in invalid_files:
        result = validator.validate(file_path)
        assert not result.is_valid
        assert result.errors


def collect_test_case_files(directory):
    return list(directory.glob("*.py"))