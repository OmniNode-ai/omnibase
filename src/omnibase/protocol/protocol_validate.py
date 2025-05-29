# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.306553'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_validate.py
# hash: 60e5bb3c87daf52e0b9a34a0949c2a8e380bd3153790edcff6ab02e7e25701a5
# last_modified_at: '2025-05-29T11:50:12.228769+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_validate.py
# namespace: omnibase.protocol_validate
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: a79401fb-e7c9-4265-b352-dcb2e7c29717
# version: 1.0.0
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
