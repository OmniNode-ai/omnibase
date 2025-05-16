# TODO: Implement full .tree validation tests in M1+.
# See docs/testing.md and milestone_0_checklist.md for requirements.

from pathlib import Path
import yaml
import pytest
import os
import jsonschema
import glob
import json

def test_tree_format_yaml_exists_and_is_valid():
    tree_path = Path("src/omnibase/schemas/tree_format.yaml")
    assert tree_path.exists(), "tree_format.yaml does not exist"
    # TODO: Extend with real structure/content validation in M1+
    with tree_path.open("r") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, (dict, list)), "tree_format.yaml must be a dict or list" 

"""
Canonical registry-driven, protocol-injected .tree schema validation tests with context parameterization.
- All test cases are registered via a central registry and decorator.
- Each test case is a class with a run() method, specifying the .tree file and expected outcome.
- Parameterized test runs over both context and registry, surfacing IDs in pytest output.
- Follows ONEX/OmniBase standards (see docs/testing.md).
Covers:
- Missing required fields (name, type, children)
- File node with children (invalid)
- Directory node missing children (invalid)
- Invalid type value
- Non-string name
- Non-list children
- Empty directory
- File node with metadata/mtime/size
- Deeply nested structure
- Root not directory
- Large number of children
- Context: mock (test data), integration (simulated real project)
"""

TREE_SCHEMA_PATH = Path("src/omnibase/schemas/tree_format.yaml")
VALID_TREE_DIR = Path("tests/validate/directory_tree/test_case/valid")
INVALID_TREE_DIR = Path("tests/validate/directory_tree/test_case/invalid")

TREE_TEST_CASES = {}

def register_tree_test_case(name):
    def decorator(cls):
        TREE_TEST_CASES[name] = cls
        return cls
    return decorator

@pytest.fixture(scope="module")
def tree_schema():
    with TREE_SCHEMA_PATH.open("r") as f:
        return yaml.safe_load(f)

@pytest.fixture(params=[
    pytest.param("mock", id="mock", marks=pytest.mark.mock),
    pytest.param("integration", id="integration", marks=pytest.mark.integration),
])
def context(request):
    return request.param

# --- Test Case Classes ---

# Valid cases
@register_tree_test_case("valid_basic")
class ValidBasicTree:
    path = VALID_TREE_DIR / "valid_basic.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("valid_empty_directory")
class ValidEmptyDirectoryTree:
    path = VALID_TREE_DIR / "valid_empty_directory.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("valid_file_with_metadata")
class ValidFileWithMetadataTree:
    path = VALID_TREE_DIR / "valid_file_with_metadata.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("valid_deeply_nested")
class ValidDeeplyNestedTree:
    path = VALID_TREE_DIR / "valid_deeply_nested.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("valid_large_number_of_children")
class ValidLargeNumberOfChildrenTree:
    path = VALID_TREE_DIR / "valid_large_number_of_children.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        jsonschema.validate(instance=data, schema=schema)

# Invalid cases
@register_tree_test_case("invalid_missing_type")
class InvalidMissingTypeTree:
    path = INVALID_TREE_DIR / "invalid_missing_type.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("invalid_file_with_children")
class InvalidFileWithChildrenTree:
    path = INVALID_TREE_DIR / "invalid_file_with_children.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("invalid_directory_missing_children")
class InvalidDirectoryMissingChildrenTree:
    path = INVALID_TREE_DIR / "invalid_directory_missing_children.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("invalid_type_value")
class InvalidTypeValueTree:
    path = INVALID_TREE_DIR / "invalid_type_value.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("invalid_nonstring_name")
class InvalidNonStringNameTree:
    path = INVALID_TREE_DIR / "invalid_nonstring_name.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("invalid_nonlist_children")
class InvalidNonListChildrenTree:
    path = INVALID_TREE_DIR / "invalid_nonlist_children.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_test_case("invalid_root_not_directory")
class InvalidRootNotDirectoryTree:
    path = INVALID_TREE_DIR / "invalid_root_not_directory.tree"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = yaml.safe_load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@pytest.mark.parametrize("context", ["mock", "integration"], ids=["mock", "integration"])
