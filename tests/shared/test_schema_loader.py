# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:28.099548'
# description: Stamped by PythonHandler
# entrypoint: python://test_schema_loader.py
# hash: be70e88d8dfed2e3c52e35eeffa9f377e881734da4a5951c75ad407f95727139
# last_modified_at: '2025-05-29T13:51:24.223621+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_schema_loader.py
# namespace: py://omnibase.tests.shared.test_schema_loader_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 9007a967-ec8a-4407-80af-f7a143a4349f
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, cast

import pytest

from omnibase.exceptions import OmniBaseError  # type: ignore[import-untyped]
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_schema import SchemaModel  # type: ignore[import-untyped]
from omnibase.schemas.loader import SchemaLoader  # type: ignore[import-untyped]
from omnibase.utils.yaml_extractor import (
    extract_example_from_schema,  # type: ignore[import-untyped]
)


@pytest.fixture(
    params=[
        Path("src/omnibase/schemas/onex_node.yaml"),
        # Add more paths or use a factory to generate temp files for unit tests
    ]
)
def onex_yaml_path(request: Any) -> Path:
    return cast(Path, request.param)


@pytest.fixture(
    params=[
        Path("src/omnibase/schemas/state_contract.json"),
        # Add more paths or use a factory to generate temp files for unit tests
    ]
)
def json_schema_path(request: Any) -> Path:
    return cast(Path, request.param)


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request: Any) -> str:
    return cast(str, request.param)


def compare_model_to_dict(model: Any, data: dict[str, Any]) -> None:
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


class ConcreteSchemaLoader(SchemaLoader):
    def __init__(self, event_bus):
        super().__init__(event_bus)

    def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
        return {}


@pytest.fixture
def schema_loader(protocol_event_bus):
    return ConcreteSchemaLoader(event_bus=protocol_event_bus)


class TestSchemaLoader:
    """
    Canonical, context-agnostic test for SchemaLoader.
    All file paths are injected via fixtures, not hardcoded.
    This pattern supports both unit and integration tests.
    """

    def setup_method(self):
        pass  # Loader is now provided by fixture

    def test_load_json_schema_success(self, json_schema_path: Path, schema_loader):
        """Test loading a valid JSON schema file."""
        result = schema_loader.load_json_schema(json_schema_path)
        assert isinstance(result, SchemaModel)
        assert result.schema_uri is not None or result.title is not None

    def test_load_onex_yaml_missing(self, schema_loader):
        """Test loading a missing YAML file raises OmniBaseError."""
        path = Path("does_not_exist.yaml")
        with pytest.raises(OmniBaseError):
            schema_loader.load_onex_yaml(path)

    def test_load_json_schema_missing(self, schema_loader):
        """Test loading a missing JSON file raises OmniBaseError."""
        path = Path("does_not_exist.json")
        with pytest.raises(OmniBaseError):
            schema_loader.load_json_schema(path)

    def test_discover_schemas_finds_all(self, schema_loader):
        """Test that discover_schemas finds all expected schemas in the directory."""
        schemas_dir = Path("src/omnibase/schemas")
        found = schema_loader.discover_schemas(schemas_dir)
        assert any(f.name == "onex_node.yaml" for f in found)
        assert any(f.name == "state_contract.json" for f in found)

    def test_discover_schemas_skips_malformed(self, tmp_path: Path, schema_loader):
        """Test that discover_schemas skips malformed schema files."""
        # Create a valid and a malformed schema file
        valid_yaml = tmp_path / "valid.yaml"
        valid_yaml.write_text("schema_version: '0.1.0'\nname: test\n")
        malformed_yaml = tmp_path / "malformed.yaml"
        malformed_yaml.write_text(": this is not valid yaml ::::\n")
        found = schema_loader.discover_schemas(tmp_path)
        assert valid_yaml in found
        assert malformed_yaml not in found

    def test_load_onex_yaml_from_schema_example(self, tmp_path: Path, schema_loader):
        """Test loading ONEX YAML from a schema example."""
        schema_path = Path("src/omnibase/schemas/onex_node.yaml")
        example = extract_example_from_schema(schema_path, 0)
        # Patch dependencies for strong typing
        if "dependencies" in example and isinstance(example["dependencies"], list):
            new_deps = []
            for dep in example["dependencies"]:
                if isinstance(dep, str):
                    new_deps.append({
                        "uri": dep,
                        "name": "autogenerated",
                        "type": "tool",
                        "target": "default"
                    })
                else:
                    new_deps.append(dep)
            example["dependencies"] = new_deps
        node_path = tmp_path / "node.onex.yaml"
        import yaml as _yaml
        node_path.write_text(_yaml.dump(example))
        result = schema_loader.load_onex_yaml(node_path)
        assert isinstance(result, NodeMetadataBlock)
        # Optionally: compare_model_to_dict(result, example)
