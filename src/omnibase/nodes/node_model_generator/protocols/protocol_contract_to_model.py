from typing import Dict, Protocol, Union
from pathlib import Path

class ProtocolContractToModel(Protocol):
    def generate_models_from_contract(self, contract: Union[dict, Path]) -> Dict[str, str]:
        """
        Generate Pydantic model code from a contract definition.
        Args:
            contract: The contract as a dict or a path to a YAML file.
        Returns:
            Dict mapping model names to generated Pydantic code strings.
        """
        ... 