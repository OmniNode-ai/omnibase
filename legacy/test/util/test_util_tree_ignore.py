# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_util_tree_ignore"
# namespace: "foundation.test.util"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "foundation-team"
# entrypoint: "test_util_tree_ignore.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolTestCase"]
# base_class: ["ProtocolTestCase"]
# mock_safe: true
# === /OmniNode:Metadata ===

import pytest
from foundation.util.util_tree_ignore import UtilTreeIgnore
from foundation.model.model_tree_ignore import TreeIgnoreModel
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from pydantic import ValidationError


def test_load_tree_ignore_valid_yaml() -> None:
    """
    Test loading a valid .treeignore YAML file using the registry.
    """
    path = TEST_CASE_REGISTRY.get_test_case("tree_ignore", "valid_tree_ignore_yaml", "valid")
    model = UtilTreeIgnore.load_tree_ignore(path)
    assert isinstance(model, TreeIgnoreModel)
    assert model.metadata_version == "0.1"
    assert len(model.patterns) >= 1


def test_load_tree_ignore_valid_json() -> None:
    """
    Test loading a valid .treeignore JSON file using the registry.
    """
    path = TEST_CASE_REGISTRY.get_test_case("tree_ignore", "valid_tree_ignore_json", "valid")
    model = UtilTreeIgnore.load_tree_ignore(path)
    assert isinstance(model, TreeIgnoreModel)
    assert model.metadata_version == "0.1"
    assert len(model.patterns) >= 1


def test_load_tree_ignore_invalid_missing_patterns() -> None:
    """
    Test loading an invalid .treeignore YAML file (missing patterns field).
    Should raise ValueError due to schema validation error.
    """
    path = TEST_CASE_REGISTRY.get_test_case("tree_ignore", "invalid_tree_ignore_missing_patterns", "invalid")
    with pytest.raises(ValueError):
        UtilTreeIgnore.load_tree_ignore(path)


def test_load_tree_ignore_invalid_bad_format() -> None:
    """
    Test loading an invalid .treeignore JSON file (bad format: patterns is not a list).
    Should raise ValueError due to schema validation error.
    """
    path = TEST_CASE_REGISTRY.get_test_case("tree_ignore", "invalid_tree_ignore_bad_format", "invalid")
    with pytest.raises(ValueError):
        UtilTreeIgnore.load_tree_ignore(path) 