# Canonical test case definitions for tools CLI main tests
# All field references must use canonical Enums where applicable.
# The Enum must be kept in sync with the CLI model if present.

import pytest
from typer.testing import CliRunner
from omnibase.tools.cli_main import app
from omnibase.core.errors import OmniBaseError

TOOLS_CLI_MAIN_CASES = {}

def register_tools_cli_main_case(name):
    def decorator(cls):
        TOOLS_CLI_MAIN_CASES[name] = cls
        return cls
    return decorator

runner = CliRunner()

@register_tools_cli_main_case("cli_version_success")
class CLIVersionSuccessCase:
    def run(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "ONEX CLI v0.1.0" in result.stdout

@register_tools_cli_main_case("cli_info_success")
class CLIInfoSuccessCase:
    def run(self):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "ONEX CLI System Information" in result.stdout
        assert "Python version" in result.stdout
        assert "Platform" in result.stdout
        assert "Loaded modules" in result.stdout

@register_tools_cli_main_case("cli_help_success")
class CLIHelpSuccessCase:
    def run(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ONEX CLI tool" in result.stdout
        assert "validate" in result.stdout
        assert "stamp" in result.stdout

@register_tools_cli_main_case("cli_validate_help_success")
class CLIValidateHelpSuccessCase:
    def run(self):
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate ONEX node metadata files" in result.stdout

@register_tools_cli_main_case("cli_stamp_help_success")
class CLIStampHelpSuccessCase:
    def run(self):
        result = runner.invoke(app, ["stamp", "--help"])
        assert result.exit_code == 0
        assert "Stamp ONEX node metadata files" in result.stdout

# Add more cases as needed for negative/error scenarios, DI, etc. 