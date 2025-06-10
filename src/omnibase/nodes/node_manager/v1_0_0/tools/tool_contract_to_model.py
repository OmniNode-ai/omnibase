from pathlib import Path
import yaml
from ..protocols.protocol_contract_to_model import ProtocolContractToModel
from ..models.model_contract_source import ModelContractSource
from ..models.model_generated_models import ModelGeneratedModels
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum

class ToolContractToModel(ProtocolContractToModel):
    """
    Implements ProtocolContractToModel for generating Pydantic models from contract definitions.
    """
    def generate_models_from_contract(self, contract: ModelContractSource) -> ModelGeneratedModels:
        contract_dict = None
        contract_path = contract.contract_path if contract.contract_path is not None else "<in-memory>"
        if contract.contract is not None:
            # Assume contract.contract is a StateContractModel with a .dict() method
            contract_dict = contract.contract.dict()
        elif contract.contract_path is not None:
            with open(contract.contract_path, 'r') as f:
                contract_dict = yaml.safe_load(f)
        else:
            raise ValueError("Either contract or contract_path must be provided in ModelContractSource.")
        definitions = contract_dict.get('definitions', {})
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[ToolContractToModel] Loaded contract from {contract_path}. Definition keys: {list(definitions.keys())}",
            context={"contract_path": str(contract_path), "definition_keys": list(definitions.keys())}
        )
        print(f"[DEBUG] ToolContractToModel: Loaded contract from {contract_path}. Definition keys: {list(definitions.keys())}")
        models = {}
        for model_name, schema in definitions.items():
            # Placeholder: generate a minimal Pydantic model for each definition
            code = f"class {model_name}(BaseModel):\n    pass\n"
            models[model_name] = code
        return ModelGeneratedModels(models=models, metadata=contract.metadata) 