# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "invalid_metadata_stamper_invalid_logger"
# namespace: "omninode.tools.invalid_metadata_stamper_invalid_logger"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "invalid_metadata_stamper_invalid_logger.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for invalid logger in metadata stamper.
This file is used to test that the metadata stamper properly handles invalid logger objects.
"""

from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA

# Invalid logger object (missing required methods)
class InvalidLogger:
    pass

def get_logger():
    """Get an invalid logger instance."""
    return InvalidLogger()

def get_template_registry():
    """Get a template registry instance."""
    registry = MetadataRegistryTemplate()
    registry.register_template("py", MINIMAL_METADATA, [".py"])
    return registry

def get_test_file():
    """Get test file content."""
    return """
# Test file
def hello():
    print("Hello, world!")
""" 