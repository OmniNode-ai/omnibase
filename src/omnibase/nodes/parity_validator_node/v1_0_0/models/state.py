# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.346218'
# description: Stamped by PythonHandler
# entrypoint: python://state.py
# hash: 82b7f127e73dc9662d7b2c2f2955173e50c7bb9a05439a3163351ed687d1d175
# last_modified_at: '2025-05-29T11:50:11.515089+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: omnibase.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 787de6b9-4e40-4b23-bd35-d2f2d8d63c69
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
State models for parity validator node.

This module defines the input and output state models for the parity validator node,
which auto-discovers and validates all ONEX nodes for CLI/node parity, schema conformance,
and contract compliance.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus


class ValidationTypeEnum(str, Enum):
    """Types of validation performed by the parity validator."""

    CLI_NODE_PARITY = "cli_node_parity"
    SCHEMA_CONFORMANCE = "schema_conformance"
    ERROR_CODE_USAGE = "error_code_usage"
    CONTRACT_COMPLIANCE = "contract_compliance"
    INTROSPECTION_VALIDITY = "introspection_validity"


class ValidationResultEnum(str, Enum):
    """Result of a validation check."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class NodeValidationResult(BaseModel):
    """Validation result for a single node."""

    node_name: str = Field(description="Name of the validated node")
    node_version: str = Field(description="Version of the validated node")
    validation_type: ValidationTypeEnum = Field(
        description="Type of validation performed"
    )
    result: ValidationResultEnum = Field(description="Validation result")
    message: str = Field(description="Human-readable result message")
    details: Optional[Dict[str, str]] = Field(
        default=None, description="Additional details about the validation"
    )
    execution_time_ms: Optional[float] = Field(
        default=None, description="Time taken for this validation in milliseconds"
    )


class DiscoveredNode(BaseModel):
    """Information about a discovered ONEX node."""

    name: str = Field(description="Node name")
    version: str = Field(description="Node version")
    module_path: str = Field(description="Python module path")
    introspection_available: bool = Field(
        description="Whether introspection is available"
    )
    cli_entrypoint: Optional[str] = Field(
        default=None, description="CLI entrypoint command"
    )
    error_count: int = Field(default=0, description="Number of errors during discovery")


# Schema version constant
PARITY_VALIDATOR_STATE_SCHEMA_VERSION = "1.0.0"


class ParityValidatorInputState(BaseModel):
    """Input state for parity validator node."""

    version: str = Field(
        default=PARITY_VALIDATOR_STATE_SCHEMA_VERSION,
        description="Schema version for input state (must be compatible with current schema)",
    )

    nodes_directory: str = Field(
        default="src/omnibase/nodes", description="Directory to scan for ONEX nodes"
    )

    validation_types: Optional[List[ValidationTypeEnum]] = Field(
        default=None, description="Specific validation types to run (if None, runs all)"
    )

    node_filter: Optional[List[str]] = Field(
        default=None,
        description="Filter to specific node names (if None, validates all discovered nodes)",
    )

    fail_fast: bool = Field(
        default=False, description="Stop validation on first failure"
    )

    include_performance_metrics: bool = Field(
        default=True, description="Include performance timing in results"
    )

    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for request tracking and telemetry",
    )

    @field_validator("validation_types")
    @classmethod
    def validate_validation_types(
        cls, v: Optional[List[ValidationTypeEnum]]
    ) -> Optional[List[ValidationTypeEnum]]:
        """Validate validation types list."""
        if v is not None and len(v) == 0:
            raise OnexError(
                "validation_types cannot be empty list", CoreErrorCode.INVALID_PARAMETER
            )
        return v

    @field_validator("node_filter")
    @classmethod
    def validate_node_filter(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate node filter list."""
        if v is not None and len(v) == 0:
            raise OnexError(
                "node_filter cannot be empty list", CoreErrorCode.INVALID_PARAMETER
            )
        return v

    @field_validator("nodes_directory")
    @classmethod
    def validate_nodes_directory(cls, v: str) -> str:
        """Validate nodes directory is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "nodes_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


class ParityValidatorOutputState(BaseModel):
    """Output state for parity validator node."""

    version: str = Field(
        default=PARITY_VALIDATOR_STATE_SCHEMA_VERSION,
        description="Schema version for output state (must match input version)",
    )

    status: OnexStatus = Field(description="Overall validation status")

    message: str = Field(description="Human-readable status message")

    discovered_nodes: List[DiscoveredNode] = Field(
        default_factory=list, description="List of all discovered ONEX nodes"
    )

    validation_results: List[NodeValidationResult] = Field(
        default_factory=list,
        description="Detailed validation results for each node and validation type",
    )

    summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Summary statistics (total_nodes, total_validations, passed, failed, skipped, errors)",
    )

    nodes_directory: str = Field(description="Directory that was scanned")

    validation_types_run: List[ValidationTypeEnum] = Field(
        default_factory=list, description="List of validation types that were executed"
    )

    total_execution_time_ms: Optional[float] = Field(
        default=None, description="Total time taken for all validations in milliseconds"
    )

    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for request tracking and telemetry",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        """Validate status field."""
        if v not in [OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR]:
            raise OnexError(f"Invalid status: {v}", CoreErrorCode.INVALID_PARAMETER)
        return v


def create_parity_validator_input_state(
    nodes_directory: str = "src/omnibase/nodes",
    validation_types: Optional[List[ValidationTypeEnum]] = None,
    node_filter: Optional[List[str]] = None,
    fail_fast: bool = False,
    include_performance_metrics: bool = True,
    correlation_id: Optional[str] = None,
) -> ParityValidatorInputState:
    """Factory function to create ParityValidatorInputState with proper version."""
    return ParityValidatorInputState(
        version=PARITY_VALIDATOR_STATE_SCHEMA_VERSION,
        nodes_directory=nodes_directory,
        validation_types=validation_types,
        node_filter=node_filter,
        fail_fast=fail_fast,
        include_performance_metrics=include_performance_metrics,
        correlation_id=correlation_id,
    )


def create_parity_validator_output_state(
    status: OnexStatus,
    message: str,
    discovered_nodes: Optional[List[DiscoveredNode]] = None,
    validation_results: Optional[List[NodeValidationResult]] = None,
    summary: Optional[Dict[str, int]] = None,
    nodes_directory: str = "src/omnibase/nodes",
    validation_types_run: Optional[List[ValidationTypeEnum]] = None,
    total_execution_time_ms: Optional[float] = None,
    correlation_id: Optional[str] = None,
) -> ParityValidatorOutputState:
    """Factory function to create ParityValidatorOutputState with proper version."""
    return ParityValidatorOutputState(
        version=PARITY_VALIDATOR_STATE_SCHEMA_VERSION,
        status=status,
        message=message,
        discovered_nodes=discovered_nodes or [],
        validation_results=validation_results or [],
        summary=summary or {},
        nodes_directory=nodes_directory,
        validation_types_run=validation_types_run or [],
        total_execution_time_ms=total_execution_time_ms,
        correlation_id=correlation_id,
    )
