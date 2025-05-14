import tempfile
import os
import pytest
from pathlib import Path
from foundation.registry.registry_metadata_block_hash import RegistryMetadataBlockHash

def test_registry_metadata_block_hash_basic(tmp_path: Path) -> None:
    """Test basic load, save, update, get, validate, and all methods."""
    registry_path = tmp_path / ".metadata_block_hash_registry.yaml"
    registry = RegistryMetadataBlockHash(registry_path=registry_path)

    # Initially empty
    assert registry.all() == {}
    assert registry.get("foo.py") is None
    assert not registry.validate("foo.py", "abc123")

    # Add an entry
    registry.update("foo.py", "abc123", committer="jonah")
    assert registry.get("foo.py") == "abc123"
    assert registry.validate("foo.py", "abc123")
    assert not registry.validate("foo.py", "wrong")
    all_hashes = registry.all()
    assert all_hashes == {"foo.py": "abc123"}

    # Add another entry
    registry.update("bar.py", "def456", committer="alice")
    assert registry.get("bar.py") == "def456"
    assert registry.validate("bar.py", "def456")
    all_hashes = registry.all()
    assert all_hashes == {"foo.py": "abc123", "bar.py": "def456"}

    # Save and reload
    registry.save()
    registry2 = RegistryMetadataBlockHash(registry_path=registry_path)
    assert registry2.get("foo.py") == "abc123"
    assert registry2.get("bar.py") == "def456"
    assert registry2.all() == {"foo.py": "abc123", "bar.py": "def456"}

    # Overwrite entry
    registry2.update("foo.py", "zzz999", committer="jonah")
    assert registry2.get("foo.py") == "zzz999"
    assert registry2.all()["foo.py"] == "zzz999"

    # Remove the file and reload (should be empty)
    os.remove(registry_path)
    registry3 = RegistryMetadataBlockHash(registry_path=registry_path)
    assert registry3.all() == {}


def test_registry_metadata_block_hash_edge_cases(tmp_path: Path) -> None:
    """Test edge cases: non-existent file, empty file, missing hash field."""
    registry_path = tmp_path / ".metadata_block_hash_registry.yaml"
    # Create an empty file
    registry_path.write_text("")
    registry = RegistryMetadataBlockHash(registry_path=registry_path)
    assert registry.all() == {}
    # Manually write invalid YAML
    registry_path.write_text("not: a: valid: yaml")
    registry = RegistryMetadataBlockHash(registry_path=registry_path)
    # Should not raise, but _data will be None or {}
    assert isinstance(registry.all(), dict) 