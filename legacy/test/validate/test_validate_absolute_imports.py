# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_absolute_imports"
# namespace: "omninode.tools.test_validate_absolute_imports"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_absolute_imports.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for AbsoluteImportsValidator using registry-based fixture and helpers.
Follows canary standards: DI, registry, type hints, docstrings, and metadata.
Supports both unit and integration modes via parameterized fixture.
"""

from pathlib import Path

import pytest
from containers.foundation.test.conftest import PathFixtureConfig
from foundation.protocol.fixture_project_structure import IProjectStructureFixture
from foundation.protocol.testing.idirectory_fixture import IDirectoryFixture
from foundation.protocol.testing.itest_helper import ITestHelper
from foundation.script.validation.validate_absolute_imports import (
    AbsoluteImportsValidator,
)
from foundation.script.validation.validator_registry import get_fixture_by_interface


def write_file(path: Path, content: str) -> None:
    """Write the given content to the specified file path."""
    path.write_text(content)


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


good_py_content = (
    "from foundation.base.base_validator_abc import ProtocolValidate\nimport os\n"
)
bad_py_content = "from .utils import something\n"


@pytest.mark.parametrize(
    "path_fixture",
    [PathFixtureConfig(mode="file", filename="good.py", file_content=good_py_content)],
    indirect=True,
)
def test_absolute_imports_validator_single_file_pass(
    path_fixture, test_helper: ITestHelper
) -> None:
    """Test that a file with only absolute imports passes validation (unit/integration)."""
    validator = AbsoluteImportsValidator()
    result = validator.validate(path_fixture)
    assert result.is_valid
    assert not result.errors


@pytest.mark.parametrize(
    "path_fixture",
    [PathFixtureConfig(mode="file", filename="bad.py", file_content=bad_py_content)],
    indirect=True,
)
def test_absolute_imports_validator_single_file_fail(
    path_fixture, test_helper: ITestHelper
) -> None:
    """Test that a file with a relative import fails validation (unit/integration)."""
    validator = AbsoluteImportsValidator()
    result = validator.validate(path_fixture)
    assert not result.is_valid
    for err in result.errors:
        test_helper.assert_issue_fields(err)
    test_helper.assert_has_error(
        result.errors, "Relative import detected", str(path_fixture)
    )


@pytest.mark.parametrize(
    "path_fixture",
    [
        PathFixtureConfig(
            mode="directory",
            structure={"good.py": "import sys\n", "bad.py": "from .foo import bar\n"},
        )
    ],
    indirect=True,
)
def test_absolute_imports_validator_directory(
    path_fixture, test_helper: ITestHelper
) -> None:
    """Test that a directory with both good and bad files is validated correctly (unit/integration)."""
    good_file = path_fixture / "good.py"
    bad_file = path_fixture / "bad.py"
    validator = AbsoluteImportsValidator()
    result = validator.validate(path_fixture)
    assert not result.is_valid
    for err in result.errors:
        test_helper.assert_issue_fields(err)
    test_helper.assert_has_error(
        result.errors, "Relative import detected", str(bad_file)
    )
    for err in result.errors:
        assert str(good_file) not in err.message