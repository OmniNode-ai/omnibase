# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 2403f1fb-9605-4bc3-8a53-dd240220a1e8
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.968817
# last_modified_at: 2025-05-24T13:39:57.891980
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9cdf081abf61fa062af9e2bdc49212b08cf963b08d82708e179d399494f6e5d1
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.state
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry Loader Node State Models.

Defines the input and output state models for the registry loader node.
This node loads and parses the ONEX registry from filesystem structure.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus

# Current schema version for registry loader node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
REGISTRY_LOADER_STATE_SCHEMA_VERSION = "1.0.0"


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


class ArtifactTypeEnum(str, Enum):
    """Enumeration of supported artifact types in the ONEX registry."""

    NODES = "nodes"
    CLI_TOOLS = "cli_tools"
    RUNTIMES = "runtimes"
    ADAPTERS = "adapters"
    CONTRACTS = "contracts"
    PACKAGES = "packages"


class RegistryLoadingErrorTypeEnum(str, Enum):
    """Enumeration of registry loading error types."""

    MISSING_FILE = "missing_file"
    PARSE_ERROR = "parse_error"
    INVALID_REGISTRY_ENTRY = "invalid_registry_entry"
    MISSING_METADATA = "missing_metadata"
    INVALID_METADATA = "invalid_metadata"
    LOAD_ERROR = "load_error"


class RegistryLoadingError(BaseModel):
    """
    Model for registry loading errors.

    Tracks errors encountered during registry loading for debugging and reporting.
    """

    path: str = Field(description="Path where the error occurred")
    error_type: RegistryLoadingErrorTypeEnum = Field(description="Type of error")
    error_message: str = Field(description="Human-readable error message")
    is_fatal: bool = Field(
        default=False, description="Whether this error prevents loading"
    )


