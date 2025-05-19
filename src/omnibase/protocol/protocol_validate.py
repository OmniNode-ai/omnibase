# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: ac8b6177-f988-4bd0-84fd-bdfcd351b069
# name: protocol_validate.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.248176
# last_modified_at: 2025-05-19T16:19:55.248179
# description: Stamped Python file: protocol_validate.py
# state_contract: none
# lifecycle: active
# hash: d2d4f7e48d6bec9f07ebd8f7d78bdaae80cdc6193ac7e4fd2644e5ab6df020cf
# entrypoint: {'type': 'python', 'target': 'protocol_validate.py'}
# namespace: onex.stamped.protocol_validate.py
# meta_type: tool
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
