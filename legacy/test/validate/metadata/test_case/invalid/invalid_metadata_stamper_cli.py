# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "invalid_metadata_stamper_cli"
# namespace: "omninode.tools.invalid_metadata_stamper_cli"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "invalid_metadata_stamper_cli.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for CLI functionality in metadata stamper.
This file is used to test that the metadata stamper properly handles CLI arguments and operations.
"""

from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA

class TestLogger:
    """Test logger implementing ProtocolLogger interface."""
    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass

    def debug(self, msg: str) -> None:
        pass

def get_logger():
    """Get a test logger instance."""
    return TestLogger()

def get_template_registry():
    """Get a template registry instance."""
    registry = MetadataRegistryTemplate()
    registry.register_template("py", MINIMAL_METADATA, ["py"])
    return registry

def get_test_file():
    """Get test file content."""
    return """
# Test file for CLI operations
def hello():
    print("Hello, world!")
"""

def get_invalid_args():
    """Get list of invalid CLI argument combinations."""
    return [
        [],  # No arguments
        ["--invalid-flag"],  # Invalid flag
        ["--template", "nonexistent"],  # Invalid template
        ["--overwrite", "--repair"],  # Conflicting flags
        ["--force-overwrite", "--repair"],  # Conflicting flags
        ["--template", "minimal", "--template", "extended"],  # Duplicate flag
    ] 