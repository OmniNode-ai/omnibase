# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_api_validator"
# namespace: "omninode.tools.test_validate_api_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_api_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for APIValidator using registry-based fixture and helpers.
Follows canary standards: DI, registry, type hints, docstrings, and metadata.
Supports both unit and integration modes via parameterized fixture.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from containers.foundation.test.conftest import (
    DirectoryDescriptor,
    FileDescriptor,
    PathFixtureConfig,
    PathMode,
)
from foundation.base.model_base import APISpecValidationIssue
from foundation.protocol.fixture_project_structure import IProjectStructureFixture
from foundation.protocol.testing.idirectory_fixture import IDirectoryFixture
from foundation.protocol.testing.itest_helper import ITestHelper
from foundation.script.validation.validate_api import APIValidator, APIValidatorConfig
from foundation.script.validation.validator_registry import get_fixture_by_interface

TEST_CASES_DIR = Path(__file__).parent / "test_cases" / "api"
valid_cases = list((TEST_CASES_DIR / "valid").glob("*.yaml"))
invalid_cases = list((TEST_CASES_DIR / "invalid").glob("*.yaml"))


@pytest.fixture(params=["unit", "integration"])
def directory_fixture(request, tmp_path: Path) -> Path:
    """Parameterized fixture: provides either a temp dir (unit) or project structure (integration)."""
    mode = request.param
    if mode == "unit":
        fixture_cls = get_fixture_by_interface(IDirectoryFixture)
        return (
            fixture_cls.get_fixture()
            if hasattr(fixture_cls, "get_fixture")
            else tmp_path
        )
    elif mode == "integration":
        fixture_cls = get_fixture_by_interface(IProjectStructureFixture)
        # Provide a minimal project structure for integration
        structure = {"files": {"README.md": "# Project\n"}, "dirs": ["src"]}
        return (
            fixture_cls(structure).get_fixture()
            if hasattr(fixture_cls, "get_fixture")
            else tmp_path
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")


@pytest.fixture
def test_helper() -> ITestHelper:
    """Registry-based test helper (DI-compliant)."""
    helper_cls = get_fixture_by_interface(ITestHelper)
    return helper_cls()


@pytest.mark.parametrize(
    "spec_path,path_fixture",
    [
        # Standard valid cases
        (
            spec,
            PathFixtureConfig(
                mode=PathMode.FILE, file=FileDescriptor(name="openapi.yaml", content="")
            ),
        )
        for spec in valid_cases
    ]
    + [
        (
            spec,
            PathFixtureConfig(
                mode=PathMode.DIRECTORY,
                files=[FileDescriptor(name="openapi.yaml", content="")],
            ),
        )
        for spec in valid_cases
    ]
    + [
        # Edge case: empty file
        (
            None,
            PathFixtureConfig(
                mode=PathMode.FILE, file=FileDescriptor(name="openapi.yaml", content="")
            ),
        ),
        # Edge case: empty directory
        (None, PathFixtureConfig(mode=PathMode.DIRECTORY)),
        # Edge case: directory with non-Python file
        (
            None,
            PathFixtureConfig(
                mode=PathMode.DIRECTORY,
                files=[FileDescriptor(name="README.md", content="# Readme")],
            ),
        ),
        # Edge case: directory with nested empty subdirectory
        (
            None,
            PathFixtureConfig(
                mode=PathMode.DIRECTORY,
                subdirs=[DirectoryDescriptor(name="empty_subdir")],
            ),
        ),
    ],
    indirect=["path_fixture"],
)
def test_valid_api_cases(
    path_fixture, test_helper: ITestHelper, spec_path: Path
) -> None:
    """Test that valid API specs pass validation (unit/integration) and edge cases."""
    if spec_path is not None:
        if path_fixture.is_file():
            path_fixture.write_text(spec_path.read_text())
            target = path_fixture.parent
        else:
            (path_fixture / "openapi.yaml").write_text(spec_path.read_text())
            target = path_fixture
    else:
        target = path_fixture
    validator = APIValidator()
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response
        result = validator.validate(target)
    # For edge cases, just check that the validator does not crash
    if spec_path is not None:
        assert (
            result.is_valid
        ), f"Expected valid API spec, got errors: {result.errors} and warnings: {result.warnings}"
        assert not result.errors
        assert not result.warnings


@pytest.mark.parametrize(
    "spec_path,path_fixture",
    [
        (
            spec,
            PathFixtureConfig(
                mode=PathMode.FILE, file=FileDescriptor(name="openapi.yaml", content="")
            ),
        )
        for spec in invalid_cases
    ]
    + [
        (
            spec,
            PathFixtureConfig(
                mode=PathMode.DIRECTORY,
                files=[FileDescriptor(name="openapi.yaml", content="")],
            ),
        )
        for spec in invalid_cases
    ],
    indirect=["path_fixture"],
)
def test_invalid_api_cases(
    path_fixture, test_helper: ITestHelper, spec_path: Path
) -> None:
    """Test that invalid API specs fail validation (unit/integration)."""
    if path_fixture.is_file():
        path_fixture.write_text(spec_path.read_text())
        target = path_fixture.parent
    else:
        (path_fixture / "openapi.yaml").write_text(spec_path.read_text())
        target = path_fixture
    config = None
    if "missing_required_method" in spec_path.name:
        config = APIValidatorConfig(required_methods=["POST"])
        validator = APIValidator(config.model_dump())
    else:
        validator = APIValidator()
    result = validator.validate(target)
    assert (
        not result.is_valid
    ), f"Expected invalid API spec, got valid. File: {spec_path}"
    assert (
        result.errors or result.warnings
    ), f"Expected errors or warnings for invalid API spec. File: {spec_path}"
    for err in result.errors:
        assert isinstance(
            err, APISpecValidationIssue
        ), f"Error is not APISpecValidationIssue: {err}"
    for warn in result.warnings:
        assert isinstance(
            warn, APISpecValidationIssue
        ), f"Warning is not APISpecValidationIssue: {warn}"