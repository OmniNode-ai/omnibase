from typing import Protocol
from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode

class ProtocolCliNodeParity(Protocol):
    def validate_cli_node_parity(self, node: ModelDiscoveredNode) -> EnumValidationResult: ... 