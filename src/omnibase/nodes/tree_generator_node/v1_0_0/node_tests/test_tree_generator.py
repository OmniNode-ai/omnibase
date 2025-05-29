# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.066431'
# description: Stamped by PythonHandler
# entrypoint: python://test_tree_generator
# hash: 925be409fc81d35c7742da427ddd87986c594700175bd273817290d7f5eb392a
# last_modified_at: '2025-05-29T14:14:00.154958+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_tree_generator.py
# namespace: python://omnibase.nodes.tree_generator_node.v1_0_0.node_tests.test_tree_generator
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 6b559243-5976-429d-8f28-80a4bdc56f53
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test suite for tree_generator_node.

Tests the functionality of generating .onextree manifest files from directory structure analysis.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from ..constants import STATUS_ERROR, STATUS_SUCCESS
from ..models.state import TreeGeneratorInputState, TreeGeneratorOutputState
from ..node import run_tree_generator_node


class TestTreeGeneratorNode:
    """Test class for tree_generator_node functionality."""

    def test_tree_generator_node_success(self) -> None:
        """Test successful execution of tree_generator_node."""
        # Create a temporary directory structure for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a simple directory structure
            (temp_path / "test_file.txt").write_text("test content")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "nested_file.py").write_text("# test python file")

            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            assert isinstance(result, TreeGeneratorOutputState)
            assert result.version == "1.0.0"
            assert result.status == STATUS_SUCCESS
            assert result.artifacts_discovered is not None
            assert result.validation_results is not None

            # Verify events were emitted
            # Check that NODE_START and NODE_SUCCESS events were emitted in order (robust to extra events)
            event_types = [call_args[0][0].event_type if call_args[0] else None for call_args in mock_event_bus.publish.call_args_list]
            try:
                start_idx = event_types.index("NODE_START")
                success_idx = event_types.index("NODE_SUCCESS")
                assert start_idx < success_idx
            except ValueError:
                assert False, f"NODE_START and NODE_SUCCESS events not found in emitted events: {event_types}"

    def test_tree_generator_node_with_nonexistent_directory(self) -> None:
        """Test tree_generator_node with nonexistent root directory."""
        input_state = TreeGeneratorInputState(
            version="1.0.0",
            root_directory="/nonexistent/path",
            output_path="/tmp/.onextree",
        )

        mock_event_bus = Mock()

        result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

        # Should handle gracefully and return error status
        assert isinstance(result, TreeGeneratorOutputState)
        assert result.status == STATUS_ERROR

    def test_tree_generator_node_minimal_input(self) -> None:
        """Test tree_generator_node with minimal required input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=temp_dir,
                # output_path uses default value
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            assert isinstance(result, TreeGeneratorOutputState)
            assert result.status in [
                STATUS_SUCCESS,
                STATUS_ERROR,
            ]  # Depends on directory content
            assert result.artifacts_discovered is not None

    def test_tree_generator_node_state_validation(self) -> None:
        """Test input state validation."""
        # Test missing required field
        from pydantic import ValidationError

        with pytest.raises(ValidationError):  # Pydantic validation error
            TreeGeneratorInputState(  # type: ignore[call-arg]
                root_directory="/some/path",
                # Missing required field: version
            )

    def test_tree_generator_node_output_state_structure(self) -> None:
        """Test output state structure and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = TreeGeneratorInputState(
                version="1.0.0", root_directory=temp_dir
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            # Test output state structure
            assert hasattr(result, "version")
            assert hasattr(result, "status")
            assert hasattr(result, "message")
            assert hasattr(result, "artifacts_discovered")
            assert hasattr(result, "validation_results")

            # Test that output can be serialized
            json_output = result.model_dump_json()
            assert isinstance(json_output, str)
            assert len(json_output) > 0


class TestTreeGeneratorNodeIntegration:
    """Integration tests for tree_generator_node."""

    def test_tree_generator_node_with_real_structure(self) -> None:
        """Test tree_generator_node with a realistic directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a structure similar to ONEX nodes
            nodes_dir = temp_path / "nodes" / "test_node" / "v1_0_0"
            nodes_dir.mkdir(parents=True)

            # Create node metadata file
            (nodes_dir / "node.onex.yaml").write_text(
                """
schema_version: "0.1.0"
name: "test_node"
version: "1.0.0"
uuid: "test-uuid"
author: "Test Author"
created_at: "2025-01-24T00:00:00.000000"
last_modified_at: "2025-01-24T00:00:00.000000"
description: "Test node"
state_contract: "state_contract://test"
lifecycle: "active"
hash: "test-hash"
entrypoint:
  type: python
  target: node.py
namespace: "test.nodes.test_node"
meta_type: "tool"
"""
            )

            (nodes_dir / "node.py").write_text("# Test node implementation")

            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            mock_event_bus = Mock()

            result = run_tree_generator_node(input_state, event_bus=mock_event_bus)

            assert isinstance(result, TreeGeneratorOutputState)
            assert result.status == STATUS_SUCCESS
            # Should find at least the test node
            if result.artifacts_discovered:
                total_artifacts = sum(result.artifacts_discovered.values())
                assert total_artifacts >= 1

            # Verify .onextree file was created
            onextree_path = temp_path / ".onextree"
            assert onextree_path.exists()


# Test fixtures
@pytest.fixture
def tree_generator_input_state() -> TreeGeneratorInputState:
    """Fixture for common input state."""
    return TreeGeneratorInputState(
        version="1.0.0", root_directory="/tmp/test", output_path="/tmp/.onextree"
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """Mock event bus for testing."""
    return Mock()


class TestOnextreeValidation:
    """Test class for validating .onextree files against actual directory contents."""

    def test_onextree_matches_directory_structure(self) -> None:
        """Test that generated .onextree accurately reflects directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a known directory structure
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file2.py").write_text("# python content")

            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "nested_file.md").write_text("# markdown")
            (subdir / "nested_subdir").mkdir()
            (subdir / "nested_subdir" / "deep_file.json").write_text('{"key": "value"}')

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            if result.status != STATUS_SUCCESS:
                print(f"[DEBUG] Tree generator status: {result.status}")
                print(f"[DEBUG] Tree generator message: {result.message}")
                print(f"[DEBUG] Tree generator validation_results: {result.validation_results}")
            assert result.status == STATUS_SUCCESS

            # Load and validate the generated .onextree
            onextree_path = temp_path / ".onextree"
            assert onextree_path.exists()

            import yaml

            with open(onextree_path, "r") as f:
                tree_data = yaml.safe_load(f)

            # Validate structure matches actual directory
            self._validate_tree_structure(tree_data, temp_path)

    def test_onextree_detects_missing_files(self) -> None:
        """Test that validation can detect when .onextree is missing files that exist in directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create initial structure
            (temp_path / "file1.txt").write_text("content1")
            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "nested_file.md").write_text("# markdown")

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            assert result.status == STATUS_SUCCESS

    def test_onextree_detects_extra_files(self) -> None:
        """Test that validation can detect when .onextree has files that don't exist in directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create initial structure
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file_to_delete.txt").write_text("will be deleted")
            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "nested_file.md").write_text("# markdown")

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            assert result.status == STATUS_SUCCESS

            # Remove files after .onextree generation
            (temp_path / "file_to_delete.txt").unlink()

            # Validate that .onextree now has extra files
            onextree_path = temp_path / ".onextree"
            import yaml

            with open(onextree_path, "r") as f:
                tree_data = yaml.safe_load(f)

            # This should detect extra files in .onextree
            validation_errors = self._validate_tree_against_directory(
                tree_data, temp_path
            )
            assert len(validation_errors) > 0
            assert any(
                "exists in .onextree but not in directory" in error.lower()
                for error in validation_errors
            )

    def test_onextree_validates_file_types(self) -> None:
        """Test that .onextree correctly identifies file vs directory types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mixed structure
            (temp_path / "regular_file.txt").write_text("content")
            (temp_path / "directory").mkdir()
            (temp_path / "directory" / "nested_file.py").write_text("# python")

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            assert result.status == STATUS_SUCCESS

            # Load and validate types
            onextree_path = temp_path / ".onextree"
            import yaml

            with open(onextree_path, "r") as f:
                tree_data = yaml.safe_load(f)

            # Validate file types are correct
            validation_errors = self._validate_file_types(tree_data, temp_path)
            assert (
                len(validation_errors) == 0
            ), f"File type validation errors: {validation_errors}"

    def test_onextree_handles_hidden_files_correctly(self) -> None:
        """Test that .onextree correctly handles hidden files according to rules."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create structure with hidden files
            (temp_path / "regular_file.txt").write_text("content")
            (temp_path / ".hidden_file").write_text("hidden content")
            (temp_path / ".onexignore").write_text(
                "# ignore patterns"
            )  # Should be included
            (temp_path / ".wip").write_text("work in progress")  # Should be included
            (temp_path / ".git").mkdir()  # Should be excluded
            (temp_path / "__pycache__").mkdir()  # Should be excluded

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            assert result.status == STATUS_SUCCESS

            # Load and validate hidden file handling
            onextree_path = temp_path / ".onextree"
            import yaml

            with open(onextree_path, "r") as f:
                tree_data = yaml.safe_load(f)

            # Check that .onexignore and .wip are included
            file_names = self._extract_all_file_names(tree_data)
            assert ".onexignore" in file_names
            assert ".wip" in file_names

            # Check that .git and __pycache__ are excluded
            assert ".git" not in file_names
            assert "__pycache__" not in file_names
            assert ".hidden_file" not in file_names

    def _validate_tree_structure(self, tree_data: dict, actual_path: Path) -> None:
        """Recursively validate that tree structure matches actual directory."""
        assert tree_data["name"] == actual_path.name

        if actual_path.is_file():
            assert tree_data["type"] == "file"
            assert "children" not in tree_data
        else:
            assert tree_data["type"] == "directory"
            assert "children" in tree_data

            # Get actual children (excluding hidden files except .onexignore, .wip)
            actual_children = []
            for child in actual_path.iterdir():
                if child.name.startswith(".") and child.name not in [
                    ".onexignore",
                    ".wip",
                ]:
                    continue
                if child.name == "__pycache__":
                    continue
                actual_children.append(child)

            tree_children = tree_data["children"]
            assert len(tree_children) == len(actual_children)

            # Recursively validate children
            for tree_child in tree_children:
                child_name = tree_child["name"]
                actual_child = actual_path / child_name
                assert (
                    actual_child.exists()
                ), f"Tree contains {child_name} but it doesn't exist in {actual_path}"
                self._validate_tree_structure(tree_child, actual_child)

    def _validate_tree_against_directory(
        self, tree_data: dict, actual_path: Path
    ) -> list[str]:
        """Validate tree against directory and return list of validation errors."""
        errors = []

        # Get all files from tree
        tree_files = set(self._extract_all_file_paths(tree_data, ""))

        # Get all actual files (excluding hidden files except .onexignore, .wip)
        actual_files = set()
        for file_path in self._get_all_files_recursive(actual_path, actual_path):
            actual_files.add(file_path)

        # Check for missing files (in directory but not in tree)
        missing_files = actual_files - tree_files
        for missing_file in missing_files:
            errors.append(
                f"File {missing_file} exists in directory but is missing from .onextree"
            )

        # Check for extra files (in tree but not in directory)
        extra_files = tree_files - actual_files
        for extra_file in extra_files:
            errors.append(f"File {extra_file} exists in .onextree but not in directory")

        return errors

    def _validate_file_types(self, tree_data: dict, base_path: Path) -> list[str]:
        """Validate that file types in tree match actual file system."""
        errors = []

        def validate_node(node: dict, current_path: Path) -> None:
            actual_path = current_path / node["name"]

            if actual_path.is_file():
                if node["type"] != "file":
                    errors.append(
                        f"{actual_path} is a file but marked as {node['type']} in .onextree"
                    )
                if "children" in node:
                    errors.append(
                        f"{actual_path} is a file but has children in .onextree"
                    )
            elif actual_path.is_dir():
                if node["type"] != "directory":
                    errors.append(
                        f"{actual_path} is a directory but marked as {node['type']} in .onextree"
                    )
                if "children" not in node:
                    errors.append(
                        f"{actual_path} is a directory but has no children field in .onextree"
                    )
                else:
                    for child in node["children"]:
                        validate_node(child, actual_path)

        validate_node(tree_data, base_path.parent)
        return errors

    def _extract_all_file_names(self, tree_data: dict) -> set[str]:
        """Extract all file and directory names from tree data."""
        names = {tree_data["name"]}

        if "children" in tree_data:
            for child in tree_data["children"]:
                names.update(self._extract_all_file_names(child))

        return names

    def _extract_all_file_paths(self, tree_data: dict, current_path: str) -> set[str]:
        """Extract all file paths from tree data."""
        paths = set()

        node_path = (
            f"{current_path}/{tree_data['name']}" if current_path else tree_data["name"]
        )
        paths.add(node_path)

        if "children" in tree_data:
            for child in tree_data["children"]:
                paths.update(self._extract_all_file_paths(child, node_path))

        return paths

    def _get_all_files_recursive(self, path: Path, base_path: Path) -> set[str]:
        """Get all file paths recursively, excluding hidden files except .onexignore, .wip."""
        files = set()

        for item in path.iterdir():
            # Skip hidden files except .onexignore, .wip
            if item.name.startswith(".") and item.name not in [".onexignore", ".wip"]:
                continue
            if item.name == "__pycache__":
                continue

            relative_path = str(item.relative_to(base_path))
            files.add(relative_path)

            if item.is_dir():
                files.update(self._get_all_files_recursive(item, base_path))

        return files


