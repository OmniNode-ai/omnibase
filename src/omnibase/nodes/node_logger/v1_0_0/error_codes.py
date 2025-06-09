# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: <to-be-updated>
# To regenerate: poetry run onex run schema_generator_node --args='["src/omnibase/nodes/node_logger/v1_0_0/contract.yaml", "src/omnibase/nodes/node_logger/v1_0_0/error_codes.py"]'

from enum import Enum

class NodeLoggerErrorCode(Enum):
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_REQUIRED_PARAMETER = "MISSING_REQUIRED_PARAMETER"
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    PARAMETER_OUT_OF_RANGE = "PARAMETER_OUT_OF_RANGE"
    FILE_WRITE_ERROR = "FILE_WRITE_ERROR"
    FORMAT_NOT_SUPPORTED = "FORMAT_NOT_SUPPORTED"
    CONTEXT_TOO_DEEP = "CONTEXT_TOO_DEEP"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
