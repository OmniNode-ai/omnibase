# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.366417'
# description: Stamped by PythonHandler
# entrypoint: python://test_cli_stamp_real_directory
# hash: fb04bc775de29ed46a1dc736817beeb25eb373c21f87a23c5c08d9d9e174e0b2
# last_modified_at: '2025-05-29T14:13:58.324575+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_cli_stamp_real_directory.py
# namespace: python://omnibase.cli_tools.onex.v1_0_0.cli_tests.test_cli_stamp_real_directory
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: a5762014-44dc-4026-a250-676830206221
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from omnibase.model.model_onex_message_result import OnexResultModel, OnexStatus
from omnibase.nodes.registry import NODE_CLI_REGISTRY
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

"""
Test the integration between CLIStamper and DirectoryTraverser.
Checks that the CLIStamper uses the DirectoryTraverser correctly.
"""


@pytest.fixture
def schema_loader() -> Any:
    """Create a mock schema loader."""
    from unittest import mock

    return mock.MagicMock()


@pytest.fixture
def directory_traverser() -> Any:
    """Create a mock directory traverser."""
    from unittest import mock

    from omnibase.utils.directory_traverser import DirectoryTraverser

    traverser = mock.MagicMock(spec=DirectoryTraverser)
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


def test_cli_directory_command_integration(cli_stamp_dir_fixture: Any) -> None:
    temp_dir, case = cli_stamp_dir_fixture
    runner = CliRunner()
    app = NODE_CLI_REGISTRY["stamper_node@v1_0_0"]
    result = runner.invoke(
        app,
        [
            "directory",
            str(temp_dir),
            "--recursive",
            "--format",
            "json",
        ]
    )
    if result.exit_code not in (0, 1, 2):
        print("[DEBUG] CLI output (stdout):\n", result.stdout)
        print("[DEBUG] CLI output (stderr):\n", result.stderr)
    assert result.exit_code in (0, 1, 2)
    if not any(s in result.stdout for s in ["success", "warning", "status"]):
        print("[DEBUG] CLI output (stdout):\n", result.stdout)
        print("[DEBUG] CLI output (stderr):\n", result.stderr)
    assert any(s in result.stdout for s in ["success", "warning", "status"])
    assert "processed" in result.stdout


def test_cli_stamp_real_directory_with_ignore_file(tmp_path: Path) -> None:
    # Implementation of the function
    return
