# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.668084'
# description: Stamped by PythonHandler
# entrypoint: python://model_node_introspection
# hash: 1709b3ea8e9130471ccbdd51d9b66cd150c007c0bac054ed1e75268484d96414
# last_modified_at: '2025-05-29T14:13:58.825779+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_node_introspection.py
# namespace: python://omnibase.model.model_node_introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 1d58424c-14a6-4b4d-b27a-0fd1baa8062c
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Node Introspection Models for ONEX.

This module defines the canonical Pydantic models for node introspection responses.
All ONEX nodes must return data conforming to these models when called with --introspect.

The introspection system enables:
- Auto-discovery of node capabilities
- Generic validation tooling
- Third-party ecosystem development
- Self-documenting node contracts
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NodeCapabilityEnum(str, Enum):
    """Standard node capabilities that can be declared via introspection."""

    SUPPORTS_DRY_RUN = "supports_dry_run"
    SUPPORTS_BATCH_PROCESSING = "supports_batch_processing"
    SUPPORTS_CUSTOM_HANDLERS = "supports_custom_handlers"
    TELEMETRY_ENABLED = "telemetry_enabled"
    SUPPORTS_CORRELATION_ID = "supports_correlation_id"
    SUPPORTS_EVENT_BUS = "supports_event_bus"
    SUPPORTS_SCHEMA_VALIDATION = "supports_schema_validation"
    SUPPORTS_ERROR_RECOVERY = "supports_error_recovery"


class CLIArgumentModel(BaseModel):
    """Model for CLI argument specification."""

    name: str = Field(..., description="Argument name (e.g., 'files', '--author')")
    type: str = Field(..., description="Argument type (e.g., 'str', 'bool', 'int')")
    required: bool = Field(..., description="Whether argument is required")
    description: str = Field(..., description="Human-readable argument description")
    default: Optional[Any] = Field(None, description="Default value if optional")
    choices: Optional[List[str]] = Field(None, description="Valid choices for argument")


class CLIInterfaceModel(BaseModel):
    """Model for CLI interface specification."""

    entrypoint: str = Field(..., description="CLI entrypoint command")
    required_args: List[CLIArgumentModel] = Field(
        default_factory=list, description="Required CLI arguments"
    )
    optional_args: List[CLIArgumentModel] = Field(
        default_factory=list, description="Optional CLI arguments"
    )
    exit_codes: List[int] = Field(..., description="Possible exit codes")
    supports_introspect: bool = Field(
        True, description="Whether node supports --introspect"
    )


