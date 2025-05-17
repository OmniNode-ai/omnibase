from pathlib import Path

import pytest

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_metadata import MetadataBlockModel
from omnibase.model.model_schema import SchemaModel
from omnibase.schema.loader import SchemaLoader
from omnibase.utils.yaml_extractor import extract_example_from_schema


@pytest.fixture(
    params=[
        Path("src/omnibase/schemas/onex_node.yaml"),
        # Add more paths or use a factory to generate temp files for unit tests
    ]
)
def onex_yaml_path(request):
    return request.param


@pytest.fixture(
    params=[
        Path("src/omnibase/schemas/state_contract.json"),
        # Add more paths or use a factory to generate temp files for unit tests
    ]
)
def json_schema_path(request):
    return request.param


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request):
    return request.param


def compare_model_to_dict(model, data):
    """
    Type-aware comparison of a Pydantic model instance to a dict.
    Handles Enums, lists, and optional fields. Ignores extra fields in dict.
    """
    from enum import Enum

    model_cls = model.__class__
    for field in getattr(model_cls, "model_fields", {}):
        model_value = getattr(model, field)
        if field not in data:
            # Optional or missing in dict, skip
            continue
        dict_value = data[field]
        if isinstance(model_value, Enum):
            assert (
                model_value.value == dict_value
            ), f"Enum field {field}: {model_value.value} != {dict_value}"
        elif isinstance(model_value, list):
            assert set(model_value) == set(
                dict_value
            ), f"List field {field}: {model_value} != {dict_value}"
        elif hasattr(model_value, "__class__") and hasattr(
            model_value.__class__, "model_fields"
        ):
            compare_model_to_dict(model_value, dict_value)
        else:
            assert (
                model_value == dict_value
            ), f"Field {field}: {model_value} != {dict_value}"


class TestSchemaLoader:
    """
    Canonical, context-agnostic test for SchemaLoader.
    All file paths are injected via fixtures, not hardcoded.
    This pattern supports both unit and integration tests.
    """

    def setup_method(self):
        self.loader = SchemaLoader()

    def test_load_json_schema_success(self, json_schema_path):
        """Test loading a valid JSON schema file."""
        result = self.loader.load_json_schema(json_schema_path)
        assert isinstance(result, SchemaModel)
        assert result.schema_uri is not None or result.title is not None

    def test_load_onex_yaml_missing(self):
        """Test loading a missing YAML file raises OmniBaseError."""
        path = Path("does_not_exist.yaml")
        with pytest.raises(OmniBaseError):
            self.loader.load_onex_yaml(path)

    def test_load_json_schema_missing(self):
        """Test loading a missing JSON file raises OmniBaseError."""
        path = Path("does_not_exist.json")
        with pytest.raises(OmniBaseError):
            self.loader.load_json_schema(path)

    def test_discover_schemas_finds_all(self):
        """Test that discover_schemas finds all expected schemas in the directory."""
        schemas_dir = Path("src/omnibase/schemas")
        found = self.loader.discover_schemas(schemas_dir)
        assert any(f.name == "onex_node.yaml" for f in found)
        assert any(f.name == "state_contract.json" for f in found)

    def test_discover_schemas_skips_malformed(self, tmp_path):
        """Test that discover_schemas skips malformed schema files."""
        # Create a valid and a malformed schema file
        valid_yaml = tmp_path / "valid.yaml"
        valid_yaml.write_text("schema_version: '0.1.0'\nname: test\n")
        malformed_yaml = tmp_path / "malformed.yaml"
        malformed_yaml.write_text(": this is not valid yaml ::::\n")
        found = self.loader.discover_schemas(tmp_path)
        assert valid_yaml in found
        assert malformed_yaml not in found

    def test_load_onex_yaml_from_schema_example(self, tmp_path):
        """Test loading ONEX YAML from a schema example."""
        schema_path = Path("src/omnibase/schemas/onex_node.yaml")
        example = extract_example_from_schema(schema_path, 0)
        node_path = tmp_path / "node.onex.yaml"
        import yaml as _yaml

        node_path.write_text(_yaml.dump(example))
        result = self.loader.load_onex_yaml(node_path)
        assert isinstance(result, MetadataBlockModel)
        compare_model_to_dict(result, example)
