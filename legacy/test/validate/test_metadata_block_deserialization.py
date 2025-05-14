# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_block_deserialization"
# namespace: "omninode.tools.test_metadata_block_deserialization"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_metadata_block_deserialization.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import re
import yaml
import pytest
from pathlib import Path
from foundation.model.model_metadata import MetadataBlockModel
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.util.util_metadata_block_extractor_registry import get_extractor

# Use only YAML test case files from the registry for metadata_block
FILES_TO_CHECK = [
    Path(TEST_CASE_REGISTRY.get_test_case("metadata_block", case, group))
    for group in ("valid", "invalid")
    for case in TEST_CASE_REGISTRY.list_test_cases("metadata_block", group)
]

METADATA_START = "# === OmniNode:Metadata ==="
METADATA_END = "# === /OmniNode:Metadata ==="

def extract_metadata_block(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".py":
        language = "python"
    elif ext in (".yaml", ".yml"):
        language = "yaml"
    elif ext == ".md":
        language = "markdown"
    else:
        language = "python"  # fallback
    extractor = get_extractor(language)
    if extractor is None:
        print(f"[DEBUG] No extractor found for language: {language} (file: {file_path})")
        return ""
    with open(file_path, "r") as f:
        lines = f.readlines()
    block = extractor.extract_block(lines)
    print(f"[DEBUG] Extracted block from {file_path} (language={language}):\n{block}\n---END BLOCK---")
    return block or ""

# Build a list of (file_path, group) tuples for parameterization
FILES_AND_GROUPS = [
    (Path(TEST_CASE_REGISTRY.get_test_case("metadata_block", case, group)), group)
    for group in ("valid", "invalid")
    for case in TEST_CASE_REGISTRY.list_test_cases("metadata_block", group)
]

@pytest.mark.parametrize("file_path,group", FILES_AND_GROUPS)
def test_metadata_block_deserialization(file_path, group):
    yaml_block = extract_metadata_block(file_path)
    assert yaml_block.strip(), f"No metadata block found in {file_path}"
    if group == "valid":
        meta_dict = yaml.safe_load(yaml_block)
        try:
            MetadataBlockModel(**meta_dict)
        except Exception as e:
            pytest.fail(f"Valid metadata block in {file_path} failed to deserialize: {e}\nBlock: {yaml_block}")
    else:
        # For invalid cases, test passes if either YAML parsing or model instantiation fails
        try:
            meta_dict = yaml.safe_load(yaml_block)
            MetadataBlockModel(**meta_dict)
        except Exception:
            return  # Expected failure
        pytest.fail(f"Invalid metadata block in {file_path} unexpectedly deserialized successfully. Block: {yaml_block}") 