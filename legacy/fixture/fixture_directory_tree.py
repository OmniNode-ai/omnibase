# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_fixture_directory_tree"
# namespace: "omninode.tools.test_fixture_directory_tree"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00Z"
# last_modified_at: "2025-05-07T12:00:00Z"
# entrypoint: "test_fixture_directory_tree.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture', 'ProtocolValidateFixture']
# base_class: ['BaseTestFixture', 'ProtocolValidateFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Directory tree validator fixture for tests.
Fixtures are registry-registered, DI-compliant, and use templates/schemas for file content.
"""

import tempfile
from pathlib import Path
from typing import Any, Generator

from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.script.validate.validate_registry import register_fixture
from foundation.script.validate.validate_directory_tree import ValidateDirectoryTree

from foundation.fixture import BaseTestFixture


class DirectoryTreeValidatorFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for the directory tree validator."""

    def get_fixture(self) -> ValidateDirectoryTree:
        """Get the directory tree validator fixture.
        
        Returns:
            ValidateDirectoryTree: The directory tree validator instance.
        """
        return ValidateDirectoryTree()


# Register the fixture
register_fixture(
    name="directory_tree_validator_fixture",
    fixture=DirectoryTreeValidatorFixture,
    description="Directory tree validator fixture for tests",
) 