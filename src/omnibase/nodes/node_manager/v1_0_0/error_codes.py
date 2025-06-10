# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: 800e01a21508c6c2fcf41d1b0ab8d5cb1f9e3466f74a6817b65a424d57d770c5
# To regenerate: poetry run python src/omnibase/runtimes/onex_runtime/v1_0_0/codegen/contract_to_model.py --contract src/omnibase/nodes/node_manager/v1_0_0/contract.yaml --output-dir src/omnibase/nodes/node_manager/v1_0_0/models

from enum import Enum

class NodeManagerErrorCode(Enum):
    UNKNOWN_ERROR = 'UNKNOWN_ERROR'
    INVALID_PARAMETER = 'INVALID_PARAMETER'
    MISSING_REQUIRED_PARAMETER = 'MISSING_REQUIRED_PARAMETER'
    SCHEMA_VALIDATION_FAILED = 'SCHEMA_VALIDATION_FAILED'
    UNSUPPORTED_OPERATION = 'UNSUPPORTED_OPERATION'
