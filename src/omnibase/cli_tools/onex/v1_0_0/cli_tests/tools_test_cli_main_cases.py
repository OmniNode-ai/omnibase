# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:07.720076'
# description: Stamped by PythonHandler
# entrypoint: python://tools_test_cli_main_cases
# hash: 010520f7a1bf0b5ea35548b54d314484a6a9d1a7d6561bd0c70d2dfc2c98382e
# last_modified_at: '2025-05-29T14:13:58.360931+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: tools_test_cli_main_cases.py
# namespace: python://omnibase.cli_tools.onex.v1_0_0.cli_tests.tools_test_cli_main_cases
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 11364edf-ab47-4604-b572-4dc5f2512d41
# version: 1.0.0
# === /OmniNode:Metadata ===


# Canonical test case definitions for tools CLI main tests
# All field references must use canonical Enums where applicable.
# The Enum must be kept in sync with the CLI model if present.

from typing import Any, Callable

from typer.testing import CliRunner

from omnibase.cli_tools.onex.v1_0_0.cli_main import app  # type: ignore[import-untyped]

TOOLS_CLI_MAIN_CASES: dict[str, type] = {}


def register_tools_cli_main_case(name: str) -> Callable[[type], type]:
    """Decorator to register a test case class in the CLI main test case registry."""

    def decorator(cls: type) -> type:
        TOOLS_CLI_MAIN_CASES[name] = cls
        return cls

    return decorator


runner = CliRunner()


@register_tools_cli_main_case("cli_version_success")
class CLIVersionSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "ONEX CLI Node v1.0.0" in result.stdout


@register_tools_cli_main_case("cli_info_success")
class CLIInfoSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "ONEX CLI Node System Information" in result.stdout
        assert "python_version" in result.stdout
        assert "platform" in result.stdout


@register_tools_cli_main_case("cli_help_success")
class CLIHelpSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ONEX CLI tool" in result.stdout
        # Note: validate command removed - use 'onex run parity_validator_node' instead
        # 'stamp' is no longer a direct subcommand


@register_tools_cli_main_case("cli_validate_help_success")
class CLIValidateHelpSuccessCase:
    def run(self, context: Any) -> None:
        # Note: validate command removed - use 'onex run parity_validator_node' instead
        result = runner.invoke(app, ["run", "parity_validator_node", "--introspect"])
        assert result.exit_code == 0
        # Just verify the command runs - introspection shows the node is available


# Add more cases as needed for negative/error scenarios, DI, etc.
