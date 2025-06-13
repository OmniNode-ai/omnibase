"""
Protocol for contract-to-model generation tools.

Defines the interface for tools that generate Pydantic models from contract.yaml files.
"""

from pathlib import Path
from typing import Protocol


class ProtocolContractToModel(Protocol):
    """
    Protocol for contract-to-model generation tools.
    
    Defines the interface for generating Pydantic models, error codes, and introspection
    files from contract.yaml specifications.
    """

    def generate_state_models(
        self,
        contract_path: Path,
        output_path: Path,
        auto: bool = False
    ) -> None:
        """
        Generate Pydantic models for input/output state from a contract.yaml file.
        
        Args:
            contract_path: Path to the contract.yaml file
            output_path: Path to write the generated state.py file
            auto: Whether to auto-generate additional files
        """
        ...

    def generate_error_codes(
        self,
        contract_path: Path,
        output_path: Path
    ) -> None:
        """
        Generate error codes from contract.yaml file.
        
        Args:
            contract_path: Path to the contract.yaml file
            output_path: Path to write the generated error_codes.py file
        """
        ...

    def generate_introspection(
        self,
        contract_path: Path,
        output_path: Path
    ) -> None:
        """
        Generate introspection file from contract.yaml file.
        
        Args:
            contract_path: Path to the contract.yaml file
            output_path: Path to write the generated introspection.py file
        """
        ... 