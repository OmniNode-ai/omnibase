"""
Standards-Compliant Test File for ONEX/OmniBase CLI

This file follows the canonical test pattern as demonstrated in tests/utils/test_node_metadata_extractor.py. It demonstrates:
- Naming conventions: test_ prefix, lowercase, descriptive
- Context-agnostic, registry-driven, fixture-injected testing
- Use of both mock (unit) and integration (real) contexts via pytest fixture parametrization
- No global state; all dependencies are injected
- Registry-driven test case execution pattern
- Compliance with all standards in docs/standards.md and docs/testing.md

All new CLI tests should follow this pattern unless a justified exception is documented and reviewed.
"""

import subprocess
from pathlib import Path
from unittest import mock
from typing import Any

import pytest
from typer.testing import CliRunner

from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader  # type: ignore[import-untyped]
from omnibase.tools.cli_main import app  # type: ignore[import-untyped]
from omnibase.tools.cli_validate import CLIValidator  # type: ignore[import-untyped]
from tests.tools.tools_test_cli_main_cases import TOOLS_CLI_MAIN_CASES  # type: ignore[import-untyped]
from omnibase.tools.stamper_engine import StamperEngine  # type: ignore[import-untyped]

runner = CliRunner()


def test_cli_version() -> None:
    """Test the CLI version command returns the expected version string."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ONEX CLI v0.1.0" in result.stdout


def test_cli_info() -> None:
    """Test the CLI info command returns system information."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "ONEX CLI System Information" in result.stdout
    assert "Python version" in result.stdout
    assert "Platform" in result.stdout
    assert "Loaded modules" in result.stdout


def test_cli_help() -> None:
    """Test the CLI help command returns help text."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ONEX CLI tool" in result.stdout
    assert "validate" in result.stdout


def test_cli_validate_help() -> None:
    """Test the CLI validate help command returns help text for validate."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate ONEX node metadata files" in result.stdout


def test_cli_stamp_help() -> None:
    """Test the CLI stamp help command returns help text for stamp."""
    result = runner.invoke(app, ["stamp", "--help"])
    assert result.exit_code == 0
    assert "Stamp ONEX node metadata files" in result.stdout


def test_cli_entrypoint() -> None:
    """Test the CLI entrypoint is properly installed and callable via poetry run."""
    try:
        result = subprocess.run(
            ["poetry", "run", "onex", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        assert result.returncode == 0
        assert "ONEX CLI tool" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.fail(f"CLI entrypoint not properly installed or failed: {e}")


def test_validator_di() -> None:
    """Test that the CLIValidator correctly uses dependency injection."""
    # Create a mock schema loader
    mock_loader = mock.MagicMock(spec=ProtocolSchemaLoader)

    # Create the validator with the mock
    validator = CLIValidator(mock_loader)

    # Assert the validator uses the mock
    assert validator.schema_loader is mock_loader

    # Test a method that uses the schema loader
    test_path = Path("test.yaml")
    # Setup mock to avoid errors in methods that use it
    mock_loader.load_onex_yaml.return_value = {"schema_version": "1.0"}

    # Call a method that uses the schema loader
    validator._validate_file(test_path)

    # Assert the mock was called correctly
    mock_loader.load_onex_yaml.assert_called_once_with(test_path)


def test_stamper_di() -> None:
    """Test that the CLIStamper correctly uses dependency injection. (Not yet implemented)"""
    pass


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request: Any) -> str:
    return str(request.param)


@pytest.mark.parametrize(
    "context", ["mock", "integration"], ids=["mock", "integration"]
)
@pytest.mark.parametrize(
    "test_case",
    list(TOOLS_CLI_MAIN_CASES.values()),
    ids=list(TOOLS_CLI_MAIN_CASES.keys()),
)
def test_tools_cli_main_cases(test_case: Any, context: str) -> None:
    test_case().run(context)
