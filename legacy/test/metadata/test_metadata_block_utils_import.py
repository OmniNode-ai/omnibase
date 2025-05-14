# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_block_utils_import"
# namespace: "omninode.tools.test_metadata_block_utils_import"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:28+00:00"
# last_modified_at: "2025-05-05T13:00:28+00:00"
# entrypoint: "test_metadata_block_utils_import.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.script.metadata import metadata_block_utils as mbu
from foundation.script.validate.python.python_validate_metadata_block import PythonValidateMetadataBlock
from foundation.script.validate.common.common_file_utils import FileUtils
from foundation.script.validate.common.common_yaml_utils import YamlUtils
from foundation.script.validate.common.common_json_utils import safe_json_dumps
from foundation.script.validate.common.common_error_utils import CommonErrorUtils

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

def test_direct_import_and_exercise(utility_registry):
    # Exercise a function from metadata_block_utils
    block = mbu.generate_metadata_block(
        name="test_tool",
        entrypoint="test_tool.py",
        template="minimal",
        logger=None,
    )
    assert "name: test_tool" in block
    # Instantiate PythonValidateMetadataBlock and check attribute
    validator = PythonValidateMetadataBlock(logger=None, utility_registry=utility_registry)
    assert hasattr(validator, "logger") 