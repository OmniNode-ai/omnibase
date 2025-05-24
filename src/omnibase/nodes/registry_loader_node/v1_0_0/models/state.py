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
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.model.enum_onex_status import OnexStatus


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
