# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.038864'
# description: Stamped by PythonHandler
# entrypoint: python://state
# hash: f9042ff008a9f4aa9f8376f89819ceecd496dbabd0e235357880f7bed7d784fa
# last_modified_at: '2025-05-29T14:14:00.138745+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: python://omnibase.nodes.tree_generator_node.v1_0_0.models.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 34dcd933-36f9-41bb-9716-d383ff701af5
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
State models for tree_generator_node.

Defines input and output state models for the tree generator node that
scans directory structures and generates .onextree manifest files.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

# Current schema version for tree generator node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
TREE_GENERATOR_STATE_SCHEMA_VERSION = "1.0.0"


def validate_semantic_version(version: str) -> str:
    """
    Validate that a version string follows semantic versioning format.

    Args:
        version: Version string to validate

    Returns:
        The validated version string

    Raises:
        OnexError: If version doesn't match semantic versioning format
    """
    import re

    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    if not re.match(semver_pattern, version):
        raise OnexError(
            f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0')",
            CoreErrorCode.INVALID_PARAMETER,
        )
    return version


class TreeGeneratorInputState(BaseModel):
    """
    Input state model for tree_generator_node.

    Defines the parameters needed to generate a .onextree manifest file
    from directory structure analysis.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    root_directory: str = Field(
        default="src/omnibase", description="Root directory to scan for ONEX artifacts"
    )
    output_format: str = Field(
        default="yaml", description="Output format for the manifest file (yaml or json)"
    )
    include_metadata: bool = Field(
        default=True, description="Whether to validate metadata files during scanning"
    )
    output_path: Optional[str] = Field(
        default=None,
        description="Custom output path for the manifest file (defaults to root/.onextree)",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("root_directory")
    @classmethod
    def validate_root_directory(cls, v: str) -> str:
        """Validate that root_directory is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "root_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validate that output_format is one of the allowed values."""
        allowed_formats = {"yaml", "json"}
        if v not in allowed_formats:
            raise OnexError(
                f"output_format must be one of {allowed_formats}, got '{v}'",
                CoreErrorCode.INVALID_PARAMETER,
            )
        return v


class TreeGeneratorOutputState(BaseModel):
    """
    Output state model for tree_generator_node.

    Contains the results of tree generation including manifest path,
    artifact counts, and validation results.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: str = Field(
        ..., description="Result status of the tree generation operation"
    )
    message: str = Field(..., description="Human-readable result or error message")
    manifest_path: Optional[str] = Field(
        default=None, description="Path to the generated manifest file"
    )
    artifacts_discovered: Optional[Dict[str, int]] = Field(
        default=None,
        description="Count of each artifact type discovered during scanning",
    )
    validation_results: Optional[Dict[str, Any]] = Field(
        default=None, description="Results of metadata validation during scanning"
    )
    tree_structure: Optional[Dict[str, Any]] = Field(
        default=None, description="Full tree structure data (optional, for debugging)"
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
        allowed_statuses = {"success", "error", "warning"}
        if v not in allowed_statuses:
            raise OnexError(
                f"status must be one of {allowed_statuses}, got '{v}'",
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


class ArtifactCounts(BaseModel):
    """
    Model for artifact counts discovered during tree scanning.

    Tracks the number of each type of ONEX artifact found during
    directory traversal and analysis.
    """

    nodes: int = Field(default=0, description="Number of node artifacts discovered")
    cli_tools: int = Field(
        default=0, description="Number of CLI tool artifacts discovered"
    )
    runtimes: int = Field(
        default=0, description="Number of runtime artifacts discovered"
    )
    adapters: int = Field(
        default=0, description="Number of adapter artifacts discovered"
    )
    contracts: int = Field(
        default=0, description="Number of contract artifacts discovered"
    )
    packages: int = Field(
        default=0, description="Number of package artifacts discovered"
    )

    @field_validator(
        "nodes", "cli_tools", "runtimes", "adapters", "contracts", "packages"
    )
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """Validate that all counts are non-negative."""
        if v < 0:
            raise OnexError(
                "Artifact counts must be non-negative",
                CoreErrorCode.PARAMETER_OUT_OF_RANGE,
            )
        return v


class ValidationResults(BaseModel):
    """
    Model for metadata validation results.

    Tracks the results of validating ONEX metadata during tree scanning,
    including counts of valid/invalid artifacts and error details.
    """

    valid_artifacts: int = Field(
        default=0, description="Number of artifacts with valid metadata"
    )
    invalid_artifacts: int = Field(
        default=0, description="Number of artifacts with invalid metadata"
    )
    errors: List[str] = Field(
        default_factory=list, description="List of validation error messages"
    )

    @field_validator("valid_artifacts", "invalid_artifacts")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """Validate that all counts are non-negative."""
        if v < 0:
            raise OnexError(
                "Validation counts must be non-negative",
                CoreErrorCode.PARAMETER_OUT_OF_RANGE,
            )
        return v


def create_tree_generator_input_state(
    root_directory: str = "src/omnibase",
    output_format: str = "yaml",
    include_metadata: bool = True,
    output_path: Optional[str] = None,
    version: Optional[str] = None,
) -> TreeGeneratorInputState:
    """
    Factory function to create a TreeGeneratorInputState with proper version handling.

    Args:
        root_directory: Root directory to scan for artifacts
        output_format: Output format for the manifest file
        include_metadata: Whether to validate metadata files
        output_path: Custom output path for the manifest file
        version: Optional schema version (defaults to current schema version)

    Returns:
        A validated TreeGeneratorInputState instance
    """
    if version is None:
        version = TREE_GENERATOR_STATE_SCHEMA_VERSION

    return TreeGeneratorInputState(
        version=version,
        root_directory=root_directory,
        output_format=output_format,
        include_metadata=include_metadata,
        output_path=output_path,
    )


def create_tree_generator_output_state(
    status: str,
    message: str,
    input_state: TreeGeneratorInputState,
    manifest_path: Optional[str] = None,
    artifacts_discovered: Optional[Dict[str, int]] = None,
    validation_results: Optional[Dict[str, Any]] = None,
    tree_structure: Optional[Dict[str, Any]] = None,
) -> TreeGeneratorOutputState:
    """
    Factory function to create a TreeGeneratorOutputState with proper version propagation.

    Args:
        status: Result status of the operation
        message: Human-readable result or error message
        input_state: The input state to propagate version from
        manifest_path: Path to the generated manifest file
        artifacts_discovered: Count of each artifact type discovered
        validation_results: Results of metadata validation
        tree_structure: Full tree structure data

    Returns:
        A validated TreeGeneratorOutputState instance with version matching input
    """
    return TreeGeneratorOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        manifest_path=manifest_path,
        artifacts_discovered=artifacts_discovered,
        validation_results=validation_results,
        tree_structure=tree_structure,
    )
