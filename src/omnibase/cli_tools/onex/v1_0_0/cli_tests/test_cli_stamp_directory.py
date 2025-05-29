# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.357368'
# description: Stamped by PythonHandler
# entrypoint: python://test_cli_stamp_directory
# hash: 668694c349e7544932c7c1badfaa1ed3efc8f706abb6091fb219f6d1813ee2d1
# last_modified_at: '2025-05-29T14:13:58.317234+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_cli_stamp_directory.py
# namespace: python://omnibase.cli_tools.onex.v1_0_0.cli_tests.test_cli_stamp_directory
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2a7aaabe-6a48-4ecd-b114-91a3f501abed
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test the CLI stamper directory command.
Tests the directory traversal functionality and ignore pattern handling.
"""

from typer.testing import CliRunner

from omnibase.nodes.registry import NODE_CLI_REGISTRY

# All previous tests used direct instantiation of StamperEngine, which is now forbidden.
# TODO: Add black-box CLI tests using runner and app from NODE_CLI_REGISTRY.


# Example placeholder test:
def test_cli_stamp_directory_help() -> None:
    runner = CliRunner()
    app = NODE_CLI_REGISTRY["stamper_node@v1_0_0"]
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "directory" in result.stdout
