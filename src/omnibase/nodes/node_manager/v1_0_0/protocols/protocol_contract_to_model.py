"""
Protocol for contract-to-model tool for node_manager node.
Defines the interface for generating Pydantic models from contract definitions.
"""
from typing import Protocol
from ..models import ModelContractSource, ModelGeneratedModels

class ProtocolContractToModel(Protocol):
    """
    Protocol for contract-to-model tool for node_manager node.
    Implementations should provide a method for generating Pydantic model code from a contract source model.
    """
    def generate_models_from_contract(self, contract: ModelContractSource) -> ModelGeneratedModels:
        """
        Generate Pydantic model code from a contract definition.
        Args:
            contract (ModelContractSource): The contract source model (dict or file path).
        Returns:
            ModelGeneratedModels: Mapping of model names to generated code strings.
        """
        ... 