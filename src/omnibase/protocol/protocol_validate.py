# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_validate"
# namespace: "omninode.tools.protocol_validate"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:32+00:00"
# last_modified_at: "2025-05-05T13:00:32+00:00"
# entrypoint: "protocol_validate.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol', 'ProtocolCLI']
# base_class: ['Protocol', 'ProtocolCLI']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Any, Protocol, List
from src.omnibase.protocol.protocol_cli import ProtocolCLI
from src.omnibase.model.model_unified_result import OnexResultModel
from src.omnibase.model.model_validate_error import ValidateResultModel, ValidateMessageModel

class ProtocolValidate(ProtocolCLI, Protocol):
    """
    Protocol for validators that check ONEX node metadata conformance.

    Example:
        class MyValidator(ProtocolValidate):
            def validate(self, path: str) -> ValidateResultModel:
                ...
            def get_validation_errors(self) -> List[ValidateMessageModel]:
                ...
    """
    logger: Any  # structlog.BoundLogger recommended

    def validate_main(self, args) -> OnexResultModel: ...
    def validate(self, target, config=None) -> ValidateResultModel: ...
    def get_name(self) -> str: ...

    def get_validation_errors(self) -> List[ValidateMessageModel]:
        """Get detailed validation errors from the last validation."""
        ...