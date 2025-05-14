#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "invalid_multiple_versions"
# namespace: "omninode.tools.invalid_multiple_versions"
# meta_type: "model"
# version: "1.0.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "invalid_multiple_versions.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['ProtocolValidate']'
# base_class:
#   - '['ProtocolValidate']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Test case for multiple validator versions.
This test case verifies that the protocol compatibility validator
correctly handles multiple versions of a validator, including incompatible ones.
"""

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidateResultModel

class MultiVersionValidator(ProtocolValidate):
    """A validator with multiple versions."""
    
    def validate(self, *args, **kwargs) -> ValidateResultModel:
        """Validate the input."""
        return ValidateResultModel(is_valid=True)
    
    def get_name(self) -> str:
        """Get the name of the validator."""
        return "multi_version_validator"
    
    @classmethod
    def metadata(cls):
        """Get the metadata for the validator."""
        return {
            "metadata_version": "0.1",
            "name": "multi_version_validator",
            "namespace": "omninode.tools.invalid_multiple_versions",
            "version": "2.0.0",
            "entrypoint": "invalid_multiple_versions.py",
            "protocols_supported": ["O.N.E. v0.1"],
            "protocol_version": "1.0.0",  # Incompatible version
            "author": "OmniNode Team",
            "owner": "jonah@omninode.ai",
            "copyright": "Copyright (c) 2025 OmniNode.ai",
            "created_at": "2025-05-07T12:00:00+00:00",
            "last_modified_at": "2025-05-07T12:00:00+00:00",
            "description": "A validator with multiple versions, including incompatible ones.",
            "tags": ["test", "multiple_versions"],
            "dependencies": [],
            "config": {}
        } 