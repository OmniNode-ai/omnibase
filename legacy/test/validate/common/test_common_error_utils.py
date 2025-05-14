# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_common_error_utils"
# namespace: "omninode.tools.test_common_error_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_common_error_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.script.validate.common.common_error_utils import CommonErrorUtils
from foundation.model.model_validate_error import ValidateMessageModel

@pytest.fixture(autouse=True)
def register_common_error_utils(utility_registry):
    utility_registry.register('common_error_utils', CommonErrorUtils())

def test_add_error(utility_registry):
    utils = utility_registry.get('common_error_utils')
    messages = []
    utils.add_error(messages, message="err", file="f.py", line=1, details={"foo": "bar"})
    assert len(messages) == 1
    assert messages[0].message == "err"
    assert messages[0].file == "f.py"
    assert messages[0].line == 1
    assert messages[0].severity == "error"
    assert messages[0].context == {"foo": "bar"}

def test_add_warning(utility_registry):
    utils = utility_registry.get('common_error_utils')
    messages = []
    utils.add_warning(messages, message="warn", file="f.py", line=2, details={"bar": "baz"})
    assert len(messages) == 1
    assert messages[0].message == "warn"
    assert messages[0].file == "f.py"
    assert messages[0].line == 2
    assert messages[0].severity == "warning"
    assert messages[0].context == {"bar": "baz"}

def test_add_failed_file(utility_registry):
    utils = utility_registry.get('common_error_utils')
    failed_files = []
    utils.add_failed_file(failed_files, "foo.py")
    assert failed_files == ["foo.py"] 