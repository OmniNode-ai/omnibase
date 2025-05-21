# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: tools_test_cli_main_cases.py
# version: 1.0.0
# uuid: b5f0d2ab-28d3-416e-a809-e86744bf296f
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.172432
# last_modified_at: 2025-05-21T16:42:46.088267
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a607aee98d6ecf3ef38338b24d1e3c420716c0c12ff35a15fb1f9648a9550a38
# entrypoint: {'type': 'python', 'target': 'tools_test_cli_main_cases.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.tools_test_cli_main_cases
# meta_type: tool
# === /OmniNode:Metadata ===

# Canonical test case definitions for tools CLI main tests
# All field references must use canonical Enums where applicable.
# The Enum must be kept in sync with the CLI model if present.

from typing import Any, Callable

from typer.testing import CliRunner

from omnibase.tools.cli_main import app  # type: ignore[import-untyped]

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
        assert "ONEX CLI v0.1.0" in result.stdout


@register_tools_cli_main_case("cli_info_success")
class CLIInfoSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "ONEX CLI System Information" in result.stdout
        assert "Python version" in result.stdout
        assert "Platform" in result.stdout
        assert "Loaded modules" in result.stdout


@register_tools_cli_main_case("cli_help_success")
class CLIHelpSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ONEX CLI tool" in result.stdout
        assert "validate" in result.stdout
        assert "stamp" in result.stdout


@register_tools_cli_main_case("cli_validate_help_success")
class CLIValidateHelpSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate ONEX node metadata files" in result.stdout


@register_tools_cli_main_case("cli_stamp_help_success")
class CLIStampHelpSuccessCase:
    def run(self, context: Any) -> None:
        result = runner.invoke(app, ["stamp", "--help"])
        assert result.exit_code == 0
        assert "Stamp ONEX node metadata files" in result.stdout


# Add more cases as needed for negative/error scenarios, DI, etc.
