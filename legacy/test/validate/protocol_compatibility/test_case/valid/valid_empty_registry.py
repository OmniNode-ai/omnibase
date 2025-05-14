#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "valid_empty_registry"
# namespace: "omninode.tools.valid_empty_registry"
# meta_type: "model"
# version: "1.0.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "valid_empty_registry.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['ProtocolValidate']'
# base_class:
#   - '['ProtocolValidate']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for an empty registry.
This test case verifies that the protocol compatibility validator
correctly handles an empty registry.
"""

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidateResultModel

class EmptyRegistryValidator(ProtocolValidate):
    """A validator that works with an empty registry."""
    
    def validate(self, *args, **kwargs) -> ValidateResultModel:
        """Validate the input."""
        return ValidateResultModel(is_valid=True)
    
    def get_name(self) -> str:
        """Get the name of the validator."""
        return "empty_registry_validator"
    
    @classmethod
    def metadata(cls):
        """Get the metadata for the validator."""
        return {
            "metadata_version": "0.1",
            "name": "empty_registry_validator",
            "namespace": "omninode.tools.valid_empty_registry",
            "version": "1.0.0",
            "entrypoint": "valid_empty_registry.py",
            "protocols_supported": ["O.N.E. v0.1"],
            "protocol_version": "0.1.0",
            "author": "OmniNode Team",
            "owner": "jonah@omninode.ai",
            "copyright": "Copyright (c) 2025 OmniNode.ai",
            "created_at": "2025-05-07T12:00:00+00:00",
            "last_modified_at": "2025-05-07T12:00:00+00:00",
            "description": "A validator that works with an empty registry.",
            "tags": ["test", "empty"],
            "dependencies": [],
            "config": {}
        } 