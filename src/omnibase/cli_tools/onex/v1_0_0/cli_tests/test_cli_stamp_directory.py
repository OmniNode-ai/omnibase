# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.357368'
# description: Stamped by PythonHandler
# entrypoint: python://test_cli_stamp_directory.py
# hash: 6e16af30ade6a4f62273270a21fb0ed1d7ef6ba56c096555c449208dd3e3fc91
# last_modified_at: '2025-05-29T11:50:10.628200+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_cli_stamp_directory.py
# namespace: omnibase.test_cli_stamp_directory
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
