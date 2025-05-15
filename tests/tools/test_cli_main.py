"""
Tests for the main CLI entrypoint.
Smoke test to verify CLI basics are working.
"""
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner

from omnibase.tools.cli_main import app
from omnibase.tools.cli_validate import CLIValidator
from omnibase.tools.cli_stamp import CLIStamper
from omnibase.schema.loader import SchemaLoader
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader

runner = CliRunner()

def test_cli_version():
    """Test the CLI version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ONEX CLI v0.1.0" in result.stdout

def test_cli_info():
    """Test the CLI info command."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "ONEX CLI System Information" in result.stdout
    assert "Python version" in result.stdout
    assert "Platform" in result.stdout
    assert "Loaded modules" in result.stdout

def test_cli_help():
    """Test the CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ONEX CLI tool" in result.stdout
    assert "validate" in result.stdout
    assert "stamp" in result.stdout

def test_cli_validate_help():
    """Test the CLI validate help command."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate ONEX node metadata files" in result.stdout

def test_cli_stamp_help():
    """Test the CLI stamp help command."""
    result = runner.invoke(app, ["stamp", "--help"])
    assert result.exit_code == 0
    assert "Stamp ONEX node metadata files" in result.stdout

@pytest.mark.skip(reason="Integration test requires installed package")
def test_cli_entrypoint():
    """Test the CLI entrypoint is properly installed."""
    # This test requires the package to be installed with pip install -e .
    try:
        result = subprocess.run(
            ["onex", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        assert result.returncode == 0
        assert "ONEX CLI tool" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.fail("CLI entrypoint not properly installed.")

def test_validator_di():
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

def test_stamper_di():
    """Test that the CLIStamper correctly uses dependency injection."""
    # Create a mock schema loader
    mock_loader = mock.MagicMock(spec=ProtocolSchemaLoader)
    
    # Create the stamper with the mock
    stamper = CLIStamper(mock_loader)
    
    # Assert the stamper uses the mock
    assert stamper.schema_loader is mock_loader 