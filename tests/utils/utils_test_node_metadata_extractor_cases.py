# Canonical test case definitions for utils node metadata extractor tests
# All field references must use the NodeMetadataField Enum for type safety and maintainability.
# The Enum must be kept in sync with the NodeMetadataBlock model.

from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.utils.utils_node_metadata_extractor import (
    load_node_metadata_from_dict,
    load_node_metadata_from_yaml,
    load_node_metadata_from_json,
)
from omnibase.core.errors import OmniBaseError
import pytest
import tempfile
import yaml
import json
from pathlib import Path

UTILS_NODE_METADATA_EXTRACTOR_CASES = {}

def register_utils_node_metadata_extractor_case(name):
    def decorator(cls):
        UTILS_NODE_METADATA_EXTRACTOR_CASES[name] = cls
        return cls
    return decorator

@register_utils_node_metadata_extractor_case("dict_success")
class DictSuccessCase:
    def run(self):
        data = {
            NodeMetadataField.NODE_ID.value: "test_node",
            NodeMetadataField.NODE_TYPE.value: "plugin",
            NodeMetadataField.VERSION_HASH.value: "v0.1.0",
            NodeMetadataField.ENTRY_POINT.value: {"type": "python", "path": "main.py"},
            NodeMetadataField.CONTRACT_TYPE.value: "io_schema",
            NodeMetadataField.CONTRACT.value: {"inputs": {"x": "int"}, "outputs": {"y": "str"}},
            NodeMetadataField.TAGS.value: [],
            NodeMetadataField.DEPENDENCIES.value: [],
            NodeMetadataField.CAPABILITIES.value: [],
            NodeMetadataField.X_EXTENSIONS.value: {},
        }
        result = load_node_metadata_from_dict(data)
        assert isinstance(result, NodeMetadataBlock)
        assert result.node_id == "test_node"

@register_utils_node_metadata_extractor_case("dict_invalid")
class DictInvalidCase:
    def run(self):
        with pytest.raises(OmniBaseError):
            load_node_metadata_from_dict({"not_a_field": 123})

@register_utils_node_metadata_extractor_case("yaml_success")
class YamlSuccessCase:
    def run(self):
        data = {
            NodeMetadataField.NODE_ID.value: "test_node",
            NodeMetadataField.NODE_TYPE.value: "plugin",
            NodeMetadataField.VERSION_HASH.value: "v0.1.0",
            NodeMetadataField.ENTRY_POINT.value: {"type": "python", "path": "main.py"},
            NodeMetadataField.CONTRACT_TYPE.value: "io_schema",
            NodeMetadataField.CONTRACT.value: {"inputs": {"x": "int"}, "outputs": {"y": "str"}},
            NodeMetadataField.TAGS.value: [],
            NodeMetadataField.DEPENDENCIES.value: [],
            NodeMetadataField.CAPABILITIES.value: [],
            NodeMetadataField.X_EXTENSIONS.value: {},
        }
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            fpath = Path(f.name)
        try:
            result = load_node_metadata_from_yaml(fpath)
            assert isinstance(result, NodeMetadataBlock)
            assert result.node_id == "test_node"
        finally:
            fpath.unlink()

@register_utils_node_metadata_extractor_case("yaml_invalid")
class YamlInvalidCase:
    def run(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(": not valid yaml :::\n")
            fpath = Path(f.name)
        try:
            with pytest.raises(OmniBaseError):
                load_node_metadata_from_yaml(fpath)
        finally:
            fpath.unlink()

@register_utils_node_metadata_extractor_case("json_success")
class JsonSuccessCase:
    def run(self):
        data = {
            NodeMetadataField.NODE_ID.value: "test_node",
            NodeMetadataField.NODE_TYPE.value: "plugin",
            NodeMetadataField.VERSION_HASH.value: "v0.1.0",
            NodeMetadataField.ENTRY_POINT.value: {"type": "python", "path": "main.py"},
            NodeMetadataField.CONTRACT_TYPE.value: "io_schema",
            NodeMetadataField.CONTRACT.value: {"inputs": {"x": "int"}, "outputs": {"y": "str"}},
            NodeMetadataField.TAGS.value: [],
            NodeMetadataField.DEPENDENCIES.value: [],
            NodeMetadataField.CAPABILITIES.value: [],
            NodeMetadataField.X_EXTENSIONS.value: {},
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            fpath = Path(f.name)
        try:
            result = load_node_metadata_from_json(fpath)
            assert isinstance(result, NodeMetadataBlock)
            assert result.node_id == "test_node"
        finally:
            fpath.unlink()

@register_utils_node_metadata_extractor_case("json_invalid")
class JsonInvalidCase:
    def run(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            fpath = Path(f.name)
        try:
            with pytest.raises(OmniBaseError):
                load_node_metadata_from_json(fpath)
        finally:
            fpath.unlink()

# Enum/model sync enforcement test
# This test ensures the NodeMetadataField Enum and NodeMetadataBlock model are always in sync.
def test_node_metadata_field_enum_matches_model():
    model_fields = set(NodeMetadataBlock.model_fields.keys())
    enum_fields = set(f.value for f in NodeMetadataField)
    assert model_fields == enum_fields, (
        f"Enum fields: {enum_fields}\nModel fields: {model_fields}\n"
        "NodeMetadataField Enum and NodeMetadataBlock model are out of sync!"
    ) 