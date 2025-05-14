#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_yaml_validator_registry"
# namespace: "omninode.tools.test_validate_yaml_validator_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_yaml_validator_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
test_yaml_validator_registry.py
containers.foundation.test.unit.validation.test_yaml_validator_registry

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import shutil
import tempfile
from pathlib import Path

import pytest
import yaml
from foundation.script.validate.python.python_validate_yaml_validator_registry import YamlValidatorRegistry

SCHEMA_EXAMPLE = {
    "metadata_version": "0.1",
    "name": "TestValidator",
    "namespace": "validators.test",
    "version": "1.0.0",
    "entrypoint": "validate_test",
    "protocols_supported": ["omninode_v1"],
    "owner": "test-team",
}

INVALID_SCHEMA = {
    # Missing required fields
    "name": "InvalidValidator"
}


@pytest.fixture
def temp_schema_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


def write_yaml(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)


def test_schema_discovery_and_loading(temp_schema_dir):
    # Write two valid schemas
    s1 = temp_schema_dir / "valid1.yaml"
    s2 = temp_schema_dir / "valid2.yml"
    write_yaml(s1, SCHEMA_EXAMPLE)
    write_yaml(s2, {**SCHEMA_EXAMPLE, "name": "TestValidator2"})
    # Write an invalid YAML file
    bad = temp_schema_dir / "bad.yaml"
    with open(bad, "w") as f:
        f.write(": this is not valid yaml ::::\n")
    # Write a schema missing metadata
    missing = temp_schema_dir / "missing.yaml"
    write_yaml(missing, INVALID_SCHEMA)
    # Run registry
    reg = YamlValidatorRegistry(schema_dir=temp_schema_dir)
    names = [s["name"] for s in reg.list_schemas()]
    assert "TestValidator" in names
    assert "TestValidator2" in names
    # Should not include invalid or missing-metadata schemas
    assert all(n != "InvalidValidator" for n in names)
    # Should not raise on bad YAML
    # Should print warnings/errors (not asserted here, but no crash)


def test_metadata_validation(temp_schema_dir):
    # Valid schema
    valid = temp_schema_dir / "valid.yaml"
    write_yaml(valid, SCHEMA_EXAMPLE)
    reg = YamlValidatorRegistry(schema_dir=temp_schema_dir)
    assert len(reg.list_schemas()) == 1
    # Invalid schema (missing owner)
    invalid = temp_schema_dir / "invalid.yaml"
    bad_meta = {**SCHEMA_EXAMPLE}
    del bad_meta["owner"]
    write_yaml(invalid, bad_meta)
    reg = YamlValidatorRegistry(schema_dir=temp_schema_dir)
    names = [s["name"] for s in reg.list_schemas()]
    assert "TestValidator" in names
    assert "InvalidValidator" not in names


# Additional tests for error handling, edge cases, etc. can be added as needed.