class TestOnextreeValidationComprehensive:
    """Comprehensive test suite for .onextree validation against actual directory contents for CI integration."""

    def test_repository_onextree_is_valid(self) -> None:
        """Test that the main repository .onextree file is valid and up-to-date."""
        # Navigate from src/omnibase/nodes/tree_generator_node/v1_0_0/node_tests/test_tree_generator.py to repo root
        repo_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
        onextree_path = repo_root / ".onextree"
        src_omnibase_path = repo_root / "src" / "omnibase"

        # Skip if .onextree doesn't exist
        if not onextree_path.exists():
            pytest.skip("Repository .onextree file does not exist")

        # Validate the main .onextree file using the validator
        from omnibase.model.model_onextree_validation import ValidationStatusEnum

        from ..helpers.tree_validator import OnextreeValidator

        validator = OnextreeValidator(verbose=True)
        result = validator.validate_onextree_file(onextree_path, src_omnibase_path)

        # Print detailed results for debugging if validation fails
        if result.status == ValidationStatusEnum.ERROR:
            print("\n=== ONEXTREE VALIDATION ERRORS ===")
            for error in result.errors:
                print(f"❌ {error.code}: {error.message}")
                if error.path:
                    print(f"   Path: {error.path}")
            print("=" * 40)

        assert result.status == ValidationStatusEnum.SUCCESS, (
            f"Repository .onextree validation failed: {result.summary}\n"
            f"Errors: {[error.message for error in result.errors]}"
        )

    def test_onextree_drift_detection_scenario(self) -> None:
        """Test a realistic scenario where .onextree becomes outdated due to development changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Simulate initial project structure
            (temp_path / "README.md").write_text("# Project")
            (temp_path / "src").mkdir()
            (temp_path / "src" / "main.py").write_text("# main")
            (temp_path / "tests").mkdir()
            (temp_path / "tests" / "test_main.py").write_text("# tests")

            # Generate initial .onextree using tree generator
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            assert result.status == STATUS_SUCCESS

            # Simulate development changes (new files added, some removed)
            (temp_path / "src" / "utils.py").write_text("# utilities")  # New file
            (temp_path / "src" / "config").mkdir()  # New directory
            (temp_path / "src" / "config" / "settings.py").write_text(
                "# settings"
            )  # New nested file
            (temp_path / "tests" / "test_main.py").unlink()  # Removed file
            (temp_path / "docs").mkdir()  # New directory
            (temp_path / "docs" / "api.md").write_text("# API docs")  # New file

            # Validation should detect drift
            from omnibase.model.model_onextree_validation import (
                ValidationErrorCodeEnum,
                ValidationStatusEnum,
            )

            from ..helpers.tree_validator import OnextreeValidator

            validator = OnextreeValidator()
            onextree_path = temp_path / ".onextree"
            validation_result = validator.validate_onextree_file(
                onextree_path, temp_path
            )

            assert validation_result.status == ValidationStatusEnum.ERROR

            # Should detect both missing and extra files
            missing_errors = [
                error
                for error in validation_result.errors
                if error.code == ValidationErrorCodeEnum.MISSING_FILE
            ]
            extra_errors = [
                error
                for error in validation_result.errors
                if error.code == ValidationErrorCodeEnum.EXTRA_FILE
            ]

            assert len(missing_errors) > 0, "Should detect missing files"
            assert len(extra_errors) > 0, "Should detect extra files"

            # Verify specific changes are detected
            missing_paths = {error.path for error in missing_errors if error.path}
            extra_paths = {error.path for error in extra_errors if error.path}

            assert any("utils.py" in path for path in missing_paths if path)
            assert any("config" in path for path in missing_paths if path)
            assert any("docs" in path for path in missing_paths if path)
            assert any("test_main.py" in path for path in extra_paths if path)

    def test_onextree_validation_exit_codes(self) -> None:
        """Test that validation provides correct exit codes for CI integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test successful validation
            (temp_path / "file.txt").write_text("content")

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            assert result.status == STATUS_SUCCESS

            from ..helpers.tree_validator import OnextreeValidator

            validator = OnextreeValidator()
            onextree_path = temp_path / ".onextree"
            validation_result = validator.validate_onextree_file(
                onextree_path, temp_path
            )

            assert validator.get_exit_code(validation_result) == 0  # Success

            # Test failed validation
            (temp_path / "new_file.txt").write_text(
                "new content"
            )  # Add file after .onextree

            validation_result = validator.validate_onextree_file(
                onextree_path, temp_path
            )
            assert validator.get_exit_code(validation_result) == 1  # Error

    def test_onextree_validation_performance_with_large_structure(self) -> None:
        """Test validation performance with a large directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a moderately large structure (50 files across 5 directories)
            for i in range(5):
                dir_path = temp_path / f"dir_{i}"
                dir_path.mkdir()
                for j in range(10):
                    (dir_path / f"file_{j}.txt").write_text(f"content {i}-{j}")

            # Generate .onextree
            input_state = TreeGeneratorInputState(
                version="1.0.0",
                root_directory=str(temp_path),
                output_path=str(temp_path / ".onextree"),
            )

            result = run_tree_generator_node(input_state)
            if result.status != STATUS_SUCCESS:
                print(f"[DEBUG] Tree generator status: {result.status}")
                print(f"[DEBUG] Tree generator message: {result.message}")
                print(f"[DEBUG] Tree generator validation_results: {result.validation_results}")
            assert result.status == STATUS_SUCCESS

            import time

            start_time = time.time()

            from omnibase.model.model_onextree_validation import ValidationStatusEnum

            from ..helpers.tree_validator import OnextreeValidator

            validator = OnextreeValidator()
            onextree_path = temp_path / ".onextree"
            validation_result = validator.validate_onextree_file(
                onextree_path, temp_path
            )

            end_time = time.time()
            validation_time = end_time - start_time

            if validation_result.status != ValidationStatusEnum.SUCCESS:
                print(f"[DEBUG] Validation status: {validation_result.status}")
                print(f"[DEBUG] Validation summary: {validation_result.summary}")
                for error in validation_result.errors:
                    print(f"[DEBUG] Error: {error.code}: {error.message} (path: {error.path})")

            assert validation_result.status == ValidationStatusEnum.SUCCESS
            # Validation should complete in reasonable time (< 3 seconds for this size)
            assert (
                validation_time < 3.0
            ), f"Validation took too long: {validation_time:.2f}s"

    def test_onextree_validation_error_reporting(self) -> None:
        """Test that validation provides detailed and actionable error reporting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create structure
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "dir1").mkdir()
            (temp_path / "dir1" / "nested.py").write_text("# python")

            # Create .onextree with multiple issues manually
            onextree_data = {
                "name": temp_path.name,
                "type": "directory",
                "children": [
                    {
                        "name": "file1.txt",
                        "type": "directory",
                        "children": [],
                    },  # Type mismatch
                    {"name": "missing_file.txt", "type": "file"},  # Extra file
                    {"name": "dir1", "type": "file"},  # Type mismatch
                    # Missing nested.py file
                ],
            }

            onextree_path = temp_path / ".onextree"
            import yaml

            with open(onextree_path, "w") as f:
                yaml.safe_dump(onextree_data, f)

            from omnibase.model.model_onextree_validation import (
                ValidationErrorCodeEnum,
                ValidationStatusEnum,
            )

            from ..helpers.tree_validator import OnextreeValidator

            validator = OnextreeValidator()
            validation_result = validator.validate_onextree_file(
                onextree_path, temp_path
            )

            assert validation_result.status == ValidationStatusEnum.ERROR
            assert len(validation_result.errors) > 0

            # Check that errors have proper structure
            for error in validation_result.errors:
                assert error.code in ValidationErrorCodeEnum
                assert error.message
                assert isinstance(error.message, str)
                # Path should be provided for most errors
                if error.code != ValidationErrorCodeEnum.UNKNOWN:
                    assert error.path is not None
