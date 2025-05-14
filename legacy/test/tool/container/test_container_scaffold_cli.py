#!/usr/bin/env python3

# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_container_scaffold_cli"
# namespace: "omninode.test.tool.container"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00Z"
# last_modified_at: "2025-05-07T12:00:00Z"
# entrypoint: "test_container_scaffold_cli.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["TestProtocol"]
# base_class: ["TestProtocol"]
# mock_safe: true
# === /OmniNode:Test_Metadata ===

"""Tests for the container scaffolding CLI tool."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from foundation.script.tool.struct.struct_index import StructIndex
from foundation.util.util_tree_format_utils import UtilTreeFormatUtils
from foundation.util.util_file_output_writer import UtilFileOutputWriter
from foundation.util.util_hash_utils import UtilHashUtils
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.fixture.fixture_registry import FIXTURE_REGISTRY
from foundation.fixture.project.python.python_fixture_project import ProjectStructureFixture

# Canonical test case matrix: (name, mode, template, expected_status)
TEST_CASES = [
    ("test_container", "dry-run", None, True),
    ("test_container", "apply", None, True),
    ("test_container", "apply", "custom_template", True),
    ("test_container", "apply", "invalid_template", False),
    ("test_container", "invalid_mode", None, False),
]

@pytest.fixture
def temp_dir():
    """Fixture to provide a temporary directory for testing."""
    fixture = ProjectStructureFixture()
    try:
        yield fixture.get_fixture()
    finally:
        fixture.cleanup()

@pytest.fixture
def mock_struct_index():
    """Create a mock StructIndex."""
    mock = Mock(spec=StructIndex)
    mock.build_tree.return_value = Mock()
    mock.write_tree_files.return_value = None
    return mock

@pytest.fixture
def cli(mock_struct_index, temp_dir):
    """Create a CLI instance with mocked dependencies."""
    # Get the CLI class from the registry
    fixture = FIXTURE_REGISTRY.get_fixture("container_scaffold_cli")()
    if fixture is None:
        pytest.skip("ContainerScaffoldCLI not registered in fixture registry")
    
    # Create instance with mocked dependencies
    cli = fixture.get_fixture(
        logger=Mock(),
        registry=Mock(),
        di_container=Mock(),
        config=Mock(),
        process_runner=Mock(),
        vcs_client=Mock(),
        output_formatter=Mock(),
        file_loader=Mock(),
        json_loader=Mock(),
    )
    cli._setup = Mock()
    cli._setup.temp_path = temp_dir
    return cli

class TestContainerScaffoldCLI:
    """Test suite for the container scaffolding CLI tool."""

    def test_dry_run_mode(self, cli, temp_dir):
        """Test dry run mode shows what would be created."""
        args = Mock(
            container_name="test_container",
            template="base_container.yaml",
            override=None,
            output_dir=str(temp_dir),
            apply=False,
            verbose=False,
        )
        
        result = cli._run_existing(args)
        
        assert result["status"] == "success"
        assert "Would create container" in result["messages"][0]["summary"]
        assert not (temp_dir / "test_container").exists()

    def test_apply_mode(self, cli, mock_struct_index, temp_dir):
        """Test apply mode creates container structure."""
        args = Mock(
            container_name="test_container",
            template="base_container.yaml",
            override=None,
            output_dir=str(temp_dir),
            apply=True,
            verbose=False,
        )
        
        with patch('foundation.script.tool.container.container_scaffold_cli.StructIndex', return_value=mock_struct_index):
            result = cli._run_existing(args)
        
        assert result["status"] == "success"
        assert "Created container" in result["messages"][0]["summary"]
        assert (temp_dir / "test_container").exists()
        assert (temp_dir / "test_container" / "src" / "test_container").exists()
        assert (temp_dir / "test_container" / "test").exists()
        mock_struct_index.build_tree.assert_called_once()
        mock_struct_index.write_tree_files.assert_called_once()

    def test_custom_template(self, cli, temp_dir):
        """Test using a custom template."""
        template_path = temp_dir / "custom_template.yaml"
        template_path.write_text("""
# === OmniNode:CanonicalStructure ===
metadata_version: "0.1"
schema_version: "1.0.0"
name: "custom_container_structure"
namespace: "omninode.structure.custom_container"
type: "structure"
version: "0.1.0"
author: "OmniNode Team"
owner: "jonah@omninode.ai"
copyright: "Copyright (c) 2025 OmniNode.ai"
created_at: "2025-05-07T12:00:00Z"
last_modified_at: "2025-05-07T12:00:00Z"
entrypoint: "structure/custom_template.yaml"
protocols_supported: ["O.N.E. v0.1"]
protocol_class: ["BaseTemplate"]
base_class: ["BaseTemplate"]
mock_safe: true

