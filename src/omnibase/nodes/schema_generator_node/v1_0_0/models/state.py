# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.534432'
# description: Stamped by PythonHandler
# entrypoint: python://state
# hash: 86a88f68774034e898c4309ad20e0a91c1018838f92540b45882ba14136ee39b
# last_modified_at: '2025-05-29T14:13:59.737252+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: python://omnibase.nodes.schema_generator_node.v1_0_0.models.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 76d14d88-7bee-4180-95a0-f41843b08ea9
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
State models for schema_generator_node.

This module defines the input and output state contracts for the schema generator node.
The node generates JSON schemas from Pydantic state models for validation and documentation.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums.onex_status import OnexStatus
from omnibase.runtimes.onex_runtime.v1_0_0.utils.schema_version_validator import (
    validate_semantic_version,
)

# Schema version for this state model
SCHEMA_GENERATOR_STATE_SCHEMA_VERSION = "1.0.0"


class SchemaGeneratorInputState(BaseModel):
    """
    Input state contract for the schema generator node (node-local).

    This model defines the input parameters required for schema generator node execution.
    All fields are validated according to the current schema version.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.

    Fields:
        version: Schema version for input state (must match current schema version)
        output_directory: Directory where JSON schemas will be generated
        models_to_generate: Optional list of specific models to generate schemas for
        include_metadata: Whether to include additional metadata in schemas
        correlation_id: Optional correlation ID for request tracking and telemetry
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": "1.0.0",
                "output_directory": "src/omnibase/schemas",
                "models_to_generate": ["stamper_input", "stamper_output"],
                "include_metadata": True,
                "correlation_id": "req-123e4567-e89b-12d3-a456-426614174000",
            }
        }
    )

    version: str = Field(
        default=SCHEMA_GENERATOR_STATE_SCHEMA_VERSION,
        description="Schema version for input state (must be compatible with current schema)",
        json_schema_extra={"example": "1.0.0"},
    )

    output_directory: str = Field(
        default="src/omnibase/schemas",
        description="Directory where JSON schemas will be generated",
        json_schema_extra={"example": "src/omnibase/schemas"},
    )

    models_to_generate: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific models to generate schemas for (if None, generates all)",
        json_schema_extra={"example": ["stamper_input", "stamper_output"]},
    )

    include_metadata: bool = Field(
        default=True,
        description="Whether to include additional metadata in schemas",
        json_schema_extra={"example": True},
    )

    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for request tracking and telemetry",
        json_schema_extra={"example": "req-123e4567-e89b-12d3-a456-426614174000"},
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v: str) -> str:
        """Validate that output_directory is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "output_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


class SchemaGeneratorOutputState(BaseModel):
    """
    Output state contract for the schema generator node (node-local).

    This model defines the output structure returned after schema generator node execution.
    All fields are validated according to the current schema version.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.

    Fields:
        version: Schema version for output state (must match current schema version)
        status: Execution status ("success", "failure", "warning")
        message: Human-readable status message
        schemas_generated: List of schema files that were generated
        output_directory: Directory where schemas were generated
        total_schemas: Total number of schemas generated
        correlation_id: Optional correlation ID for request tracking and telemetry
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": "1.0.0",
                "status": "success",
                "message": "Generated 8 JSON schemas successfully",
                "schemas_generated": [
                    "stamper_input.schema.json",
                    "stamper_output.schema.json",
                ],
                "output_directory": "src/omnibase/schemas",
                "total_schemas": 8,
                "correlation_id": "req-123e4567-e89b-12d3-a456-426614174000",
            }
        }
    )

    version: str = Field(
        default=SCHEMA_GENERATOR_STATE_SCHEMA_VERSION,
        description="Schema version for output state (must be compatible with current schema)",
        json_schema_extra={"example": "1.0.0"},
    )

    status: OnexStatus = Field(
        description="Execution status",
        json_schema_extra={"example": OnexStatus.SUCCESS.value},
    )

    message: str = Field(
        description="Human-readable status message",
        json_schema_extra={"example": "Generated 8 JSON schemas successfully"},
    )

    schemas_generated: List[str] = Field(
        default_factory=list,
        description="List of schema files that were generated",
        json_schema_extra={
            "example": ["stamper_input.schema.json", "stamper_output.schema.json"]
        },
    )

    output_directory: str = Field(
        description="Directory where schemas were generated",
        json_schema_extra={"example": "src/omnibase/schemas"},
    )

    total_schemas: int = Field(
        default=0,
        description="Total number of schemas generated",
        json_schema_extra={"example": 8},
    )

    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for request tracking and telemetry",
        json_schema_extra={"example": "req-123e4567-e89b-12d3-a456-426614174000"},
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        """Validate that status is a valid OnexStatus value."""
        if v not in OnexStatus:
            raise OnexError(
                f"status must be a valid OnexStatus value, got '{v}'",
                CoreErrorCode.INVALID_PARAMETER,
            )
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory_output(cls, v: str) -> str:
        """Validate that output_directory is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "output_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()

    @field_validator("total_schemas")
    @classmethod
    def validate_total_schemas(cls, v: int) -> int:
        """Validate that total_schemas is non-negative."""
        if v < 0:
            raise OnexError(
                "total_schemas must be non-negative",
                CoreErrorCode.PARAMETER_OUT_OF_RANGE,
            )
        return v


def create_schema_generator_input_state(
    output_directory: str = "src/omnibase/schemas",
    models_to_generate: Optional[List[str]] = None,
    include_metadata: bool = True,
    correlation_id: Optional[str] = None,
) -> SchemaGeneratorInputState:
    """
    Factory function to create a SchemaGeneratorInputState with proper version.

    Args:
        output_directory: Directory where JSON schemas will be generated
        models_to_generate: Optional list of specific models to generate schemas for
        include_metadata: Whether to include additional metadata in schemas
        correlation_id: Optional correlation ID for request tracking

    Returns:
        SchemaGeneratorInputState: Properly versioned input state
    """
    return SchemaGeneratorInputState(
        version=SCHEMA_GENERATOR_STATE_SCHEMA_VERSION,
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
    """
    Factory function to create a SchemaGeneratorOutputState with proper version.

    Args:
        status: Execution status
        message: Human-readable status message
        schemas_generated: List of schema files that were generated
        output_directory: Directory where schemas were generated
        total_schemas: Total number of schemas generated
        correlation_id: Optional correlation ID for request tracking

    Returns:
        SchemaGeneratorOutputState: Properly versioned output state
    """
    return SchemaGeneratorOutputState(
        version=SCHEMA_GENERATOR_STATE_SCHEMA_VERSION,
        status=status,
        message=message,
        schemas_generated=schemas_generated,
        output_directory=output_directory,
        total_schemas=total_schemas,
        correlation_id=correlation_id,
    )
