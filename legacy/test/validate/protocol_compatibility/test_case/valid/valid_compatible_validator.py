#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "valid_compatible_validator"
# namespace: "omninode.tools.valid_compatible_validator"
# meta_type: "model"
# version: "1.0.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "valid_compatible_validator.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['ProtocolValidate']'
# base_class:
#   - '['ProtocolValidate']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for a compatible validator.
This validator is compatible with the current protocol version.
"""

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidateResultModel

class CompatibleValidator(ProtocolValidate):
    """A validator that is compatible with the current protocol version."""
    
    def validate(self, *args, **kwargs) -> ValidateResultModel:
        """Validate the input."""
        return ValidateResultModel(is_valid=True)
    
    def get_name(self) -> str:
        """Get the name of the validator."""
        return "compatible_validator"
    
    @classmethod
    def metadata(cls):
        """Get the metadata for the validator."""
        return {
            "metadata_version": "0.1",
            "name": "compatible_validator",
            "namespace": "omninode.tools.valid_compatible_validator",
            "version": "1.0.0",
            "entrypoint": "valid_compatible_validator.py",
            "protocols_supported": ["O.N.E. v0.1"],
            "protocol_version": "0.1.0",
            "author": "OmniNode Team",
            "owner": "jonah@omninode.ai",
            "copyright": "Copyright (c) 2025 OmniNode.ai",
            "created_at": "2025-05-07T12:00:00+00:00",
            "last_modified_at": "2025-05-07T12:00:00+00:00",
            "description": "A validator that is compatible with the current protocol version.",
            "tags": ["test", "compatible"],
            "dependencies": [],
            "config": {}
        } 