@pytest.mark.parametrize("test_case_cls", list(TREE_TEST_CASES.values()), ids=list(TREE_TEST_CASES.keys()))
def test_tree_cases(tree_schema, test_case_cls, context):
    test_case_cls().run(tree_schema, context)

# TODO: Replace stub_tree_structure with real .tree loader and add negative tests in M1+

valid_tree_files = list(VALID_TREE_DIR.glob("*.tree"))
invalid_tree_files = list(INVALID_TREE_DIR.glob("*.tree"))

@pytest.mark.parametrize("tree_file", valid_tree_files, ids=[f.name for f in valid_tree_files])
def test_valid_tree_files(tree_schema, tree_file):
    with tree_file.open("r") as f:
        data = yaml.safe_load(f)
    jsonschema.validate(instance=data, schema=tree_schema)

@pytest.mark.parametrize("tree_file", invalid_tree_files, ids=[f.name for f in invalid_tree_files])
def test_invalid_tree_files(tree_schema, tree_file):
    with tree_file.open("r") as f:
        data = yaml.safe_load(f)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=data, schema=tree_schema)

"""
Comprehensive .tree schema validation tests.
Covers:
- Missing required fields (name, type, children)
- File node with children (invalid)
- Directory node missing children (invalid)
- Invalid type value
- Non-string name
- Non-list children
- Empty directory
- File node with metadata/mtime/size
- Deeply nested structure
- Root not directory
- Large number of children
""" 

TREE_SCHEMA_JSON_PATH = Path("src/omnibase/schemas/tree_format.json")
VALID_TREE_JSON_PATH = Path("tests/validate/directory_tree/test_case/valid/valid_basic.tree.json")

@pytest.fixture(scope="module")
def tree_schema_json():
    with TREE_SCHEMA_JSON_PATH.open("r") as f:
        return json.load(f)

@pytest.mark.parametrize("context", ["mock", "integration"], ids=["mock", "integration"])
def test_valid_tree_json(tree_schema_json, context):
    with VALID_TREE_JSON_PATH.open("r") as f:
        data = json.load(f)
    import jsonschema
    jsonschema.validate(instance=data, schema=tree_schema_json) 

VALID_TREE_JSON_DIR = Path("tests/validate/directory_tree/test_case/valid")
INVALID_TREE_JSON_DIR = Path("tests/validate/directory_tree/test_case/invalid")

# Registry for JSON test cases
TREE_JSON_TEST_CASES = {}

def register_tree_json_test_case(name):
    def decorator(cls):
        TREE_JSON_TEST_CASES[name] = cls
        return cls
    return decorator

# Valid JSON case (mirrors valid_basic)
@register_tree_json_test_case("valid_basic_json")
class ValidBasicTreeJson:
    path = VALID_TREE_JSON_DIR / "valid_basic.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        jsonschema.validate(instance=data, schema=schema)

# TODO: Add more .tree.json files and cases as needed for full parity

# Invalid JSON cases
@register_tree_json_test_case("invalid_missing_type_json")
class InvalidMissingTypeTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_missing_type.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_json_test_case("invalid_file_with_children_json")
class InvalidFileWithChildrenTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_file_with_children.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_json_test_case("invalid_directory_missing_children_json")
class InvalidDirectoryMissingChildrenTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_directory_missing_children.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_json_test_case("invalid_type_value_json")
class InvalidTypeValueTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_type_value.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_json_test_case("invalid_nonstring_name_json")
class InvalidNonStringNameTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_nonstring_name.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_json_test_case("invalid_nonlist_children_json")
class InvalidNonListChildrenTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_nonlist_children.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@register_tree_json_test_case("invalid_root_not_directory_json")
class InvalidRootNotDirectoryTreeJson:
    path = INVALID_TREE_JSON_DIR / "invalid_root_not_directory.tree.json"
    def run(self, schema, context):
        with self.path.open("r") as f:
            data = json.load(f)
        import pytest
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

@pytest.mark.parametrize("context", ["mock", "integration"], ids=["mock", "integration"])
@pytest.mark.parametrize("test_case_cls", list(TREE_JSON_TEST_CASES.values()), ids=list(TREE_JSON_TEST_CASES.keys()))
def test_tree_json_cases(tree_schema_json, test_case_cls, context):
    test_case_cls().run(tree_schema_json, context) 