structure:
  root: container_name
  rules:
    allow_flexible:
      - __pycache__
      - .mypy_cache
    deny_unlisted: true
    allow_symlinks: false
    allow_hidden_files: true

  canonical_paths:
    - path: src
      required: true
      description: "Source code directory"
      allowed_files:
        - pattern: "*.py"
          description: "Python source files"
      allowed_dirs:
        - pattern: "test_*"
          description: "Test directories"
# === /OmniNode:CanonicalStructure ===
""")
        
        args = Mock(
            container_name="test_container",
            template=str(template_path),
            override=None,
            output_dir=str(temp_dir),
            apply=True,
            verbose=False,
        )
        
        result = cli._run_existing(args)
        assert result["status"] == "success"

    def test_container_override(self, cli, temp_dir):
        """Test using a container-specific override."""
        override_path = temp_dir / "test_container.yaml"
        override_path.write_text("""
# === OmniNode:CanonicalStructure ===
metadata_version: "0.1"
schema_version: "1.0.0"
name: "test_container_structure"
namespace: "omninode.structure.test_container"
type: "structure"
version: "0.1.0"
author: "OmniNode Team"
owner: "jonah@omninode.ai"
copyright: "Copyright (c) 2025 OmniNode.ai"
created_at: "2025-05-07T12:00:00Z"
last_modified_at: "2025-05-07T12:00:00Z"
entrypoint: "structure/test_container.yaml"
protocols_supported: ["O.N.E. v0.1"]
protocol_class: ["BaseTemplate"]
base_class: ["BaseTemplate"]
mock_safe: true
extends: "base_container_structure"

structure:
  root: test_container
  overrides:
    canonical_paths:
      - path: src/test_container/script
        required: true
        description: "Scripts directory"
        allowed_files:
          - pattern: "*.py"
            description: "Python source files"
        allowed_dirs:
          - pattern: "tool"
            description: "Tool implementations"
          - pattern: "validate"
            description: "Validator implementations"
    
    validation_rules:
      - name: "script_naming"
        description: "Script files must be in script directory"
        pattern: "*.py"
        required_path: "src/test_container/script"
# === /OmniNode:CanonicalStructure ===
""")
        
        args = Mock(
            container_name="test_container",
            template="base_container.yaml",
            override=str(override_path),
            output_dir=str(temp_dir),
            apply=True,
            verbose=False,
        )
        
        result = cli._run_existing(args)
        assert result["status"] == "success"

    def test_error_handling(self, cli, temp_dir):
        """Test error handling for invalid inputs."""
        # Test with invalid container name
        args = Mock(
            container_name="invalid/name",
            template="base_container.yaml",
            override=None,
            output_dir=str(temp_dir),
            apply=True,
            verbose=False,
        )
        
        with patch.object(Path, 'mkdir', side_effect=OSError("Invalid container name")):
            result = cli._run_existing(args)
            assert result["status"] == "error"
        
        # Test with non-existent template
        args = Mock(
            container_name="test_container",
            template="nonexistent.yaml",
            override=None,
            output_dir=str(temp_dir),
            apply=True,
            verbose=False,
        )
        
        with patch('foundation.script.tool.container.container_scaffold_cli.StructIndex', side_effect=FileNotFoundError("Template not found")):
            result = cli._run_existing(args)
            assert result["status"] == "error"

    def test_verbose_output(self, cli, mock_struct_index, temp_dir):
        """Test verbose mode provides detailed output."""
        args = Mock(
            container_name="test_container",
            template="base_container.yaml",
            override=None,
            output_dir=str(temp_dir),
            apply=True,
            verbose=True,
        )

        with patch('foundation.script.tool.container.container_scaffold_cli.StructIndex', return_value=mock_struct_index):
            result = cli._run_existing(args)
            assert result["status"] == "success"
            
            # Get the actual call args
            actual_call = mock_struct_index.build_tree.call_args
            assert actual_call is not None, "build_tree was not called"
            
            # Compare path components instead of raw paths to handle /private prefix
            actual_path = actual_call[0][0]
            expected_path = temp_dir / "test_container"
            assert actual_path.name == expected_path.name
            assert actual_path.parent.name == expected_path.parent.name
            
            # Compare the kwargs
            assert actual_call[1] == {
                "max_depth": -1,
                "follow_symlinks": False,
                "with_metadata": True,
                "verbose": True
            }

@pytest.mark.parametrize("name, mode, template, expected_status", TEST_CASES)
def test_container_scaffold_cli(name, mode, template, expected_status, temp_dir, mock_struct_index):
    """Test the container scaffold CLI with various configurations."""
    # ... existing code ... 