class RegistryLoaderInputState(BaseModel):
    """
    Input state model for registry loader node.

    Defines the parameters needed to load the ONEX registry from filesystem.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(description="Schema version for input state")
    root_directory: str = Field(
        description="Root directory path to scan for ONEX artifacts"
    )
    onextree_path: Optional[str] = Field(
        default=None,
        description="Path to .onextree file (if None, will look for .onextree in root_directory parent)",
    )
    include_wip: bool = Field(
        default=False,
        description="Whether to include work-in-progress (.wip) artifacts",
    )
    artifact_types: Optional[List[ArtifactTypeEnum]] = Field(
        default=None,
        description="Filter to specific artifact types. If None, loads all types.",
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


class RegistryArtifact(BaseModel):
    """
    Represents a single artifact in the registry.
    """

    name: str = Field(description="Artifact name")
    version: str = Field(description="Artifact version")
    artifact_type: ArtifactTypeEnum = Field(description="Type of artifact")
    path: str = Field(description="Filesystem path to the artifact")
    metadata: Dict[str, Any] = Field(
        description="Parsed metadata from .onex or equivalent file"
    )
    is_wip: bool = Field(
        default=False, description="Whether this artifact is marked as work-in-progress"
    )


class RegistryLoaderOutputState(BaseModel):
    """
    Output state for registry loader node.

    Contains the results of registry loading including all discovered artifacts,
    statistics, and any errors encountered.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(description="Schema version used for loading")
    status: OnexStatus = Field(description="Overall loading status")
    message: str = Field(description="Human-readable status message")

    # Artifact results
    artifacts: List[RegistryArtifact] = Field(
        default_factory=list,
        description="List of all discovered artifacts (valid and invalid)",
    )
    artifact_count: int = Field(
        default=0, description="Total number of artifacts found"
    )
    valid_artifact_count: int = Field(
        default=0, description="Number of valid artifacts"
    )
    invalid_artifact_count: int = Field(
        default=0, description="Number of invalid artifacts"
    )
    wip_artifact_count: int = Field(default=0, description="Number of WIP artifacts")

    # Discovery metadata
    artifact_types_found: List[ArtifactTypeEnum] = Field(
        default_factory=list, description="List of artifact types that were discovered"
    )

    # Paths and timing
    root_directory: str = Field(description="Root directory that was scanned")
    onextree_path: Optional[str] = Field(
        default=None, description="Path to .onextree file if found"
    )
    scan_duration_ms: Optional[float] = Field(
        default=None, description="Time taken to scan in milliseconds"
    )

    # Error tracking
    errors: List[RegistryLoadingError] = Field(
        default_factory=list,
        description="List of non-fatal errors encountered during loading",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()

    @field_validator("root_directory")
    @classmethod
    def validate_root_directory_output(cls, v: str) -> str:
        """Validate that root_directory is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "root_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()

    @field_validator(
        "artifact_count",
        "valid_artifact_count",
        "invalid_artifact_count",
        "wip_artifact_count",
    )
    @classmethod
    def validate_non_negative_counts(cls, v: int) -> int:
        """Validate that all counts are non-negative."""
        if v < 0:
            raise OnexError(
                "Artifact counts must be non-negative", CoreErrorCode.INVALID_PARAMETER
            )
        return v

    @field_validator("scan_duration_ms")
    @classmethod
    def validate_scan_duration(cls, v: Optional[float]) -> Optional[float]:
        """Validate that scan duration is non-negative if provided."""
        if v is not None and v < 0:
            raise OnexError(
                "scan_duration_ms must be non-negative", CoreErrorCode.INVALID_PARAMETER
            )
        return v


def create_registry_loader_input_state(
    root_directory: str,
    onextree_path: Optional[str] = None,
    include_wip: bool = False,
    artifact_types: Optional[List[ArtifactTypeEnum]] = None,
    version: Optional[str] = None,
) -> RegistryLoaderInputState:
    """
    Factory function to create a RegistryLoaderInputState with proper version handling.

    Args:
        root_directory: Root directory path to scan for ONEX artifacts
        onextree_path: Path to .onextree file (optional)
        include_wip: Whether to include work-in-progress artifacts
        artifact_types: Filter to specific artifact types
        version: Optional schema version (defaults to current schema version)

    Returns:
        A validated RegistryLoaderInputState instance
    """
    if version is None:
        version = REGISTRY_LOADER_STATE_SCHEMA_VERSION

    return RegistryLoaderInputState(
        version=version,
        root_directory=root_directory,
        onextree_path=onextree_path,
        include_wip=include_wip,
        artifact_types=artifact_types,
    )


def create_registry_loader_output_state(
    status: OnexStatus,
    message: str,
    input_state: RegistryLoaderInputState,
    artifacts: Optional[List[RegistryArtifact]] = None,
    artifact_types_found: Optional[List[ArtifactTypeEnum]] = None,
    onextree_path: Optional[str] = None,
    scan_duration_ms: Optional[float] = None,
    errors: Optional[List[RegistryLoadingError]] = None,
) -> RegistryLoaderOutputState:
    """
    Factory function to create a RegistryLoaderOutputState with proper version propagation.

    Args:
        status: Overall loading status
        message: Human-readable status message
        input_state: The input state to propagate version and root_directory from
        artifacts: List of discovered artifacts
        artifact_types_found: List of artifact types discovered
        onextree_path: Path to .onextree file if found
        scan_duration_ms: Time taken to scan in milliseconds
        errors: List of non-fatal errors encountered

    Returns:
        A validated RegistryLoaderOutputState instance with version matching input
    """
    if artifacts is None:
        artifacts = []
    if artifact_types_found is None:
        artifact_types_found = []
    if errors is None:
        errors = []

    # Calculate counts from artifacts
    artifact_count = len(artifacts)
    valid_artifact_count = sum(
        1 for a in artifacts if a.metadata
    )  # Simplified validation check
    invalid_artifact_count = artifact_count - valid_artifact_count
    wip_artifact_count = sum(1 for a in artifacts if a.is_wip)

    return RegistryLoaderOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        artifacts=artifacts,
        artifact_count=artifact_count,
        valid_artifact_count=valid_artifact_count,
        invalid_artifact_count=invalid_artifact_count,
        wip_artifact_count=wip_artifact_count,
        artifact_types_found=artifact_types_found,
        root_directory=input_state.root_directory,  # Propagate from input
        onextree_path=onextree_path,
        scan_duration_ms=scan_duration_ms,
        errors=errors,
    )
