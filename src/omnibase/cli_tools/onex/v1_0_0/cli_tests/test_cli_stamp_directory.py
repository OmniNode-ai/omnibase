# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_cli_stamp_directory.py
# version: 1.0.0
# uuid: 03f69d3f-ace1-4232-a39e-263160318c64
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.907543
# last_modified_at: 2025-05-22T20:50:39.718286
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5855ab772111a3ae05da06e342c06437897efa808ca082937611d1deea6c1df2
# entrypoint: python@test_cli_stamp_directory.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_cli_stamp_directory
# meta_type: tool
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
