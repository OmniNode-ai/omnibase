#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_validate_bootstrap_import"
# namespace: "omninode.tools.test_python_validate_bootstrap_import"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "test_python_validate_bootstrap_import.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Test cases for the bootstrap import validator.
"""

import pytest
from pathlib import Path
from foundation.script.validate.python.python_validate_bootstrap_import import BootstrapImportValidator
from foundation.model.model_unified_result import UnifiedStatus, UnifiedMessageModel
import sys

@pytest.fixture
def validator():
    """Create a validator instance."""
    return BootstrapImportValidator()

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path

def test_validate_non_existent_file(validator):
    """Test validation of a non-existent file."""
    result = validator.validate(Path("non_existent.py"))
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_non_python_file(validator, temp_dir):
    """Test validation of a non-Python file."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("This is not Python code")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_non_entrypoint(validator, temp_dir):
    """Test validation of a Python file that is not an entrypoint."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
def some_function():
    pass
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_entrypoint_without_bootstrap(validator, temp_dir):
    """Test validation of an entrypoint without bootstrap import or call."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
if __name__ == "__main__":
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.error
    assert len(result.messages) == 2
    assert any(msg.summary == "Missing bootstrap import" for msg in result.messages)
    assert any(msg.summary == "Missing bootstrap call" for msg in result.messages)

def test_validate_entrypoint_with_import_only(validator, temp_dir):
    """Test validation of an entrypoint with only bootstrap import."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
from foundation.bootstrap.bootstrap import bootstrap

if __name__ == "__main__":
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.error
    assert len(result.messages) == 1
    assert result.messages[0].summary == "Missing bootstrap call"

def test_validate_entrypoint_with_call_only(validator, temp_dir):
    """Test validation of an entrypoint with only bootstrap call."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
if __name__ == "__main__":
    bootstrap()
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.error
    assert len(result.messages) == 1
    assert result.messages[0].summary == "Missing bootstrap import"

def test_validate_valid_entrypoint(validator, temp_dir):
    """Test validation of a valid entrypoint with both import and call."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
from foundation.bootstrap.bootstrap import bootstrap

if __name__ == "__main__":
    bootstrap()
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_entrypoint_with_alternative_import(validator, temp_dir):
    """Test validation of an entrypoint with alternative import syntax."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
import foundation.bootstrap.bootstrap

if __name__ == "__main__":
    foundation.bootstrap.bootstrap.bootstrap()
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_entrypoint_with_comments(validator, temp_dir):
    """Test validation of an entrypoint with comments and whitespace."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
# This is a comment
from foundation.bootstrap.bootstrap import bootstrap  # Import bootstrap

if __name__ == "__main__":  # Entrypoint check
    # Call bootstrap
    bootstrap()
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_entrypoint_with_multiple_imports(validator, temp_dir):
    """Test validation of an entrypoint with multiple imports."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
import os
import sys
from foundation.bootstrap.bootstrap import bootstrap
from pathlib import Path

if __name__ == "__main__":
    bootstrap()
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_validate_entrypoint_with_nested_imports(validator, temp_dir):
    """Test validation of an entrypoint with nested imports."""
    file_path = temp_dir / "test.py"
    file_path.write_text("""
try:
    from foundation.bootstrap.bootstrap import bootstrap
except ImportError:
    from foundation.bootstrap import bootstrap

if __name__ == "__main__":
    bootstrap()
    print("Hello, world!")
""")
    result = validator.validate(file_path)
    assert result.status == UnifiedStatus.success
    assert not result.messages

def test_main_no_args(monkeypatch, capsys):
    """Test main() with no arguments."""
    monkeypatch.setattr(sys, 'argv', ['python_validate_bootstrap_import.py'])
    validator = BootstrapImportValidator()
    assert validator.main() == 1
    captured = capsys.readouterr()
    assert "Usage: python_validate_bootstrap_import.py <file>" in captured.out

def test_main_nonexistent_file(monkeypatch, capsys):
    """Test main() with a nonexistent file."""
    monkeypatch.setattr(sys, 'argv', ['python_validate_bootstrap_import.py', 'nonexistent.py'])
    validator = BootstrapImportValidator()
    assert validator.main() == 1
    captured = capsys.readouterr()
    assert "Bootstrap import validation FAILED: File nonexistent.py does not exist" in captured.out

def test_main_valid_file(monkeypatch, capsys, tmp_path):
    """Test main() with a valid file that has proper bootstrap import and call."""
    test_file = tmp_path / "test_entrypoint.py"
    test_file.write_text('''
from foundation.bootstrap.bootstrap import bootstrap

def main():
    print("Hello world")

if __name__ == "__main__":
    bootstrap()
    main()
''')
    monkeypatch.setattr(sys, 'argv', ['python_validate_bootstrap_import.py', str(test_file)])
    validator = BootstrapImportValidator()
    assert validator.main() == 0
    captured = capsys.readouterr()
    assert "Bootstrap import validation PASSED" in captured.out

def test_main_invalid_file(monkeypatch, capsys, tmp_path):
    """Test main() with a file missing bootstrap import and call."""
    test_file = tmp_path / "test_entrypoint.py"
    test_file.write_text('''
def main():
    print("Hello world")

if __name__ == "__main__":
    main()
''')
    monkeypatch.setattr(sys, 'argv', ['python_validate_bootstrap_import.py', str(test_file)])
    validator = BootstrapImportValidator()
    assert validator.main() == 1
    captured = capsys.readouterr()
    assert "Bootstrap import validation FAILED" in captured.out
    assert "Missing bootstrap import" in captured.out
    assert "Missing bootstrap call" in captured.out 