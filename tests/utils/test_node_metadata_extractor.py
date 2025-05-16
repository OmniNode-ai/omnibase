import pytest
from pathlib import Path
from omnibase.utils.utils_node_metadata_extractor import (
    load_node_metadata_from_dict,
    load_node_metadata_from_yaml,
    load_node_metadata_from_json,
)
from omnibase.model.model_node_metadata import NodeMetadataBlock
import tempfile
import yaml
import json
from tests.utils.utils_test_node_metadata_extractor_cases import UTILS_NODE_METADATA_EXTRACTOR_CASES

@pytest.fixture
def minimal_node_metadata_dict():
    return {
        "node_id": "test_node",
        "node_type": "plugin",
        "version_hash": "v0.1.0",
        "entry_point": {"type": "python", "path": "main.py"},
        "contract_type": "io_schema",
        "contract": {"inputs": {"x": "int"}, "outputs": {"y": "str"}},
        "tags": [],
        "dependencies": [],
        "capabilities": [],
        "x_extensions": {},
    }

def test_load_node_metadata_from_dict_success(minimal_node_metadata_dict):
    result = load_node_metadata_from_dict(minimal_node_metadata_dict)
    assert isinstance(result, NodeMetadataBlock)
    assert result.node_id == "test_node"

def test_load_node_metadata_from_dict_invalid():
    with pytest.raises(Exception):
        load_node_metadata_from_dict({"not_a_field": 123})

def test_load_node_metadata_from_yaml_success(minimal_node_metadata_dict):
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.dump(minimal_node_metadata_dict, f)
        fpath = Path(f.name)
    try:
        result = load_node_metadata_from_yaml(fpath)
        assert isinstance(result, NodeMetadataBlock)
        assert result.node_id == "test_node"
    finally:
        fpath.unlink()

def test_load_node_metadata_from_json_success(minimal_node_metadata_dict):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(minimal_node_metadata_dict, f)
        fpath = Path(f.name)
    try:
        result = load_node_metadata_from_json(fpath)
        assert isinstance(result, NodeMetadataBlock)
        assert result.node_id == "test_node"
    finally:
        fpath.unlink()

def test_load_node_metadata_from_yaml_invalid():
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(": not valid yaml :::\n")
        fpath = Path(f.name)
    try:
        with pytest.raises(Exception):
            load_node_metadata_from_yaml(fpath)
    finally:
        fpath.unlink()

def test_load_node_metadata_from_json_invalid():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write("not valid json")
        fpath = Path(f.name)
    try:
        with pytest.raises(Exception):
            load_node_metadata_from_json(fpath)
    finally:
        fpath.unlink()

@pytest.mark.parametrize("test_case", list(UTILS_NODE_METADATA_EXTRACTOR_CASES.values()), ids=list(UTILS_NODE_METADATA_EXTRACTOR_CASES.keys()))
def test_utils_node_metadata_extractor_cases(test_case):
    test_case().run() 