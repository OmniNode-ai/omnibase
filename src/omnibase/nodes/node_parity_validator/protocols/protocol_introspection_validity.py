from typing import Protocol
from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_parity_validator.v1_0_0.models.state import DiscoveredNode

class ProtocolIntrospectionValidity(Protocol):
    def validate_introspection_validity(self, node: DiscoveredNode) -> EnumValidationResult: ... 