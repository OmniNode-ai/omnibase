# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T09:34:52.821564'
# description: Stamped by PythonHandler
# entrypoint: python://state.py
# hash: 46016ab0b3293a37eba0e602cccae3effda408f5336b78d48372f79f3459f3e1
# last_modified_at: '2025-05-29T11:50:11.442906+00:00'
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
# uuid: 636246dc-455f-4111-9992-ae9363458d35
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
State models for node_manager_node.

Defines input and output state models for managing ONEX nodes including:
- Generating new nodes from templates
- Regenerating contracts and manifests
- Maintaining and fixing existing nodes

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus

# Current schema version for node manager state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
NODE_MANAGER_STATE_SCHEMA_VERSION = "1.0.0"


class NodeManagerOperation(str, Enum):
    """Supported operations for the node manager."""
    GENERATE = "generate"
    REGENERATE_CONTRACT = "regenerate_contract"
    REGENERATE_MANIFEST = "regenerate_manifest"
    FIX_NODE_HEALTH = "fix_node_health"
    SYNCHRONIZE_CONFIGS = "synchronize_configs"


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


def validate_node_name(name: str) -> str:
    """
    Validate that a node name follows ONEX naming conventions.

    Args:
        name: Node name to validate

    Returns:
        The validated node name

    Raises:
        OnexError: If node name doesn't follow conventions
    """
    import re

    # Node names should be lowercase with underscores, no special characters
    if not re.match(r"^[a-z][a-z0-9_]*[a-z0-9]$", name):
        raise OnexError(
            f"Node name '{name}' must be lowercase with underscores, start with letter, end with letter/number",
            CoreErrorCode.INVALID_PARAMETER,
        )
    
    # Prevent reserved names
    reserved_names = {"template", "base", "core", "protocol", "runtime", "test"}
    if name in reserved_names:
        raise OnexError(
            f"Node name '{name}' is reserved and cannot be used",
            CoreErrorCode.INVALID_PARAMETER,
        )
    
    return name


