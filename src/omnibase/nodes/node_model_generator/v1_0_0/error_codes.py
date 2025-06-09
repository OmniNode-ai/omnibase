# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: a447d830fe4859438e0b7fbb730572b10e57f9cc8bd1c03a50f9d5ef724b1dc1
# To regenerate: poetry run python src/omnibase/runtimes/onex_runtime/v1_0_0/codegen/contract_to_model.py --contract src/omnibase/nodes/node_model_generator/v1_0_0/contract.yaml --output-dir src/omnibase/nodes/node_model_generator/v1_0_0/models

from enum import Enum

class NodeModelGeneratorErrorCode(Enum):
    UNKNOWN_ERROR = 'UNKNOWN_ERROR'
    INVALID_PARAMETER = 'INVALID_PARAMETER'
    MISSING_REQUIRED_PARAMETER = 'MISSING_REQUIRED_PARAMETER'
    SCHEMA_VALIDATION_FAILED = 'SCHEMA_VALIDATION_FAILED'
    UNSUPPORTED_OPERATION = 'UNSUPPORTED_OPERATION'
