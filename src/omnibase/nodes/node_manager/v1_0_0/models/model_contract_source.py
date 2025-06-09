from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
from omnibase.model.model_state_contract import StateContractModel
from .model_metadata import ModelMetadata

class ModelContractSource(BaseModel):
    """
    Canonical input model for contract-to-model generation tools.
    Provide either a contract (parsed StateContractModel) or a path to a contract file.
    Optionally include canonical metadata.
    """
    contract: Optional[StateContractModel] = Field(default=None, description="Parsed contract as a StateContractModel.")
    contract_path: Optional[Path] = Field(default=None, description="Path to the contract file.")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the contract source.")

    def get_contract(self) -> StateContractModel:
        """
        Returns the contract as a StateContractModel, loading from file if necessary.
        """
        if self.contract is not None:
            return self.contract
        if self.contract_path is not None:
            from omnibase.model.model_state_contract import load_state_contract_from_file
            return load_state_contract_from_file(str(self.contract_path))
        raise ValueError("Either contract or contract_path must be provided.") 