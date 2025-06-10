from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from omnibase.enums.onex_status import OnexStatus
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.runtimes.onex_runtime.v1_0_0.utils.schema_version_validator import validate_semantic_version

SCHEMA_GENERATOR_STATE_SCHEMA_VERSION = "1.0.0"

class SchemaGeneratorInputState(BaseModel):
    """
    Input state contract for the schema generator node (node-local).
    """
    version: str = Field(default=SCHEMA_GENERATOR_STATE_SCHEMA_VERSION)
    output_directory: str = Field(default="src/omnibase/schemas")
    models_to_generate: Optional[List[str]] = Field(default=None)
    include_metadata: bool = Field(default=True)
    correlation_id: Optional[str] = Field(default=None)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v: str) -> str:
        if not v or not v.strip():
            raise OnexError("output_directory cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        return v.strip()

class SchemaGeneratorOutputState(BaseModel):
    """
    Output state contract for the schema generator node (node-local).
    """
    version: str = Field(default=SCHEMA_GENERATOR_STATE_SCHEMA_VERSION)
    status: OnexStatus
    message: str
    schemas_generated: List[str] = Field(default_factory=list)
    output_directory: str
    total_schemas: int = Field(default=0)
    correlation_id: Optional[str] = Field(default=None)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        if v not in OnexStatus:
            raise OnexError(f"status must be a valid OnexStatus value, got '{v}'", CoreErrorCode.INVALID_PARAMETER)
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise OnexError("message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        return v.strip()

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory_output(cls, v: str) -> str:
        if not v or not v.strip():
            raise OnexError("output_directory cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        return v.strip()

    @field_validator("total_schemas")
    @classmethod
    def validate_total_schemas(cls, v: int) -> int:
        if v < 0:
            raise OnexError("total_schemas must be non-negative", CoreErrorCode.PARAMETER_OUT_OF_RANGE)
        return v

def create_schema_generator_input_state(
    output_directory: str = "src/omnibase/schemas",
    models_to_generate: Optional[List[str]] = None,
    include_metadata: bool = True,
    correlation_id: Optional[str] = None,
) -> SchemaGeneratorInputState:
    return SchemaGeneratorInputState(
        output_directory=output_directory,
        models_to_generate=models_to_generate,
        include_metadata=include_metadata,
        correlation_id=correlation_id,
    )

def create_schema_generator_output_state(
    status: str,
    message: str,
    schemas_generated: List[str],
    output_directory: str,
    total_schemas: int,
    correlation_id: Optional[str] = None,
) -> SchemaGeneratorOutputState:
    return SchemaGeneratorOutputState(
        status=OnexStatus(status),
        message=message,
        schemas_generated=schemas_generated,
        output_directory=output_directory,
        total_schemas=total_schemas,
        correlation_id=correlation_id,
    ) 