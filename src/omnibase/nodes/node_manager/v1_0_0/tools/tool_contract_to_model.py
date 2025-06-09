from pathlib import Path
import yaml
from ..protocols.protocol_contract_to_model import ProtocolContractToModel
from ..models.model_contract_source import ModelContractSource
from ..models.model_generated_models import ModelGeneratedModels

class ToolContractToModel(ProtocolContractToModel):
    """
    Implements ProtocolContractToModel for generating Pydantic models from contract definitions.
    """
    def generate_models_from_contract(self, contract: ModelContractSource) -> ModelGeneratedModels:
        contract_dict = None
        if contract.contract is not None:
            # Assume contract.contract is a StateContractModel with a .dict() method
            contract_dict = contract.contract.dict()
        elif contract.contract_path is not None:
            with open(contract.contract_path, 'r') as f:
                contract_dict = yaml.safe_load(f)
        else:
            raise ValueError("Either contract or contract_path must be provided in ModelContractSource.")
        definitions = contract_dict.get('definitions', {})
        models = {}
        for model_name, schema in definitions.items():
            # Placeholder: generate a minimal Pydantic model for each definition
            code = f"class {model_name}(BaseModel):\n    pass\n"
            models[model_name] = code
        return ModelGeneratedModels(models=models, metadata=contract.metadata) 