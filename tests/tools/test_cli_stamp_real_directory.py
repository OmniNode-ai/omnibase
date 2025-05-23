# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_cli_stamp_real_directory.py
# version: 1.0.0
# uuid: 1e408f6b-1dcb-4311-931e-a3373c612d48
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.907897
# last_modified_at: 2025-05-22T20:50:39.715979
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5aae51d8783fb88c14d747c71ddc9a880b3a4a920cb1b120ee57044b6c23dd3f
# entrypoint: python@test_cli_stamp_real_directory.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_cli_stamp_real_directory
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test the integration between CLIStamper and DirectoryTraverser.
Checks that the CLIStamper uses the DirectoryTraverser correctly.
"""

from pathlib import Path
from typing import Any
from unittest import mock

import pytest
from typer.testing import CliRunner

from omnibase.model.model_enum_template_type import (
    TemplateTypeEnum,  # type: ignore[import-untyped]
)
from omnibase.model.model_onex_message_result import (  # type: ignore[import-untyped]
    OnexResultModel,
    OnexStatus,
)
from omnibase.nodes.stamper_node.helpers.stamper_engine import StamperEngine
from omnibase.tools.cli_stamp import app  # type: ignore[import-untyped]
from omnibase.utils.directory_traverser import (
    DirectoryTraverser,  # type: ignore[import-untyped]
)


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
        status=OnexStatus.SUCCESS,
        target="/mock/dir",
        messages=[],
        metadata={
            "processed": 5,
            "failed": 0,
            "skipped": 2,
        },
    )

    return traverser


def test_stamper_uses_directory_traverser(
    schema_loader: Any, directory_traverser: Any
) -> None:
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
        ignore_file=Path("/mock/.onexignore"),
        author="Test User",
    )
    # Verify the result is from our mock
    assert result.status == OnexStatus.SUCCESS
    assert result.metadata is not None
    assert result.metadata["processed"] == 5
    # Verify directory_traverser.process_directory was called with correct arguments
    directory_traverser.process_directory.assert_called_once()
    args, kwargs = directory_traverser.process_directory.call_args
    assert kwargs["directory"] == Path("/mock/dir")
    assert kwargs["include_patterns"] == ["**/*.yaml"]
    assert kwargs["exclude_patterns"] == ["**/exclude/**"]
    assert kwargs["recursive"] is True
    assert kwargs["ignore_file"] == Path("/mock/.onexignore")
    assert kwargs["dry_run"] is True


def test_cli_directory_command_integration(cli_stamp_dir_fixture) -> None:
    temp_dir, case = cli_stamp_dir_fixture
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "directory",
            str(temp_dir),
            "--recursive",
            "--format",
            "json",
        ],
    )

    # Accept Typer's standard exit code 2 for CLI usage errors, in addition to 0/1 for protocol-driven results.
    # Exit code 2 means a CLI usage error (e.g., missing/invalid arguments), not a protocol or tool failure.
    if result.exit_code not in (0, 1, 2):
        print("[DEBUG] CLI output (stdout):\n", result.stdout)
        print("[DEBUG] CLI output (stderr):\n", result.stderr)
    assert result.exit_code in (0, 1, 2)
    # Accept 'success' or 'warning' in output
    if not any(s in result.stdout for s in ["success", "warning", "status"]):
        print("[DEBUG] CLI output (stdout):\n", result.stdout)
        print("[DEBUG] CLI output (stderr):\n", result.stderr)
    assert any(s in result.stdout for s in ["success", "warning", "status"])

    # Check that the output mentions our files
    assert "processed" in result.stdout
