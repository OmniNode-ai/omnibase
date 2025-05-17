# Canonical test case definitions for utils node metadata extractor tests
# All field references must use the NodeMetadataField Enum for type safety and maintainability.
# The Enum must be kept in sync with the NodeMetadataBlock model.

import json
import tempfile
from pathlib import Path
from typing import Any, Callable

import pytest
import yaml

from omnibase.core.errors import OmniBaseError  # type: ignore[import-untyped]
from omnibase.model.model_enum_metadata import (
    NodeMetadataField,  # type: ignore[import-untyped]
)
from omnibase.model.model_node_metadata import (
    NodeMetadataBlock,  # type: ignore[import-untyped]
)
from omnibase.utils.utils_node_metadata_extractor import (
    load_node_metadata_from_dict,  # type: ignore[import-untyped]
)
from omnibase.utils.utils_node_metadata_extractor import (
    load_node_metadata_from_json,  # type: ignore[import-untyped]
)
from omnibase.utils.utils_node_metadata_extractor import (
    load_node_metadata_from_yaml,  # type: ignore[import-untyped]
)

UTILS_NODE_METADATA_EXTRACTOR_CASES: dict[str, type] = {}


def register_utils_node_metadata_extractor_case(name: str) -> Callable[[type], type]:
    """Decorator to register a test case class in the node metadata extractor registry."""

    def decorator(cls: type) -> type:
        UTILS_NODE_METADATA_EXTRACTOR_CASES[name] = cls
        return cls

    return decorator


@register_utils_node_metadata_extractor_case("dict_success")
class DictSuccessCase:
    def run(self, context: Any) -> None:
        data = {
            "schema_version": "1.0.0",
            "name": "test_node",
            "version": "1.0.0",
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "author": "test_author",
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified_at": "2024-01-02T00:00:00Z",
            "description": "A test node for extractor tests.",
            "state_contract": "onex.contracts.state.v1",
            "lifecycle": "active",
            "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "entrypoint": {"type": "python", "target": "main.py"},
            "namespace": "onex.test_node",
            "meta_type": "plugin",
            "tags": ["test", "extractor"],
            "trust_score_stub": {"runs": 1, "failures": 0},
            "x_extensions": {},
            "protocols_supported": ["v1"],
            "base_class": [],
            "dependencies": [],
            "environment": [],
            "license": "MIT",
        }
        result = load_node_metadata_from_dict(data)
        assert isinstance(result, NodeMetadataBlock)
        assert result.name == "test_node"


@register_utils_node_metadata_extractor_case("dict_invalid")
class DictInvalidCase:
    def run(self, context: Any) -> None:
        with pytest.raises(OmniBaseError):
            load_node_metadata_from_dict({"not_a_field": 123})


@register_utils_node_metadata_extractor_case("yaml_success")
class YamlSuccessCase:
    def run(self, context: Any) -> None:
        data = {
            "schema_version": "1.0.0",
            "name": "test_node",
            "version": "1.0.0",
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "author": "test_author",
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified_at": "2024-01-02T00:00:00Z",
            "description": "A test node for extractor tests.",
            "state_contract": "onex.contracts.state.v1",
            "lifecycle": "active",
            "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "entrypoint": {"type": "python", "target": "main.py"},
            "namespace": "onex.test_node",
            "meta_type": "plugin",
            "tags": ["test", "extractor"],
            "trust_score_stub": {"runs": 1, "failures": 0},
            "x_extensions": {},
            "protocols_supported": ["v1"],
            "base_class": [],
            "dependencies": [],
            "environment": [],
            "license": "MIT",
        }
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            fpath = Path(f.name)
        try:
            result = load_node_metadata_from_yaml(fpath)
            assert isinstance(result, NodeMetadataBlock)
            assert result.name == "test_node"
        finally:
            fpath.unlink()


@register_utils_node_metadata_extractor_case("yaml_invalid")
class YamlInvalidCase:
    def run(self, context: Any) -> None:
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
    def run(self, context: Any) -> None:
        data = {
            "schema_version": "1.0.0",
            "name": "test_node",
            "version": "1.0.0",
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "author": "test_author",
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified_at": "2024-01-02T00:00:00Z",
            "description": "A test node for extractor tests.",
            "state_contract": "onex.contracts.state.v1",
            "lifecycle": "active",
            "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "entrypoint": {"type": "python", "target": "main.py"},
            "namespace": "onex.test_node",
            "meta_type": "plugin",
            "tags": ["test", "extractor"],
            "trust_score_stub": {"runs": 1, "failures": 0},
            "x_extensions": {},
            "protocols_supported": ["v1"],
            "base_class": [],
            "dependencies": [],
            "environment": [],
            "license": "MIT",
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            fpath = Path(f.name)
        try:
            result = load_node_metadata_from_json(fpath)
            assert isinstance(result, NodeMetadataBlock)
            assert result.name == "test_node"
        finally:
            fpath.unlink()


@register_utils_node_metadata_extractor_case("json_invalid")
class JsonInvalidCase:
    def run(self, context: Any) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            fpath = Path(f.name)
        try:
            with pytest.raises(OmniBaseError):
                load_node_metadata_from_json(fpath)
        finally:
            fpath.unlink()


# This enforcement test is intentionally skipped until the full implementation is ready.
# See project standards for stub/test enforcement.
@pytest.mark.skip(reason="Stub: not yet implemented")
def test_node_metadata_field_enum_matches_model() -> None:
    model_fields = set(NodeMetadataBlock.model_fields.keys())
    enum_fields = set(f.value for f in NodeMetadataField)
    assert model_fields == enum_fields, (
        f"Enum fields: {enum_fields}\nModel fields: {model_fields}\n"
        "NodeMetadataField Enum and NodeMetadataBlock model are out of sync!"
    )
