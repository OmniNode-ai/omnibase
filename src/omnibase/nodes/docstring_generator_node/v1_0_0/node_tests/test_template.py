# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_template.py
# version: 1.0.0
# uuid: d57be13a-9b02-4940-9c78-819e34bf005d
# author: OmniNode Team
# created_at: 2025-05-27T07:34:49.190491
# last_modified_at: 2025-05-27T11:55:57.526040
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 996973011d6df370a62cc35e624ed9ea2a2df029800509e2e28cee5ff80e2093
# entrypoint: python@test_template.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_template
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test suite for docstring_generator_node.

This module contains comprehensive tests for the docstring generator node,
including unit tests for documentation generation, schema processing,
and template rendering functionality.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from omnibase.core.error_codes import OnexError
from omnibase.enums import OnexStatus

from ..models.state import (
    DocstringGeneratorInputState,
    DocstringGeneratorOutputState,
    create_docstring_generator_input_state,
)
from ..node import DocstringGeneratorNode, run_docstring_generator_node


class TestDocstringGeneratorNode:
    """Test class for docstring generator node functionality."""

    def test_node_introspection_methods(self) -> None:
        """Test that the node implements all required introspection methods."""
        # Test class methods
        assert DocstringGeneratorNode.get_node_name() == "docstring_generator_node"
        assert DocstringGeneratorNode.get_node_version() == "1.0.0"
        assert "documentation" in DocstringGeneratorNode.get_node_description().lower()
        assert (
            DocstringGeneratorNode.get_input_state_class()
            == DocstringGeneratorInputState
        )
        assert (
            DocstringGeneratorNode.get_output_state_class()
            == DocstringGeneratorOutputState
        )

        # Test error codes class
        error_codes_class = DocstringGeneratorNode.get_error_codes_class()
        assert error_codes_class is not None

    def test_docstring_generator_node_success(self, tmp_path: Path) -> None:
        """Test successful execution of docstring generator node."""
        # Create test schema file
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()

        schema_file = schema_dir / "test_schema.yaml"
        schema_file.write_text(
            """
title: Test Schema
description: A test schema for documentation generation
type: object
properties:
  name:
    type: string
    description: The name field
  age:
    type: integer
    description: The age field
required:
  - name
examples:
  - name: "John Doe"
    age: 30
"""
        )

        # Create test template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_file = template_dir / "test_template.md.j2"
        template_file.write_text(
            """
# {{ title }}

{{ description }}

## Fields

{% for field in fields %}
- **{{ field.name }}** ({{ field.type }}): {{ field.description }}
  {% if field.required %}*Required*{% endif %}
{% endfor %}

{% if examples %}
## Examples

{% for example in examples %}
```yaml
{{ example }}
```
{% endfor %}
{% endif %}
"""
        )

        # Create output directory
        output_dir = tmp_path / "output"

        # Create input state
        input_state = create_docstring_generator_input_state(
            schema_directory=str(schema_dir),
            template_path=str(template_file),
            output_directory=str(output_dir),
            include_examples=True,
            verbose=False,
        )

        # Run the node
        result = run_docstring_generator_node(input_state)

        # Verify results
        assert isinstance(result, DocstringGeneratorOutputState)
        assert result.status == OnexStatus.SUCCESS
        assert len(result.generated_documents) == 1
        assert len(result.error_files) == 0

        # Check generated document
        doc = result.generated_documents[0]
        assert doc.schema_name == "test_schema"
        assert doc.title == "Test Schema"
        assert doc.field_count == 2
        assert doc.example_count == 1

        # Check output file was created
        output_file = output_dir / "test_schema.md"
        assert output_file.exists()

        content = output_file.read_text()
        assert "Test Schema" in content
        assert "name" in content
        assert "age" in content

    def test_docstring_generator_node_with_minimal_input(self, tmp_path: Path) -> None:
        """Test docstring generator node with minimal required input."""
        # Create minimal schema
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()

        schema_file = schema_dir / "minimal.yaml"
        schema_file.write_text(
            """
title: Minimal Schema
type: object
"""
        )

        # Create minimal template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_file = template_dir / "minimal.md.j2"
        template_file.write_text("# {{ title }}")

        output_dir = tmp_path / "output"

        input_state = create_docstring_generator_input_state(
            schema_directory=str(schema_dir),
            template_path=str(template_file),
            output_directory=str(output_dir),
            include_examples=False,
        )

        result = run_docstring_generator_node(input_state)

        assert result.status == OnexStatus.SUCCESS
        assert len(result.generated_documents) == 1
        assert result.generated_documents[0].example_count == 0

    def test_docstring_generator_node_error_handling(self, tmp_path: Path) -> None:
        """Test error handling in docstring generator node."""
        # Test with non-existent schema directory
        input_state = create_docstring_generator_input_state(
            schema_directory="/nonexistent/path",
            template_path="/nonexistent/template.j2",
            output_directory=str(tmp_path / "output"),
        )

        result = run_docstring_generator_node(input_state)

        assert result.status == OnexStatus.ERROR
        assert "not found" in result.message.lower()

    def test_docstring_generator_node_state_validation(self) -> None:
        """Test input state validation."""
        # Test with empty schema directory
        with pytest.raises(OnexError):
            create_docstring_generator_input_state(
                schema_directory="",
                template_path="template.j2",
                output_directory="output",
            )

    def test_docstring_generator_node_output_state_structure(
        self, tmp_path: Path
    ) -> None:
        """Test output state structure and validation."""
        # Create minimal test setup
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()

        schema_file = schema_dir / "test.yaml"
        schema_file.write_text("title: Test\ntype: object")

        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_file = template_dir / "test.md.j2"
        template_file.write_text("# {{ title }}")

        output_dir = tmp_path / "output"

        input_state = create_docstring_generator_input_state(
            schema_directory=str(schema_dir),
            template_path=str(template_file),
            output_directory=str(output_dir),
        )

        result = run_docstring_generator_node(input_state)

        # Test output state structure
        assert hasattr(result, "status")
        assert hasattr(result, "message")
        assert hasattr(result, "generated_documents")
        assert hasattr(result, "skipped_files")
        assert hasattr(result, "error_files")
        assert hasattr(result, "summary")
        assert hasattr(result, "output_directory")

        # Test that output can be serialized
        json_output = result.model_dump_json()
        assert isinstance(json_output, str)
        assert len(json_output) > 0


