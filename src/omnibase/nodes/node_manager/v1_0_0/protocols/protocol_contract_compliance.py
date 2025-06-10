from typing import Protocol
from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode

class ProtocolContractCompliance(Protocol):
    def validate_contract_compliance(self, node: ModelDiscoveredNode) -> EnumValidationResult: ... 