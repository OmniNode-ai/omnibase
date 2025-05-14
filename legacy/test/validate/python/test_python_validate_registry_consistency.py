# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_validate_registry_consistency"
# namespace: "omninode.tools.test_python_validate_registry_consistency"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_python_validate_registry_consistency.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for RegistryConsistencyValidator using registry-based test cases.
Follows standards: DI, registry, type hints, docstrings, and metadata.
"""

from pathlib import Path
import pytest
from foundation.fixture.validator.python.python_fixture_registry_consistency import PythonTestFixtureRegistryConsistency
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedMessageModel, UnifiedStatus, UnifiedBatchResultModel

@pytest.fixture(scope="module")
def validator():
    # Use the DI/registry-compliant fixture
    return PythonTestFixtureRegistryConsistency().get_fixture()

def test_registry_consistency_valid(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "valid_registry_consistent", "valid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors
    assert not result.warnings

def test_registry_consistency_missing_metadata(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "invalid_registry_missing_metadata", "invalid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors

def test_registry_consistency_drift(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "invalid_registry_drift", "invalid")
    result = validator.validate(fname)
    assert not result.is_valid
    assert any("duplicate" in e.message.lower() or "drift" in e.message.lower() for e in result.errors)

def test_registry_consistency_yaml_parse_error(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "invalid_registry_consistency_bad", "invalid")
    result = validator.validate(fname)
    assert not result.is_valid
    assert any("parse yaml" in e.message.lower() for e in result.errors)

def test_registry_consistency_missing_name_field(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "invalid_registry_consistency_missing_name", "invalid")
    result = validator.validate(fname)
    assert not result.is_valid
    assert any("missing 'name'" in e.message.lower() for e in result.errors)

def test_registry_consistency_empty_registry(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "valid_registry_consistency_empty", "valid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors

def test_registry_consistency_extra_metadata_block(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "invalid_registry_consistency_extra", "invalid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors

def test_validator_skips_non_registry_file(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "valid_registry_consistency_not_a_registry", "valid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors

def test_validation_error_and_warning(validator):
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "invalid_registry_consistency_error_warning", "invalid")
    result = validator.validate(fname)
    assert not result.is_valid
    assert any("duplicate" in e.message.lower() for e in result.errors)

def test_registry_consistency_skips_non_yaml_file(validator):
    """Validator should skip non-YAML files (e.g., .py) and return valid with no errors."""
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "valid_registry_consistency_not_a_registry", "valid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors

def test_registry_consistency_entry_without_metadata_block(validator):
    """Validator should allow registry entries without a metadata block (optional)."""
    fname = TEST_CASE_REGISTRY.get_test_case("registry_consistency", "valid_registry_entry_without_metadata_block", "valid")
    result = validator.validate(fname)
    assert result.is_valid
    assert not result.errors

def test_cli_main_valid(monkeypatch, tmp_path):
    # Create a valid registry YAML file
    file = tmp_path / "valid_registry.yaml"
    file.write_text("""registry:\n  - name: test_entry\n""")
    import sys
    from foundation.script.validate.python import python_validate_registry_consistency as mod
    monkeypatch.setattr(sys, "argv", ["prog", str(file)])
    assert mod.PythonValidateRegistryConsistency().main([str(file)]) == 0

def test_cli_main_invalid(monkeypatch, tmp_path):
    # Create an invalid registry YAML file (duplicate entry)
    file = tmp_path / "invalid_registry.yaml"
    file.write_text("""registry:\n  - name: test_entry\n  - name: test_entry\n""")
    import sys
    from foundation.script.validate.python import python_validate_registry_consistency as mod
    monkeypatch.setattr(sys, "argv", ["prog", str(file)])
    assert mod.PythonValidateRegistryConsistency().main([str(file)]) == 1

def test_invalid_extension(tmp_path):
    file = tmp_path / "not_a_yaml.txt"
    file.write_text("not yaml")
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    result = PythonValidateRegistryConsistency().validate(file)
    assert result.status.name == "INVALID_EXTENSION"
    assert result.is_valid

def test_file_not_exist(tmp_path):
    file = tmp_path / "does_not_exist.yaml"
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    result = PythonValidateRegistryConsistency().validate(file)
    assert not result.is_valid
    assert any("does not exist" in e.message for e in result.errors)

def test_yaml_parse_error(tmp_path):
    file = tmp_path / "bad.yaml"
    file.write_text(": this is not valid yaml ::::\n")
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    result = PythonValidateRegistryConsistency().validate(file)
    assert not result.is_valid
    assert any("parse YAML" in e.message or "parse yaml" in e.message for e in result.errors)

def test_empty_yaml(tmp_path):
    file = tmp_path / "empty.yaml"
    file.write_text("")
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    result = PythonValidateRegistryConsistency().validate(file)
    assert result.status.name == "SKIPPED"
    assert result.is_valid

def test_non_dict_yaml(tmp_path):
    file = tmp_path / "list.yaml"
    file.write_text("- item1\n- item2\n")
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    result = PythonValidateRegistryConsistency().validate(file)
    assert result.status.name == "SKIPPED"
    assert result.is_valid

def test_missing_registry_key(tmp_path):
    file = tmp_path / "no_registry.yaml"
    file.write_text("foo: bar\n")
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    result = PythonValidateRegistryConsistency().validate(file)
    assert result.status.name == "SKIPPED"
    assert result.is_valid

def test_add_error_and_warning():
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    v = PythonValidateRegistryConsistency()
    v.add_error(message="err", file="f.yaml")
    v.add_warning(message="warn", file="f.yaml")
    assert v.errors and v.errors[0].message == "err"
    assert v.warnings and v.warnings[0].message == "warn"

def test_add_failed_file():
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    v = PythonValidateRegistryConsistency()
    v.add_failed_file("foo.yaml")
    assert "foo.yaml" in v.failed_files

def test_should_validate():
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    v = PythonValidateRegistryConsistency()
    from pathlib import Path
    assert v.should_validate(Path("foo.yaml"))
    assert v.should_validate(Path("foo.YML"))
    assert not v.should_validate(Path("foo.txt"))

def test_get_parser():
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    v = PythonValidateRegistryConsistency()
    parser = v.get_parser()
    assert hasattr(parser, "parse_args")

def test_validate_main(tmp_path):
    from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
    import argparse
    file = tmp_path / "valid_registry.yaml"
    file.write_text("registry:\n  - name: test_entry\n")
    v = PythonValidateRegistryConsistency()
    # Should return 0 for valid
    args = argparse.Namespace(target=str(file))
    assert v.validate_main(args) == 0
    # Should return 1 for invalid
    file2 = tmp_path / "invalid_registry.yaml"
    file2.write_text("registry:\n  - name: test_entry\n  - name: test_entry\n")
    args2 = argparse.Namespace(target=str(file2))
    assert v.validate_main(args2) == 1 