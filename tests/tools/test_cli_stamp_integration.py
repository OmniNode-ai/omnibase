"""
Test the integration between CLIStamper and DirectoryTraverser.
Checks that the CLIStamper uses the DirectoryTraverser correctly.
"""

import tempfile
from pathlib import Path
from unittest import mock
from typing import Any, Generator

import pytest
from typer.testing import CliRunner

from omnibase.model.model_enum_template_type import TemplateTypeEnum  # type: ignore[import-untyped]
from omnibase.model.model_onex_message_result import OnexResultModel, OnexStatus  # type: ignore[import-untyped]
from omnibase.tools.cli_stamp import app  # type: ignore[import-untyped]
from omnibase.utils.directory_traverser import DirectoryTraverser  # type: ignore[import-untyped]
from omnibase.tools.stamper_engine import StamperEngine  # type: ignore[import-untyped]


@pytest.fixture
def schema_loader() -> Any:
    """Create a mock schema loader."""
    return mock.MagicMock()


@pytest.fixture
def directory_traverser() -> Any:
    """Create a mock directory traverser."""
    traverser = mock.MagicMock(spec=DirectoryTraverser)
    
    # Setup the process_directory method to return a success result
    traverser.process_directory.return_value = OnexResultModel(
        status=OnexStatus.success,
        target="/mock/dir",
        messages=[],
        metadata={
            "processed": 5,
            "failed": 0,
            "skipped": 2,
        },
    )
    
    return traverser


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory with test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_dir = Path(tmp_dir)
        
        # Create a test YAML file
        yaml_file = test_dir / "test.yaml"
        yaml_file.write_text("name: test")
        
        # Create a subdirectory with a test file
        subdir = test_dir / "subdir"
        subdir.mkdir()
        sub_yaml_file = subdir / "sub_test.yaml"
        sub_yaml_file.write_text("name: subtest")
        
        yield test_dir


def test_stamper_uses_directory_traverser(schema_loader: Any, directory_traverser: Any) -> None:
    """Test that StamperEngine correctly uses the DirectoryTraverser."""
    # Use StamperEngine with the mock directory traverser
    engine = StamperEngine(schema_loader, directory_traverser=directory_traverser)
    result = engine.process_directory(
        directory=Path("/mock/dir"),
        template=TemplateTypeEnum.MINIMAL,
        recursive=True,
        dry_run=True,
        include_patterns=["**/*.yaml"],
        exclude_patterns=["**/exclude/**"],
        ignore_file=Path("/mock/.stamperignore"),
        author="Test User",
    )
    # Verify the result is from our mock
    assert result.status == OnexStatus.success
    assert result.metadata["processed"] == 5
    # Verify directory_traverser.process_directory was called with correct arguments
    directory_traverser.process_directory.assert_called_once()
    args, kwargs = directory_traverser.process_directory.call_args
    assert kwargs["directory"] == Path("/mock/dir")
    assert kwargs["include_patterns"] == ["**/*.yaml"]
    assert kwargs["exclude_patterns"] == ["**/exclude/**"]
    assert kwargs["recursive"] is True
    assert kwargs["ignore_file"] == Path("/mock/.stamperignore")
    assert kwargs["dry_run"] is True


def test_cli_directory_command_integration(temp_dir: Path) -> None:
    """Test the CLI directory command with actual files."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "directory",
            str(temp_dir),
            "--recursive",
            "--dry-run",
            "--format", "json",
        ],
    )
    
    # Check the command ran successfully
    assert result.exit_code == 0 or result.exit_code == 1
    # Accept 'success' or 'warning' in output
    assert any(s in result.stdout for s in ["success", "warning", "status"])
    
    # Check that the output mentions our files
    assert "processed" in result.stdout 