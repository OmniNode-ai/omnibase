# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_schema_loader.py
# version: 1.0.0
# uuid: abc3c233-c515-48ed-a15f-49b74f40e7db
# author: OmniNode Team
# created_at: 2025-05-21T13:18:56.578705
# last_modified_at: 2025-05-22T20:50:39.722689
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ccc6ebaa19d729d8765111db8d147336ee13ff88e766c85b8bf0352e2fa87707
# entrypoint: python@test_schema_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_schema_loader
# meta_type: tool
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
    def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
        return {}


class TestSchemaLoader:
    """
    Canonical, context-agnostic test for SchemaLoader.
    All file paths are injected via fixtures, not hardcoded.
    This pattern supports both unit and integration tests.
    """

    def setup_method(self) -> None:
        self.loader = ConcreteSchemaLoader()

    def test_load_json_schema_success(self, json_schema_path: Path) -> None:
        """Test loading a valid JSON schema file."""
        result = self.loader.load_json_schema(json_schema_path)
        assert isinstance(result, SchemaModel)
        assert result.schema_uri is not None or result.title is not None

    def test_load_onex_yaml_missing(self) -> None:
        """Test loading a missing YAML file raises OmniBaseError."""
        path = Path("does_not_exist.yaml")
        with pytest.raises(OmniBaseError):
            self.loader.load_onex_yaml(path)

    def test_load_json_schema_missing(self) -> None:
        """Test loading a missing JSON file raises OmniBaseError."""
        path = Path("does_not_exist.json")
        with pytest.raises(OmniBaseError):
            self.loader.load_json_schema(path)

    def test_discover_schemas_finds_all(self) -> None:
        """Test that discover_schemas finds all expected schemas in the directory."""
        schemas_dir = Path("src/omnibase/schemas")
        found = self.loader.discover_schemas(schemas_dir)
        assert any(f.name == "onex_node.yaml" for f in found)
        assert any(f.name == "state_contract.json" for f in found)

    def test_discover_schemas_skips_malformed(self, tmp_path: Path) -> None:
        """Test that discover_schemas skips malformed schema files."""
        # Create a valid and a malformed schema file
        valid_yaml = tmp_path / "valid.yaml"
        valid_yaml.write_text("schema_version: '0.1.0'\nname: test\n")
        malformed_yaml = tmp_path / "malformed.yaml"
        malformed_yaml.write_text(": this is not valid yaml ::::\n")
        found = self.loader.discover_schemas(tmp_path)
        assert valid_yaml in found
        assert malformed_yaml not in found

    def test_load_onex_yaml_from_schema_example(self, tmp_path: Path) -> None:
        """Test loading ONEX YAML from a schema example."""
        schema_path = Path("src/omnibase/schemas/onex_node.yaml")
        example = extract_example_from_schema(schema_path, 0)
        node_path = tmp_path / "node.onex.yaml"
        import yaml as _yaml

        node_path.write_text(_yaml.dump(example))
        result = self.loader.load_onex_yaml(node_path)
        assert isinstance(result, NodeMetadataBlock)
        # Optionally: compare_model_to_dict(result, example)
