# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_extraction"
# namespace: "omninode.tools.test_metadata_extraction"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:28+00:00"
# last_modified_at: "2025-05-05T13:00:28+00:00"
# entrypoint: "test_metadata_extraction.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for extract_base_classes_from_file in metadata_block_utils.
Fixtures are injected via the fixture registry.
"""
import pytest
from foundation.script.metadata import metadata_block_utils as mbu
from foundation.fixture.fixture_test_fixtures import temp_py_file, temp_invalid_py_file, logger
from foundation.script.validate.common.common_file_utils import FileUtils
from foundation.script.validate.common.common_yaml_utils import YamlUtils
from foundation.script.validate.common.common_json_utils import safe_json_dumps
from foundation.script.validate.common.common_error_utils import CommonErrorUtils


def test_extract_base_classes_from_file_valid(fixture_registry):
    temp_py_file = next(fixture_registry.get_fixture("temp_py_file").get_fixture())
    logger = fixture_registry.get_fixture("logger").get_fixture()
    bases = mbu.extract_base_classes_from_file(str(temp_py_file), logger=logger)
    assert set(bases) == {"A", "B"}

def test_extract_base_classes_from_file_invalid(fixture_registry):
    temp_invalid_py_file = next(fixture_registry.get_fixture("temp_invalid_py_file").get_fixture())
    logger = fixture_registry.get_fixture("logger").get_fixture()
    bases = mbu.extract_base_classes_from_file(str(temp_invalid_py_file), logger=logger)
    assert bases == []

def test_extract_base_classes_from_file_nonexistent(fixture_registry):
    logger = fixture_registry.get_fixture("logger").get_fixture()
    bases = mbu.extract_base_classes_from_file("/tmp/does_not_exist.py", logger=logger)
    assert bases == []

@pytest.fixture
def utility_registry():
    class Registry(dict):
        def register(self, name, obj):
            self[name] = obj
        def get(self, name):
            return self[name]
    reg = Registry()
    reg.register('file_utils', FileUtils())
    reg.register('yaml_utils', YamlUtils())
    reg.register('json_utils', {'safe_json_dumps': safe_json_dumps})
    reg.register('common_error_utils', CommonErrorUtils())
    return reg 