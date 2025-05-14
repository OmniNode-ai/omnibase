# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_dependency_hygiene_validator"
# namespace: "omninode.tools.test_validate_dependency_hygiene_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_validate_dependency_hygiene_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from pathlib import Path

from foundation.script.validation.validate_dependency_hygiene import (
    DependencyHygieneValidator,
)


def make_pyproject(path: Path, deps=None):
    deps = deps or {"requests": "^2.0.0"}
    content = """
[tool.poetry]
name = "sample"
version = "0.1.0"
description = "Sample project"
authors = ["Test <test@example.com>"]

[tool.poetry.dependencies]
python = ">=3.8,<4.0"
"""
    for dep, ver in deps.items():
        content += f'{dep} = "{ver}"\n'
    (path / "pyproject.toml").write_text(content)


def test_valid_dependency_usage(tmp_path):
    make_pyproject(tmp_path, {"requests": "^2.0.0"})
    (tmp_path / "main.py").write_text("import requests\n")
    validator = DependencyHygieneValidator()
    result = validator.validate(tmp_path)
    assert result.is_valid
    assert not result.errors
    assert not result.warnings


def test_unused_dependency_warning(tmp_path):
    make_pyproject(tmp_path, {"requests": "^2.0.0"})
    (tmp_path / "main.py").write_text("print('hello')\n")
    validator = DependencyHygieneValidator()
    result = validator.validate(tmp_path)
    assert not result.is_valid
    assert any("not imported anywhere" in w.message for w in result.warnings) or any(
        "not imported anywhere" in e.message for e in result.errors
    )


def test_requirements_txt_error(tmp_path):
    make_pyproject(tmp_path, {"requests": "^2.0.0"})
    (tmp_path / "main.py").write_text("import requests\n")
    (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
    validator = DependencyHygieneValidator()
    result = validator.validate(tmp_path)
    assert not result.is_valid
    assert any("requirements.txt is present" in e.message for e in result.errors)


def test_missing_pyproject_toml(tmp_path):
    (tmp_path / "main.py").write_text("import requests\n")
    validator = DependencyHygieneValidator()
    result = validator.validate(tmp_path)
    assert not result.is_valid
    assert any("pyproject.toml not found" in e.message for e in result.errors)


def test_unused_dependency_error_severity(tmp_path):
    make_pyproject(tmp_path, {"requests": "^2.0.0"})
    (tmp_path / "main.py").write_text("print('no import')\n")
    validator = DependencyHygieneValidator({"severity": "error"})
    result = validator.validate(tmp_path)
    assert not result.is_valid
    assert any("not imported anywhere" in e.message for e in result.errors)
    assert not result.warnings