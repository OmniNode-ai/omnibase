# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_yaml_utils"
# namespace: "omninode.tools.test_yaml_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_yaml_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.script.validate.common.common_yaml_utils import YamlUtils

@pytest.fixture(autouse=True)
def register_yaml_utils(utility_registry):
    utility_registry.register('yaml_utils', YamlUtils())

def test_safe_yaml_load_valid(utility_registry):
    yaml_utils = utility_registry.get('yaml_utils')
    content = """
    foo: bar
    baz: 123
    """
    data, error = yaml_utils.safe_yaml_load(content)
    assert error is None
    assert data == {'foo': 'bar', 'baz': 123}

def test_safe_yaml_load_invalid(utility_registry):
    yaml_utils = utility_registry.get('yaml_utils')
    content = "foo: [unclosed"
    data, error = yaml_utils.safe_yaml_load(content)
    assert data is None
    assert error is not None

def test_safe_yaml_load_not_dict(utility_registry):
    yaml_utils = utility_registry.get('yaml_utils')
    content = "- item1\n- item2"
    data, error = yaml_utils.safe_yaml_load(content)
    assert data is None
    assert error == "YAML content is not a dictionary." 