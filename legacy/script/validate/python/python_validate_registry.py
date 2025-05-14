#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_registry"
# namespace: "omninode.tools.python_validate_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T12:00:00+00:00"
# last_modified_at: "2025-05-07T12:00:00+00:00"
# entrypoint: "python_validate_registry.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['ProtocolValidate']'
# base_class:
#   - '['ProtocolValidate']'
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Registry for Python validators.

This module handles registration of all Python validators to avoid circular imports.
"""

from foundation.script.validate.validate_registry import validate_registry

def register_python_validators():
    """Register all Python validators."""
    # Import validators here to avoid circular imports
    from foundation.script.validate.python.python_validate_metadata_block import PythonValidateMetadataBlock
    from foundation.script.validate.python.python_validate_bootstrap_import import BootstrapImportValidator
    from foundation.script.validate.python.python_validate_chunk import PythonValidateChunk
    from foundation.script.validate.python.python_validate_protocol_compatibility import PythonValidateProtocolCompatibility

    # Register metadata block validator
    validate_registry.register(
        name=PythonValidateMetadataBlock.metadata().name,
        validator_cls=PythonValidateMetadataBlock,
        meta=PythonValidateMetadataBlock.metadata(),
    )

    # Register bootstrap import validator
    validate_registry.register(
        name=BootstrapImportValidator.metadata().name,
        validator_cls=BootstrapImportValidator,
        meta=BootstrapImportValidator.metadata(),
    )

    # Register chunk validator
    validate_registry.register(
        name=PythonValidateChunk.metadata().name,
        validator_cls=PythonValidateChunk,
        meta=PythonValidateChunk.metadata(),
    )

    # Register protocol compatibility validator
    validate_registry.register(
        name=PythonValidateProtocolCompatibility.metadata().name,
        validator_cls=PythonValidateProtocolCompatibility,
        meta=PythonValidateProtocolCompatibility.metadata(),
    )