class NodeManagerInputState(BaseModel):
    """
    Input state model for node_manager_node.

    Defines all parameters needed for node management operations including:
    - Generating new nodes from templates
    - Regenerating contracts and manifests
    - Maintaining and fixing existing nodes

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    
    operation: NodeManagerOperation = Field(
        ...,
        description="Type of operation to perform (generate, regenerate_contract, etc.)"
    )
    
    # For generation operations
    node_name: Optional[str] = Field(
        default=None, 
        description="Name of the node (required for generation, optional for maintenance on specific nodes)"
    )
    
    template_source: Optional[str] = Field(
        default="template_node",
        description="Source template to use for generation (only used for generate operation)"
    )
    
    target_directory: Optional[str] = Field(
        default="src/omnibase/nodes",
        description="Target directory for operations"
    )
    
    author: Optional[str] = Field(
        default="OmniNode Team",
        description="Author name for generated/updated node metadata"
    )
    
    customizations: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom values to replace template placeholders (generation only)"
    )
    
    generation_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options for post-generation tasks (stamping, validation, etc.)"
    )
    
    # For maintenance operations
    nodes: Optional[List[str]] = Field(
        default=None,
        description="List of specific node names to operate on (if None, operates on all nodes)"
    )
    
    dry_run: bool = Field(
        default=True,
        description="Whether to run in dry-run mode (show what would be done without making changes)"
    )
    
    backup_enabled: bool = Field(
        default=True,
        description="Whether to create backups before making changes"
    )
    
    maintenance_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options specific to maintenance operations"
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("node_name")
    @classmethod
    def validate_node_name_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the node name follows ONEX conventions if provided."""
        if v is not None:
            return validate_node_name(v)
        return v

    @field_validator("template_source")
    @classmethod
    def validate_template_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate that template source is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise OnexError(
                "template_source cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip() if v else v

    @field_validator("target_directory")
    @classmethod
    def validate_target_directory(cls, v: Optional[str]) -> Optional[str]:
        """Validate that target directory is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise OnexError(
                "target_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip() if v else v

    @field_validator("author")
    @classmethod
    def validate_author(cls, v: Optional[str]) -> Optional[str]:
        """Validate that author is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise OnexError(
                "author cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip() if v else v

    def model_post_init(self, __context) -> None:
        """Validate operation-specific requirements after model initialization."""
        if self.operation == NodeManagerOperation.GENERATE:
            if not self.node_name:
                raise OnexError(
                    "node_name is required for generate operation",
                    CoreErrorCode.MISSING_REQUIRED_PARAMETER,
                )


class NodeManagerOutputState(BaseModel):
    """
    Output state model for node_manager_node.

    Includes operation result, status, message, and affected files.
    Always includes input_state for protocol traceability.
    """

    version: str = Field(
        ..., description="Schema version for output state"
    )
    
    status: OnexStatus = Field(
        ..., 
        description="Execution status"
    )
    
    operation: NodeManagerOperation = Field(
        ...,
        description="Operation performed"
    )
    
    message: str = Field(
        ..., 
        description="Human-readable result message"
    )
    
    input_state: NodeManagerInputState = Field(
        ...,
        description="Input state for traceability"
    )
    
    affected_files: Optional[List[str]] = Field(
        default=None,
        description="List of affected files"
    )
    
    node_directory: Optional[str] = Field(
        default=None,
        description="Directory of the processed/generated node"
    )
    
    processed_nodes: Optional[List[str]] = Field(
        default=None,
        description="List of processed node names"
    )
    
    validation_results: Optional[Any] = Field(
        default=None,
        description="Validation results for generated/processed nodes"
    )
    
    warnings: Optional[List[str]] = Field(
        default=None,
        description="List of warnings encountered"
    )
    
    next_steps: Optional[List[str]] = Field(
        default=None,
        description="Recommended next steps"
    )
    
    operation_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional operation details"
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        """Validate that status is a valid OnexStatus enum value."""
        if not isinstance(v, OnexStatus):
            try:
                return OnexStatus(v)
            except ValueError:
                raise OnexError(
                    f"Invalid status value: {v}",
                    CoreErrorCode.INVALID_PARAMETER,
                )
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()

    @field_validator("node_directory")
    @classmethod
    def validate_node_directory(cls, v: Optional[str]) -> Optional[str]:
        """Validate that node directory is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise OnexError(
                "node_directory cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip() if v else v


# Keep the old class names for backward compatibility
NodeGeneratorInputState = NodeManagerInputState
NodeGeneratorOutputState = NodeManagerOutputState


class NodeValidationResult(BaseModel):
    """
    Validation result model for nodes.

    Contains detailed validation information about a node.
    """

    is_valid: bool = Field(
        ..., 
        description="Whether the node passed all validations"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="List of validation errors found"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="List of validation warnings found"
    )
    
    checked_files: List[str] = Field(
        default_factory=list,
        description="List of files that were validated"
    )
    
    missing_files: List[str] = Field(
        default_factory=list,
        description="List of expected files that are missing"
    )


def create_node_manager_input_state(
    operation: NodeManagerOperation,
    node_name: Optional[str] = None,
    template_source: str = "template_node",
    target_directory: str = "src/omnibase/nodes",
    author: str = "OmniNode Team",
    customizations: Optional[Dict[str, Any]] = None,
    generation_options: Optional[Dict[str, Any]] = None,
    nodes: Optional[List[str]] = None,
    dry_run: bool = True,
    backup_enabled: bool = True,
    maintenance_options: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
) -> NodeManagerInputState:
    """
    Factory function to create a NodeManagerInputState with proper version handling.

    Args:
        operation: Type of operation to perform
        node_name: Name of the node (required for generation)
        template_source: Source template to use for generation
        target_directory: Target directory for operations
        author: Author name for generated/updated node metadata
        customizations: Custom values to replace template placeholders
        generation_options: Options for post-generation tasks
        nodes: List of specific node names to operate on
        dry_run: Whether to run in dry-run mode
        backup_enabled: Whether to create backups before making changes
        maintenance_options: Options specific to maintenance operations
        version: Optional schema version (defaults to current schema version)

    Returns:
        NodeManagerInputState instance with validated fields
    """
    if version is None:
        version = NODE_MANAGER_STATE_SCHEMA_VERSION

    return NodeManagerInputState(
        version=version,
        operation=operation,
        node_name=node_name,
        template_source=template_source,
        target_directory=target_directory,
        author=author,
        customizations=customizations or {},
        generation_options=generation_options or {
            "run_initial_stamping": True,
            "generate_onextree": True,
            "run_parity_validation": True
        },
        nodes=nodes,
        dry_run=dry_run,
        backup_enabled=backup_enabled,
        maintenance_options=maintenance_options or {},
    )


def create_node_manager_output_state(
    operation: NodeManagerOperation,
    status: OnexStatus,
    message: str,
    input_state: NodeManagerInputState,
    affected_files: Optional[List[str]] = None,
    node_directory: Optional[str] = None,
    processed_nodes: Optional[List[str]] = None,
    validation_results: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
    operation_details: Optional[Dict[str, Any]] = None,
) -> NodeManagerOutputState:
    """
    Factory function to create a NodeManagerOutputState with proper version handling.

    Args:
        operation: Type of operation that was performed
        status: Result status of the operation
        message: Human-readable result or error message
        input_state: The input state that was used for the operation
        affected_files: List of files that were created/modified
        node_directory: Path to the primary node directory
        processed_nodes: List of node names that were processed
        validation_results: Results from validating nodes or operations
        warnings: List of warnings encountered during operation
        next_steps: Suggested next steps or actions to take
        operation_details: Operation-specific details and results

    Returns:
        NodeManagerOutputState instance with validated fields
    """
    return NodeManagerOutputState(
        version=input_state.version,
        operation=operation,
        status=status,
        message=message,
        input_state=input_state,
        affected_files=affected_files or [],
        node_directory=node_directory,
        processed_nodes=processed_nodes or [],
        validation_results=validation_results or {},
        warnings=warnings or [],
        next_steps=next_steps or [],
        operation_details=operation_details or {},
    )


# Legacy factory functions for backward compatibility
def create_node_generator_input_state(
    node_name: str,
    template_source: str = "template_node",
    target_directory: str = "src/omnibase/nodes",
    author: str = "OmniNode Team",
    customizations: Optional[Dict[str, Any]] = None,
    generation_options: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
) -> NodeManagerInputState:
    """Legacy factory function for backward compatibility."""
    return create_node_manager_input_state(
        operation=NodeManagerOperation.GENERATE,
        node_name=node_name,
        template_source=template_source,
        target_directory=target_directory,
        author=author,
        customizations=customizations,
        generation_options=generation_options,
        version=version,
    )


def create_node_generator_output_state(
    status: OnexStatus,
    message: str,
    node_directory: str,
    input_state: NodeManagerInputState,
    generated_files: Optional[List[str]] = None,
    validation_results: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
) -> NodeManagerOutputState:
    """Legacy factory function for backward compatibility."""
    return create_node_manager_output_state(
        operation=NodeManagerOperation.GENERATE,
        status=status,
        message=message,
        input_state=input_state,
        affected_files=generated_files,
        node_directory=node_directory,
        validation_results=validation_results,
        warnings=warnings,
        next_steps=next_steps,
    )
