# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "invalid_metadata_stamper_missing_registry"
# namespace: "omninode.tools.invalid_metadata_stamper_missing_registry"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "invalid_metadata_stamper_missing_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for missing registry in metadata stamper.
This file is used to test that the metadata stamper properly handles missing template registry.
"""

from foundation.protocol.protocol_logger import ProtocolLogger

class TestLogger:
    """Concrete implementation of ProtocolLogger for testing."""
    def info(self, msg: str, *args, **kwargs) -> None:
        pass
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        pass
    
    def error(self, msg: str, *args, **kwargs) -> None:
        pass
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        pass

def get_logger():
    """Get a logger instance."""
    return TestLogger()

def get_template_registry():
    """Get a template registry instance."""
    return None  # Missing registry

def get_test_file():
    """Get test file content."""
    return """
# Test file
def hello():
    print("Hello, world!")
""" 