import tempfile
import os
from pathlib import Path
import pytest
from foundation.registry.registry_metadata_block_hash import RegistryMetadataBlockHash
from foundation.script.validate.validate_metadata_block_hash_registry import ValidateMetadataBlockHashRegistry
from foundation.model.model_unified_result import UnifiedStatus

@pytest.fixture
def temp_registry(tmp_path: Path) -> RegistryMetadataBlockHash:
    registry_path = tmp_path / ".metadata_block_hash_registry.yaml"
    return RegistryMetadataBlockHash(registry_path=registry_path)

@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    return tmp_path / "test.py"

def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")

METADATA_BLOCK = """# === OmniNode:Metadata ===\n# name: test\n# tree_hash: abc123\n# === /OmniNode:Metadata ===\n"""
METADATA_BLOCK_NO_HASH = """# === OmniNode:Metadata ===\n# name: test\n# === /OmniNode:Metadata ===\n"""
METADATA_BLOCK_INVALID_YAML = """# === OmniNode:Metadata ===\n# name: test\n# tree_hash: [unclosed\n# === /OmniNode:Metadata ===\n"""

def test_matching_hash(temp_file: Path, temp_registry: RegistryMetadataBlockHash) -> None:
    """Validator passes when block and registry hash match."""
    write_file(temp_file, METADATA_BLOCK)
    temp_registry.update(str(temp_file.resolve()), "abc123")
    validator = ValidateMetadataBlockHashRegistry(temp_registry)
    result = validator.validate(temp_file)
    assert result.status == UnifiedStatus.success
    assert not result.messages


def test_mismatched_hash(temp_file: Path, temp_registry: RegistryMetadataBlockHash) -> None:
    """Validator errors when block and registry hash do not match."""
    write_file(temp_file, METADATA_BLOCK.replace("abc123", "wrong"))
    temp_registry.update(str(temp_file.resolve()), "abc123")
    validator = ValidateMetadataBlockHashRegistry(temp_registry)
    result = validator.validate(temp_file)
    assert result.status == UnifiedStatus.error
    assert any("tree_hash mismatch" in m.summary for m in result.messages)


def test_missing_metadata_block(temp_file: Path, temp_registry: RegistryMetadataBlockHash) -> None:
    """Validator errors when no metadata block is present."""
    write_file(temp_file, "print('no metadata block')\n")
    temp_registry.update(str(temp_file.resolve()), "abc123")
    validator = ValidateMetadataBlockHashRegistry(temp_registry)
    result = validator.validate(temp_file)
    assert result.status == UnifiedStatus.error
    assert any("No metadata block found" in m.summary for m in result.messages)


def test_missing_tree_hash(temp_file: Path, temp_registry: RegistryMetadataBlockHash) -> None:
    """Validator errors when tree_hash is missing from block."""
    write_file(temp_file, METADATA_BLOCK_NO_HASH)
    temp_registry.update(str(temp_file.resolve()), "abc123")
    validator = ValidateMetadataBlockHashRegistry(temp_registry)
    result = validator.validate(temp_file)
    assert result.status == UnifiedStatus.error
    assert any("No tree_hash found" in m.summary for m in result.messages)


def test_missing_registry_entry(temp_file: Path, temp_registry: RegistryMetadataBlockHash) -> None:
    """Validator errors when registry has no entry for file."""
    write_file(temp_file, METADATA_BLOCK)
    validator = ValidateMetadataBlockHashRegistry(temp_registry)
    result = validator.validate(temp_file)
    assert result.status == UnifiedStatus.error
    assert any("No hash found in registry" in m.summary for m in result.messages)


def test_invalid_yaml_in_block(temp_file: Path, temp_registry: RegistryMetadataBlockHash) -> None:
    """Validator errors when metadata block YAML is invalid."""
    write_file(temp_file, METADATA_BLOCK_INVALID_YAML)
    temp_registry.update(str(temp_file.resolve()), "abc123")
    validator = ValidateMetadataBlockHashRegistry(temp_registry)
    result = validator.validate(temp_file)
    assert result.status == UnifiedStatus.error
    assert any("YAML parse error" in m.summary for m in result.messages) 