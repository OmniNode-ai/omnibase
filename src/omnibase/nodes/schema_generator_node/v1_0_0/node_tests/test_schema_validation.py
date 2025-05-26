# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_schema_validation.py
# version: 1.0.0
# uuid: 8fe23e0a-b1b9-4ab7-868c-cf590619d8b5
# author: OmniNode Team
# created_at: 2025-05-25T15:41:15.123132
# last_modified_at: 2025-05-25T19:48:02.873474
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 800d30d2100970a904e7a4d4bd8a843ebd8f97e68f89b9258096c9d9f40e28b1
# entrypoint: python@test_schema_validation.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_schema_validation
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for schema generator node validation functionality.

This module contains tests to validate that the schema generator node works correctly
and that committed schemas are up-to-date with current state models.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from omnibase.core.error_codes import OnexError
from omnibase.nodes.schema_generator_node.v1_0_0.models.state import (
    SchemaGeneratorInputState,
    SchemaGeneratorOutputState,
    create_schema_generator_input_state,
    create_schema_generator_output_state,
)
from omnibase.nodes.schema_generator_node.v1_0_0.node import SchemaGeneratorNode


class TestSchemaGeneratorNode:
    """Test cases for the SchemaGeneratorNode class."""

    def test_node_initialization(self) -> None:
        """Test that the node initializes correctly with all available models."""
        node = SchemaGeneratorNode()

        # Check that all expected models are available
        expected_models = {
            "stamper_input",
            "stamper_output",
            "tree_generator_input",
            "tree_generator_output",
            "registry_loader_input",
            "registry_loader_output",
            "template_input",
            "template_output",
            "schema_generator_input",
            "schema_generator_output",
        }

        assert set(node.available_models.keys()) == expected_models

    def test_generate_all_schemas(self) -> None:
        """Test generating all schemas to a temporary directory."""
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                include_metadata=True,
            )

            output_state = node.execute(input_state)

            assert output_state.status == "success"
            assert output_state.total_schemas == 10
            assert len(output_state.schemas_generated) == 10
            assert output_state.output_directory == temp_dir

            # Check that all expected schema files were created
            temp_path = Path(temp_dir)
            schema_files = list(temp_path.glob("*.schema.json"))
            assert len(schema_files) == 10

            # Verify each schema file is valid JSON
            for schema_file in schema_files:
                with open(schema_file, "r") as f:
                    schema_data = json.load(f)
                    assert "$schema" in schema_data
                    assert "$id" in schema_data
                    assert "properties" in schema_data

    def test_generate_specific_schemas(self) -> None:
        """Test generating only specific schemas."""
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                models_to_generate=["stamper_input", "stamper_output"],
                include_metadata=True,
            )

            output_state = node.execute(input_state)

            assert output_state.status == "success"
            assert output_state.total_schemas == 2
            assert len(output_state.schemas_generated) == 2
            assert "stamper_input.schema.json" in output_state.schemas_generated
            assert "stamper_output.schema.json" in output_state.schemas_generated

    def test_generate_without_metadata(self) -> None:
        """Test generating schemas without metadata."""
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                models_to_generate=["stamper_input"],
                include_metadata=False,
            )

            output_state = node.execute(input_state)

            assert output_state.status == "success"
            assert output_state.total_schemas == 1

            # Check that metadata is not included
            schema_file = Path(temp_dir) / "stamper_input.schema.json"
            with open(schema_file, "r") as f:
                schema_data = json.load(f)
                assert "$schema" not in schema_data
                assert "$id" not in schema_data

    def test_invalid_model_names(self) -> None:
        """Test handling of invalid model names."""
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                models_to_generate=["invalid_model", "another_invalid"],
            )

            output_state = node.execute(input_state)

            assert output_state.status == "failure"
            assert "Invalid model names" in output_state.message
            assert output_state.total_schemas == 0

    def test_correlation_id_propagation(self) -> None:
        """Test that correlation ID is properly propagated."""
        node = SchemaGeneratorNode()
        correlation_id = "test-correlation-123"

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                models_to_generate=["stamper_input"],
                correlation_id=correlation_id,
            )

            output_state = node.execute(input_state)

            assert output_state.correlation_id == correlation_id


