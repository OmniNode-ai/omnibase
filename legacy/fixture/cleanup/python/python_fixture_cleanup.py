# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_cleanup"
# namespace: "omninode.tools.test_python_fixture_cleanup"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:24+00:00"
# last_modified_at: "2025-05-05T13:00:24+00:00"
# entrypoint: "test_python_fixture_cleanup.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Shared cleanup/teardown fixture for validator tests.
Fixture is registry-registered, DI-compliant, and ensures cleanup of test artifacts.
"""

import shutil
from pathlib import Path

from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture


class CleanupFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for cleaning up test directories and files."""

    def get_fixture(self):
        def cleanup(path: Path):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

        return cleanup


# Register the cleanup fixture in the registry
register_fixture(
    name="cleanup_fixture",
    fixture=CleanupFixture,
    description="Fixture for cleaning up test directories and files",
)