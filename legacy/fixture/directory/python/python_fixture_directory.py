# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_directory"
# namespace: "omninode.tools.test_python_fixture_directory"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:25+00:00"
# last_modified_at: "2025-05-05T13:00:25+00:00"
# entrypoint: "test_python_fixture_directory.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture', 'ProtocolValidateFixture']
# base_class: ['BaseTestFixture', 'ProtocolValidateFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Shared directory fixture for validator tests.
Fixtures are registry-registered, DI-compliant, and use templates/schemas for file content.
"""

import tempfile
from pathlib import Path

from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture


class ValidContainerYamlFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for a valid container.yaml file structure."""

    def get_fixture(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        valid_yaml = temp_dir / "container.yaml"
        valid_yaml.write_text(
            """
name: valid-container
version: 1.0.0
maintainer: test@example.com
"""
        )
        return temp_dir


class InvalidContainerYamlFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for an invalid container.yaml file structure."""

    def get_fixture(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        invalid_yaml = temp_dir / "container.yaml"
        invalid_yaml.write_text(
            """
name:
version: not-a-version
"""
        )
        return temp_dir


class ValidEnvDirFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for a valid .env directory."""

    def get_fixture(self):
        temp_dir = Path(tempfile.mkdtemp())
        env_file = temp_dir / ".env"
        env_file.write_text(
            """
# Example .env file
PORT=8080
USERNAME=admin
PASSWORD=postgres
HOST=localhost
API_URL=https://omninode.ai
"""
        )
        return temp_dir


class InvalidEnvDirFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for an invalid .env directory."""

    def get_fixture(self):
        temp_dir = Path(tempfile.mkdtemp())
        env_file = temp_dir / ".env"
        env_file.write_text(
            """
PORT=12345
USERNAME=realuser
PASSWORD=supersecret
API_KEY=sk-1234567890abcdef
SECRET_TOKEN=abcdefg
HOST=malicious.com
"""
        )
        return temp_dir


class InvalidReadmeDirFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for a directory with an invalid README.md (missing sections, too short)."""

    def get_fixture(self):
        temp_dir = Path(tempfile.mkdtemp())
        readme = temp_dir / "README.md"
        readme.write_text("# Overview\nShort.")
        return temp_dir


class MissingEnvDirFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for a missing .env directory (nonexistent path)."""

    def get_fixture(self):
        return Path("/tmp/nonexistent_env_dir")


class ValidReadmeDirFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for a directory with a valid README.md (all required sections, sufficient length)."""

    def get_fixture(self):
        temp_dir = Path(tempfile.mkdtemp())
        readme = temp_dir / "README.md"
        content = """
# Overview
This project provides ..

# Installation
Instructions ..

# Usage
How to use ..

# API Reference
API details ..

# Contributing
Contribution guidelines ..

For more info, see [OmniNode](https://omninode.ai).
"""
        content += "\n" + ("Extra info. " * 10)
        readme.write_text(content)
        return temp_dir


class TmpPathDirectoryFixture(ProtocolValidateFixture):
    def __init__(self, tmp_path: Path):
        self._tmp_path = tmp_path

    def get_fixture(self) -> Path:
        return self._tmp_path


# Register fixture in the registry
register_fixture(
    name="valid_container_yaml_fixture",
    fixture=ValidContainerYamlFixture,
    description="Fixture for a valid container.yaml file structure",
)
register_fixture(
    name="invalid_container_yaml_fixture",
    fixture=InvalidContainerYamlFixture,
    description="Fixture for an invalid container.yaml file structure",
)
register_fixture(
    name="valid_env_dir_fixture",
    fixture=ValidEnvDirFixture,
    description="Fixture for a valid .env directory",
)
register_fixture(
    name="invalid_env_dir_fixture",
    fixture=InvalidEnvDirFixture,
    description="Fixture for an invalid .env directory",
)
register_fixture(
    name="invalid_readme_dir_fixture",
    fixture=InvalidReadmeDirFixture,
    description="Fixture for a directory with an invalid README.md (missing sections, too short)",
)
register_fixture(
    name="missing_env_dir_fixture",
    fixture=MissingEnvDirFixture,
    description="Fixture for a missing .env directory (nonexistent path)",
)
register_fixture(
    name="valid_readme_dir_fixture",
    fixture=ValidReadmeDirFixture,
    description="Fixture for a directory with a valid README.md (all required sections, sufficient length)",
)