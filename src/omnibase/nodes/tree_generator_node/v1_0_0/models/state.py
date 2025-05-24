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
State models for tree_generator_node.

Defines input and output state models for the tree generator node that
scans directory structures and generates .onextree manifest files.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TreeGeneratorInputState(BaseModel):
    """
    Input state model for tree_generator_node.

    Defines the parameters needed to generate a .onextree manifest file
    from directory structure analysis.
    """

    version: str  # Schema version for input state
    root_directory: str = "src/omnibase"  # Root directory to scan
    output_format: str = "yaml"  # Output format: yaml or json
    include_metadata: bool = True  # Whether to validate metadata files
    output_path: Optional[str] = None  # Custom output path (defaults to root/.onextree)


class TreeGeneratorOutputState(BaseModel):
    """
    Output state model for tree_generator_node.

    Contains the results of tree generation including manifest path,
    artifact counts, and validation results.
    """

    version: str  # Schema version for output state (matches input)
    status: str  # Execution status: success|failure|warning
    message: str  # Human-readable result message
    manifest_path: Optional[str] = None  # Path to generated manifest file
    artifacts_discovered: Optional[Dict[str, int]] = None  # Count of each artifact type
    validation_results: Optional[Dict[str, Any]] = None  # Metadata validation results
    tree_structure: Optional[Dict[str, Any]] = None  # Full tree structure (optional)


class ArtifactCounts(BaseModel):
    """
    Model for artifact counts discovered during tree scanning.
    """

    nodes: int = 0
    cli_tools: int = 0
    runtimes: int = 0
    adapters: int = 0
    contracts: int = 0
    packages: int = 0


class ValidationResults(BaseModel):
    """
    Model for metadata validation results.
    """

    valid_artifacts: int = 0
    invalid_artifacts: int = 0
    errors: List[str] = []
