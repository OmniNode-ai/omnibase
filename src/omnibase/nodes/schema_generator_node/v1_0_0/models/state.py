# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 4fed6709-517c-4ea9-8ffa-33e85aadad5c
# author: OmniNode Team
# created_at: 2025-05-25T15:36:45.691747
# last_modified_at: 2025-05-25T19:48:02.874828
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a709cf6966e8ca246186f7c4aea2f2f405c56f8ca1e897a979ab6c15c3efad17
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.state
# meta_type: tool
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
                "output_directory": "src/schemas",
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
        default="src/schemas",
        description="Directory where JSON schemas will be generated",
        json_schema_extra={"example": "src/schemas"},
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
            raise ValueError("output_directory cannot be empty")
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
                "output_directory": "src/schemas",
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

    status: str = Field(
        description="Execution status",
        json_schema_extra={"example": "success"},
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
        json_schema_extra={"example": "src/schemas"},
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
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"success", "failure", "warning"}
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}, got '{v}'")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory_output(cls, v: str) -> str:
        """Validate that output_directory is not empty."""
        if not v or not v.strip():
            raise ValueError("output_directory cannot be empty")
        return v.strip()

    @field_validator("total_schemas")
    @classmethod
    def validate_total_schemas(cls, v: int) -> int:
        """Validate that total_schemas is non-negative."""
        if v < 0:
            raise ValueError("total_schemas must be non-negative")
        return v


def create_schema_generator_input_state(
    output_directory: str = "src/schemas",
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