class StateFieldModel(BaseModel):
    """Model for state model field specification."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type")
    required: bool = Field(..., description="Whether field is required")
    description: str = Field(..., description="Field description")
    default: Optional[Any] = Field(None, description="Default value if optional")


class StateModelModel(BaseModel):
    """Model for state model specification."""

    class_name: str = Field(..., description="State model class name")
    schema_version: str = Field(..., description="Schema version for this state model")
    fields: List[StateFieldModel] = Field(..., description="State model fields")
    schema_file: Optional[str] = Field(None, description="Path to JSON schema file")


class StateModelsModel(BaseModel):
    """Model for input/output state models."""

    input: StateModelModel = Field(..., description="Input state model specification")
    output: StateModelModel = Field(..., description="Output state model specification")


class ErrorCodeModel(BaseModel):
    """Model for error code specification."""

    code: str = Field(
        ..., description="Error code (e.g., 'ONEX_STAMP_001_FILE_NOT_FOUND')"
    )
    number: int = Field(..., description="Numeric error identifier")
    description: str = Field(..., description="Human-readable error description")
    exit_code: int = Field(..., description="CLI exit code for this error")
    category: str = Field(
        ..., description="Error category (e.g., 'file', 'validation')"
    )


class ErrorCodesModel(BaseModel):
    """Model for error codes specification."""

    component: str = Field(
        ..., description="Error component identifier (e.g., 'STAMP', 'TREE')"
    )
    codes: List[ErrorCodeModel] = Field(..., description="List of error codes")
    total_codes: int = Field(..., description="Total number of error codes defined")


class DependenciesModel(BaseModel):
    """Model for node dependencies specification."""

    runtime: List[str] = Field(
        default_factory=list, description="Required runtime dependencies"
    )
    optional: List[str] = Field(
        default_factory=list, description="Optional dependencies"
    )
    python_version: str = Field(..., description="Required Python version")
    external_tools: List[str] = Field(
        default_factory=list, description="Required external tools"
    )


class VersionStatusModel(BaseModel):
    latest: Optional[str] = None
    supported: Optional[List[str]] = None
    deprecated: Optional[List[str]] = None
    # Add more fields as needed for protocol


class PerformanceProfileModel(BaseModel):
    cpu: Optional[float] = None
    memory: Optional[float] = None
    disk: Optional[float] = None
    throughput: Optional[float] = None
    latency_ms: Optional[float] = None
    notes: Optional[str] = None
    # Add more fields as needed for protocol


class NodeMetadataModel(BaseModel):
    """Model for node metadata."""

    name: str = Field(..., description="Node name")
    version: str = Field(..., description="Node version")
    description: str = Field(..., description="Node description")
    author: str = Field(..., description="Node author")
    schema_version: str = Field(..., description="Node schema version")
    created_at: Optional[str] = Field(None, description="Node creation timestamp")
    last_modified_at: Optional[str] = Field(
        None, description="Last modification timestamp"
    )

    # Enhanced version information
    available_versions: Optional[List[str]] = Field(
        None, description="All available versions of this node"
    )
    latest_version: Optional[str] = Field(None, description="Latest available version")
    total_versions: Optional[int] = Field(
        None, description="Total number of versions available"
    )
    version_status: Optional[VersionStatusModel] = Field(
        None, description="Status of each version (latest, supported, deprecated)"
    )

    # Ecosystem information
    category: Optional[str] = Field(
        None, description="Node category (e.g., validation, generation, transformation)"
    )
    tags: Optional[List[str]] = Field(
        None, description="Node tags for categorization and discovery"
    )
    maturity: Optional[str] = Field(
        None, description="Node maturity level (experimental, beta, stable, deprecated)"
    )
    use_cases: Optional[List[str]] = Field(
        None, description="Primary use cases for this node"
    )
    performance_profile: Optional[PerformanceProfileModel] = Field(
        None, description="Performance characteristics and resource usage"
    )


class ContractModel(BaseModel):
    """Model for node contract specification."""

    input_state_schema: str = Field(..., description="Input state JSON schema filename")
    output_state_schema: str = Field(
        ..., description="Output state JSON schema filename"
    )
    cli_interface: CLIInterfaceModel = Field(
        ..., description="CLI interface specification"
    )
    protocol_version: str = Field(..., description="ONEX protocol version")


class NodeIntrospectionResponse(BaseModel):
    """
    Canonical response model for ONEX node introspection.

    This is the standardized format that all ONEX nodes must return
    when called with the --introspect command.
    """

    node_metadata: NodeMetadataModel = Field(
        ..., description="Node metadata and identification"
    )
    contract: ContractModel = Field(
        ..., description="Node contract and interface specification"
    )
    state_models: StateModelsModel = Field(
        ..., description="Input and output state model specifications"
    )
    error_codes: ErrorCodesModel = Field(
        ..., description="Error codes and exit code mapping"
    )
    dependencies: DependenciesModel = Field(
        ..., description="Runtime and optional dependencies"
    )
    capabilities: List[NodeCapabilityEnum] = Field(
        default_factory=list, description="Node capabilities"
    )
    introspection_version: str = Field(
        "1.0.0", description="Introspection format version"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "node_metadata": {
                    "name": "stamper_node",
                    "version": "1.0.0",
                    "description": "ONEX metadata stamper for file annotation",
                    "author": "ONEX Team",
                    "schema_version": "1.1.1",
                },
                "contract": {
                    "input_state_schema": "stamper_input.schema.json",
                    "output_state_schema": "stamper_output.schema.json",
                    "cli_interface": {
                        "entrypoint": "python -m omnibase.nodes.stamper_node.v1_0_0.node",
                        "required_args": [
                            {
                                "name": "files",
                                "type": "List[str]",
                                "required": True,
                                "description": "Files to stamp",
                            }
                        ],
                        "optional_args": [
                            {
                                "name": "--author",
                                "type": "str",
                                "required": False,
                                "description": "Author name for metadata",
                            }
                        ],
                        "exit_codes": [0, 1, 2],
                    },
                    "protocol_version": "1.1.0",
                },
                "capabilities": ["supports_dry_run", "supports_batch_processing"],
            }
        }
    )


def create_node_introspection_response(
    node_metadata: NodeMetadataModel,
    contract: ContractModel,
    state_models: StateModelsModel,
    error_codes: ErrorCodesModel,
    dependencies: DependenciesModel,
    capabilities: Optional[List[NodeCapabilityEnum]] = None,
    introspection_version: str = "1.0.0",
) -> NodeIntrospectionResponse:
    """
    Factory function to create a standardized node introspection response.

    Args:
        node_metadata: Node metadata and identification
        contract: Node contract and interface specification
        state_models: Input and output state model specifications
        error_codes: Error codes and exit code mapping
        dependencies: Runtime and optional dependencies
        capabilities: Node capabilities (optional)
        introspection_version: Introspection format version

    Returns:
        NodeIntrospectionResponse: Standardized introspection response
    """
    return NodeIntrospectionResponse(
        node_metadata=node_metadata,
        contract=contract,
        state_models=state_models,
        error_codes=error_codes,
        dependencies=dependencies,
        capabilities=capabilities or [],
        introspection_version=introspection_version,
    )

NodeMetadataModel.model_rebuild()
VersionStatusModel.model_rebuild()
PerformanceProfileModel.model_rebuild()
