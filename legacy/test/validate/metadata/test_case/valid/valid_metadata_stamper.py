# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "valid_metadata_stamper"
# namespace: "omninode.tools.valid_metadata_stamper"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "valid_metadata_stamper.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for valid metadata stamper functionality.
This file is used to test that the metadata stamper properly handles valid cases.
"""

from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA

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
    registry = MetadataRegistryTemplate()
    registry.register_template("py", MINIMAL_METADATA, [".py"])
    return registry

def get_test_file():
    """Get test file content."""
    return """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test"
# namespace: "omninode.tools.test"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "test.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===

from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    value: int

def hello():
    print("Hello, world!")
""" 