class TestSchemaValidation:
    """Test cases for schema validation against committed schemas."""

    def load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a JSON file."""
        with open(file_path, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data

    def compare_schemas(
        self, current_dir: Path, generated_dir: Path
    ) -> tuple[bool, list[str]]:
        """
        Compare schemas in two directories.

        Returns:
            Tuple of (all_match, error_messages)
        """
        current_files = set(f.name for f in current_dir.glob("*.schema.json"))
        generated_files = set(f.name for f in generated_dir.glob("*.schema.json"))

        errors = []

        # Check for missing or extra files
        if current_files != generated_files:
            missing = generated_files - current_files
            extra = current_files - generated_files

            if missing:
                errors.append(f"Missing schema files: {missing}")
            if extra:
                errors.append(f"Extra schema files: {extra}")

        # Compare content of each file
        for filename in current_files.intersection(generated_files):
            current_schema = self.load_json_file(current_dir / filename)
            generated_schema = self.load_json_file(generated_dir / filename)

            if current_schema != generated_schema:
                errors.append(f"Schema mismatch: {filename}")

        return len(errors) == 0, errors

    def test_committed_schemas_are_up_to_date(self) -> None:
        """Test that committed schemas match current state models."""
        # Path to committed schemas
        current_schemas_dir = Path("src/schemas")

        # Skip test if schema directory doesn't exist
        if not current_schemas_dir.exists():
            pytest.skip("Schema directory not found - run schema generator first")

        # Generate schemas in temporary directory
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_schemas_dir = Path(temp_dir) / "schemas"

            input_state = create_schema_generator_input_state(
                output_directory=str(temp_schemas_dir),
                include_metadata=True,
            )

            output_state = node.execute(input_state)

            assert (
                output_state.status == "success"
            ), f"Schema generation failed: {output_state.message}"

            # Compare schemas
            schemas_match, errors = self.compare_schemas(
                current_schemas_dir, temp_schemas_dir
            )

            if not schemas_match:
                error_msg = "Committed schemas are out-of-date:\n" + "\n".join(
                    f"  - {error}" for error in errors
                )
                error_msg += "\n\nTo fix: poetry run python -m omnibase.nodes.schema_generator_node.v1_0_0.node"
                pytest.fail(error_msg)

    def test_schema_content_validity(self) -> None:
        """Test that generated schemas have valid JSON Schema structure."""
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                include_metadata=True,
            )

            output_state = node.execute(input_state)
            assert output_state.status == "success"

            # Validate each generated schema
            temp_path = Path(temp_dir)
            for schema_file in temp_path.glob("*.schema.json"):
                schema_data = self.load_json_file(schema_file)

                # Check required JSON Schema fields
                assert "type" in schema_data
                assert "properties" in schema_data
                assert "$schema" in schema_data
                assert "$id" in schema_data

                # Check that it's an object schema
                assert schema_data["type"] == "object"

                # Check that properties is a dict
                assert isinstance(schema_data["properties"], dict)

                # Check that all properties have types
                for prop_name, prop_def in schema_data["properties"].items():
                    assert (
                        "type" in prop_def or "anyOf" in prop_def or "$ref" in prop_def
                    ), f"Property {prop_name} missing type definition"

    def test_schema_metadata_consistency(self) -> None:
        """Test that schema metadata is consistent across all schemas."""
        node = SchemaGeneratorNode()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_state = create_schema_generator_input_state(
                output_directory=temp_dir,
                include_metadata=True,
            )

            output_state = node.execute(input_state)
            assert output_state.status == "success"

            # Check metadata consistency
            temp_path = Path(temp_dir)
            for schema_file in temp_path.glob("*.schema.json"):
                schema_data = self.load_json_file(schema_file)

                # Check consistent JSON Schema version
                assert (
                    schema_data["$schema"]
                    == "https://json-schema.org/draft/2020-12/schema"
                )

                # Check consistent ID format
                expected_id = f"https://onex.schemas/{schema_file.name}"
                assert schema_data["$id"] == expected_id


class TestStateModels:
    """Test cases for schema generator state models."""

    def test_input_state_creation(self) -> None:
        """Test creating input state with factory function."""
        input_state = create_schema_generator_input_state(
            output_directory="test/dir",
            models_to_generate=["test_model"],
            include_metadata=False,
            correlation_id="test-123",
        )

        assert input_state.output_directory == "test/dir"
        assert input_state.models_to_generate == ["test_model"]
        assert input_state.include_metadata is False
        assert input_state.correlation_id == "test-123"
        assert input_state.version == "1.0.0"

    def test_output_state_creation(self) -> None:
        """Test creating output state with factory function."""
        output_state = create_schema_generator_output_state(
            status="success",
            message="Test message",
            schemas_generated=["test.schema.json"],
            output_directory="test/dir",
            total_schemas=1,
            correlation_id="test-123",
        )

        assert output_state.status == "success"
        assert output_state.message == "Test message"
        assert output_state.schemas_generated == ["test.schema.json"]
        assert output_state.output_directory == "test/dir"
        assert output_state.total_schemas == 1
        assert output_state.correlation_id == "test-123"
        assert output_state.version == "1.0.0"

    def test_input_state_validation(self) -> None:
        """Test input state field validation."""
        # Test empty output directory validation
        with pytest.raises(OnexError, match="output_directory cannot be empty"):
            SchemaGeneratorInputState(output_directory="")

    def test_output_state_validation(self) -> None:
        """Test output state field validation."""
        # Test invalid status
        with pytest.raises(OnexError, match="status must be one of"):
            SchemaGeneratorOutputState(
                status="invalid",
                message="test",
                output_directory="test",
            )

        # Test empty message
        with pytest.raises(OnexError, match="message cannot be empty"):
            SchemaGeneratorOutputState(
                status="success",
                message="",
                output_directory="test",
            )

        # Test negative total_schemas
        with pytest.raises(OnexError, match="total_schemas must be non-negative"):
            SchemaGeneratorOutputState(
                status="success",
                message="test",
                output_directory="test",
                total_schemas=-1,
            )
