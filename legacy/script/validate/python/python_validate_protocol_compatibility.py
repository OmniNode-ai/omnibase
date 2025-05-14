#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: python_validate_protocol_compatibility
# namespace: omninode.tools.python_validate_protocol_compatibility
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:58+00:00
# last_modified_at: 2025-04-27T18:12:58+00:00
# entrypoint: python_validate_protocol_compatibility.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""python_validate_protocol_compatibility.py
containers.foundation.src.foundation.script.validate.python.python_validate_protocol_compatibility.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.script.validate.validate_registry import validate_registry
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedStatus, UnifiedMessageModel
from foundation.model.model_metadata import MetadataBlockModel

class PythonValidateProtocolCompatibility(ProtocolValidate):
    """
    Validator that ensures all validators are compatible with the current protocol version.
    """
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None, registry=None):
        super().__init__(config, logger)
        self.logger = logger or logging.getLogger(__name__)
        self.registry = registry if registry is not None else validate_registry

    @classmethod
    def metadata(cls) -> MetadataBlockModel:
        """Get metadata about this validator."""
        return MetadataBlockModel(
            metadata_version="0.1",
            name="protocol_compatibility",
            namespace="omninode.tools.python_validate_protocol_compatibility",
            version="1.0.0",
            entrypoint="python_validate_protocol_compatibility.py",
            protocols_supported=["O.N.E. v0.1"],
            protocol_version="0.1.0",
            author="OmniNode Team",
            owner="jonah@omninode.ai",
            copyright="Copyright (c) 2025 OmniNode.ai",
            created_at="2025-04-27T18:12:58+00:00",
            last_modified_at="2025-04-27T18:12:58+00:00",
            description="Validator for protocol compatibility.",
            tags=["protocol", "compatibility", "validator"],
            dependencies=[],
            config={}
        )

    def validate(self, data: Dict[str, Any]) -> UnifiedResultModel:
        """
        Validate that all registered validators are compatible with the current protocol version.
        """
        self.logger.info("Starting protocol compatibility validation")
        errors = []
        try:
            # Get all registered validators
            for name in self.registry.list_validators():
                versions = self.registry.get_validator_versions(name)
                for version in versions:
                    if not self.registry.check_version_compatibility(name, version):
                        errors.append(UnifiedMessageModel(
                            type="error",
                            summary=f"Validator {name} version {version} is incompatible with current protocol version",
                            file=str(data),
                            details=json.dumps({
                                "validator_name": name,
                                "validator_version": version,
                                "protocol_version": self.registry._current_protocol_version
                            }),
                            severity="error",
                            level="error",
                            context={"validator": "protocol_compatibility"}
                        ))
        except Exception as e:
            self.logger.error("Error during protocol compatibility validation", exc_info=True)
            return UnifiedResultModel(
                messages=[UnifiedMessageModel(
                    type="error",
                    summary=f"Error during protocol compatibility validation: {str(e)}",
                    file=str(data),
                    details=json.dumps({"exception": str(e)}),
                    severity="error",
                    level="error",
                    context={"validator": "protocol_compatibility"}
                )],
                status=UnifiedStatus.error
            )
        if errors:
            self.logger.error("Protocol compatibility validation failed")
            return UnifiedResultModel(
                messages=errors,
                status=UnifiedStatus.error
            )
        self.logger.info("Protocol compatibility validation passed")
        return UnifiedResultModel(
            messages=[],
            status=UnifiedStatus.success
        )

    def get_name(self) -> str:
        """Get the name of this validator."""
        return "protocol_compatibility" 