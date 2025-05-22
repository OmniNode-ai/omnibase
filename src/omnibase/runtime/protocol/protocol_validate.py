# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_validate.py
# version: 1.0.0
# uuid: '89e47b23-423d-4c18-9a4f-d89a33848962'
# author: OmniNode Team
# created_at: '2025-05-21T13:18:56.571144'
# last_modified_at: '2025-05-22T18:05:26.870449'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: protocol_validate.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_validate
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Any, List, Optional, Protocol

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.model.model_validate_error import (
    ValidateMessageModel,
    ValidateResultModel,
)
from omnibase.protocol.protocol_cli import ProtocolCLI


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

    def validate_main(self, args: Any) -> OnexResultModel: ...
    def validate(
        self, target: str, config: Optional[Any] = None
    ) -> ValidateResultModel: ...
    def get_name(self) -> str: ...

    def get_validation_errors(self) -> List[ValidateMessageModel]:
        """Get detailed validation errors from the last validation."""
        ...

    def discover_plugins(self) -> List["NodeMetadataBlock"]:
        """
        Returns a list of plugin metadata blocks supported by this validator.
        Enables dynamic test/validator scaffolding and runtime plugin contract enforcement.
        Compliant with ONEX execution model and Cursor Rule.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        ...

    def validate_node(self, node: "NodeMetadataBlock") -> bool: ...
