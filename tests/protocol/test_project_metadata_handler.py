# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-29T06:01:49.538455'
# description: Stamped by PythonHandler
# entrypoint: python://test_project_metadata_handler.py
# hash: 5c3549e80df22ef98a8189395cf322bba633f524308fc1660883ba0fd08ab9ba
# last_modified_at: '2025-05-29T13:43:04.000561+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_project_metadata_handler.py
# namespace:
#   value: py://omnibase.tests.protocol.test_project_metadata_handler_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: c84822e9-43ea-4d28-aa39-b8a14c26fe5e
# version: 1.0.0
# === /OmniNode:Metadata ===


import pytest
from pathlib import Path
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.project_metadata_handler import ProjectMetadataHandler
from omnibase.model.model_project_metadata import ProjectMetadataBlock, get_canonical_versions
import yaml

canonical_versions = get_canonical_versions()

@pytest.fixture
def temp_project_metadata_file(tmp_path):
    file = tmp_path / "project.onex.yaml"
    data = {
        "author": "Test Author",
        "name": "omnibase",
        "namespace": "omnibase",
        "description": "Test project metadata",
        "metadata_version": "0.1.0",
        "protocol_version": "0.1.0",
        "schema_version": "0.1.0",
        "lifecycle": "active",
        "created_at": "2025-05-29T06:00:00Z",
        "last_modified_at": "2025-05-29T06:00:00Z",
        "license": "MIT",
        "entrypoint": "yaml://project.onex.yaml",
        "meta_type": "project",
        "tools": {},
        "copyright": "OmniNode.ai",
    }
    with open(file, "w") as f:
        yaml.safe_dump(data, f)
    return file

def test_can_handle(temp_project_metadata_file):
    handler = ProjectMetadataHandler()
    content = temp_project_metadata_file.read_text()
    assert handler.can_handle(temp_project_metadata_file, content)

def test_load(temp_project_metadata_file):
    handler = ProjectMetadataHandler()
    meta = handler.load(temp_project_metadata_file)
    assert isinstance(meta, ProjectMetadataBlock)
    assert meta.name == "omnibase"
    assert meta.metadata_version == canonical_versions["metadata_version"]
    assert meta.protocol_version == canonical_versions["protocol_version"]
    assert meta.schema_version == canonical_versions["schema_version"]

def test_stamp_updates_last_modified(temp_project_metadata_file):
    handler = ProjectMetadataHandler()
    content = temp_project_metadata_file.read_text()
    result = handler.stamp(temp_project_metadata_file, content, write=False)
    assert result.status.value == "success"
    assert result.messages[0].summary == "Project metadata stamped successfully"

def test_introspect(temp_project_metadata_file):
    handler = ProjectMetadataHandler()
    d = handler.introspect(temp_project_metadata_file)
    assert d["meta_type"] == "project"
    assert d["entrypoint"] == "yaml://project.onex.yaml"

def test_validate(temp_project_metadata_file):
    handler = ProjectMetadataHandler()
    content = temp_project_metadata_file.read_text()
    result = handler.validate(temp_project_metadata_file, content)
    assert result.status.value == "success"

# Negative test: missing required field
@pytest.fixture
def temp_invalid_project_metadata_file(tmp_path):
    file = tmp_path / "project.onex.yaml"
    data = {
        # Missing 'author'
        "name": "omnibase",
        "namespace": "omnibase",
        "metadata_version": "0.1.0",
        "protocol_version": "0.1.0",
        "schema_version": "0.1.0",
        "lifecycle": "active",
        "entrypoint": "yaml://project.onex.yaml",
        "meta_type": "project",
        "copyright": "OmniNode.ai",
    }
    with open(file, "w") as f:
        yaml.safe_dump(data, f)
    return file

def test_load_invalid_fails(temp_invalid_project_metadata_file):
    handler = ProjectMetadataHandler()
    with pytest.raises(Exception):
        handler.load(temp_invalid_project_metadata_file)