class TestDocstringGeneratorNodeIntegration:
    """Integration tests for docstring generator node."""

    def test_docstring_generator_node_end_to_end(self, tmp_path: Path) -> None:
        """End-to-end test for docstring generator node."""
        # Create a realistic schema structure
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()

        # Create multiple schema files
        for i in range(3):
            schema_file = schema_dir / f"schema_{i}.yaml"
            schema_file.write_text(
                f"""
title: Schema {i}
description: Test schema number {i}
type: object
properties:
  field_{i}:
    type: string
    description: Field {i}
required:
  - field_{i}
"""
            )

        # Create template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_file = template_dir / "schema.md.j2"
        template_file.write_text(
            """
# {{ title }}

{{ description }}

## Fields
{% for field in fields %}
- {{ field.name }}: {{ field.description }}
{% endfor %}
"""
        )

        output_dir = tmp_path / "output"

        input_state = create_docstring_generator_input_state(
            schema_directory=str(schema_dir),
            template_path=str(template_file),
            output_directory=str(output_dir),
            verbose=True,
        )

        result = run_docstring_generator_node(input_state)

        # Verify all schemas were processed
        assert result.status == OnexStatus.SUCCESS
        assert len(result.generated_documents) == 3
        assert result.summary["generated"] == 3
        assert result.summary["errors"] == 0

        # Verify all output files exist
        for i in range(3):
            output_file = output_dir / f"schema_{i}.md"
            assert output_file.exists()


# Test fixtures
@pytest.fixture
def docstring_generator_input_state(tmp_path: Path) -> DocstringGeneratorInputState:
    """Fixture for common input state."""
    # Create minimal test setup
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()

    schema_file = schema_dir / "fixture_test.yaml"
    schema_file.write_text("title: Fixture Test\ntype: object")

    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "fixture.md.j2"
    template_file.write_text("# {{ title }}")

    output_dir = tmp_path / "output"

    return create_docstring_generator_input_state(
        schema_directory=str(schema_dir),
        template_path=str(template_file),
        output_directory=str(output_dir),
    )


@pytest.fixture
def mock_event_bus() -> Mock:
    """Fixture for mock event bus."""
    return Mock()
