# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# name: "test_model_metadata"
# namespace: "omninode.tests.model_metadata"
# meta_type: "test"
# version: "0.1.0"
# owner: "foundation-team"
# === /OmniNode:Test_Metadata ===

import pytest
from foundation.model.model_metadata import MetadataBlockModel, StamperIgnoreModel
from pydantic import ValidationError

# --- MetadataBlockModel validator error branches ---
def test_metadata_version_invalid():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.2',
            name='valid_name',
            namespace='valid.namespace',
            version='0.1.0',
            entrypoint='main.py',
            protocols_supported=['O.N.E. v0.1'],
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

def test_name_invalid():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.1',
            name='invalid name!',
            namespace='valid.namespace',
            version='0.1.0',
            entrypoint='main.py',
            protocols_supported=['O.N.E. v0.1'],
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

def test_namespace_invalid():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.1',
            name='valid_name',
            namespace='invalid namespace!',
            version='0.1.0',
            entrypoint='main.py',
            protocols_supported=['O.N.E. v0.1'],
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

def test_version_invalid():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.1',
            name='valid_name',
            namespace='valid.namespace',
            version='1.0',
            entrypoint='main.py',
            protocols_supported=['O.N.E. v0.1'],
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

def test_entrypoint_invalid():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.1',
            name='valid_name',
            namespace='valid.namespace',
            version='0.1.0',
            entrypoint='main.txt',
            protocols_supported=['O.N.E. v0.1'],
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

def test_protocols_supported_invalid_type():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.1',
            name='valid_name',
            namespace='valid.namespace',
            version='0.1.0',
            entrypoint='main.py',
            protocols_supported=123,
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

def test_protocols_supported_malformed_string():
    with pytest.raises(ValidationError):
        MetadataBlockModel(
            metadata_version='0.1',
            name='valid_name',
            namespace='valid.namespace',
            version='0.1.0',
            entrypoint='main.py',
            protocols_supported="not_a_list",
            author='a', owner='b', copyright='c', created_at='d', last_modified_at='e'
        )

# --- StamperIgnoreModel coverage ---
def test_stamper_ignore_model_default():
    model = StamperIgnoreModel()
    assert isinstance(model.get_ignore_files(), list)
    assert model.get_ignore_files() == [
        "containers/foundation/src/foundation/template/metadata/metadata_template_blocks.py"
    ]

def test_stamper_ignore_model_custom():
    files = ["foo.py", "bar.py"]
    model = StamperIgnoreModel(ignore_files=files)
    assert model.get_ignore_files() == files 