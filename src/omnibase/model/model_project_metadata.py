# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-29T06:01:33.492378'
# description: Stamped by PythonHandler
# entrypoint: python://model_project_metadata
# hash: c0f792ed6e667c4eca139b85b9a6ad5e660a1b71664fa23e328dc66b8c5c1112
# last_modified_at: '2025-05-29T14:13:58.911890+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_project_metadata.py
# namespace: python://omnibase.model.model_project_metadata
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: ce8a74b5-9b6e-494e-abec-c3e5248b21aa
# version: 1.0.0
# === /OmniNode:Metadata ===


from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml
from pydantic import BaseModel, Field

from omnibase.enums import ArtifactTypeEnum, NamespaceStrategyEnum
from omnibase.enums.metadata import Lifecycle, MetaTypeEnum
from omnibase.metadata.metadata_constants import (
    AUTHOR_KEY,
    COPYRIGHT_KEY,
    CREATED_AT_KEY,
    DESCRIPTION_KEY,
    ENTRYPOINT_KEY,
    LAST_MODIFIED_AT_KEY,
    LICENSE_KEY,
    LIFECYCLE_KEY,
    METADATA_VERSION_KEY,
    NAME_KEY,
    NAMESPACE_KEY,
    PROJECT_ONEX_YAML_FILENAME,
    PROTOCOL_VERSION_KEY,
    SCHEMA_VERSION_KEY,
    TOOLS_KEY,
)
from omnibase.model.model_entrypoint import EntrypointBlock
from omnibase.model.model_onex_ignore import OnexIgnoreSection
from omnibase.model.model_onex_version import OnexVersionInfo
from omnibase.model.model_tool_collection import ToolCollection


class ArtifactTypeConfig(BaseModel):
    name: ArtifactTypeEnum
    metadata_file: Optional[str] = None
    version_pattern: Optional[str] = None


class NamespaceConfig(BaseModel):
    enabled: bool = True
    strategy: NamespaceStrategyEnum = NamespaceStrategyEnum.ONEX_DEFAULT


class MetadataValidationConfig(BaseModel):
    enabled: bool = True
    required_fields: Optional[List[str]] = None


class TreeGeneratorConfig(BaseModel):
    artifact_types: List[ArtifactTypeConfig] = Field(default_factory=list)
    namespace: NamespaceConfig = Field(default_factory=NamespaceConfig)
    metadata_validation: MetadataValidationConfig = Field(
        default_factory=MetadataValidationConfig
    )
    tree_ignore: Optional[OnexIgnoreSection] = Field(
        default=None,
        description="Glob patterns for files/directories to ignore during tree generation, using canonical .onexignore format. Example: {'patterns': ['__pycache__/', '*.pyc', '.git/']}",
    )


class ProjectMetadataBlock(BaseModel):
    """
    Canonical ONEX project-level metadata block.
    - tools: ToolCollection (not dict[str, Any])
    - meta_type: MetaTypeEnum (not str)
    - lifecycle: Lifecycle (not str)
    Entrypoint field must use the canonical URI format: '<type>://<target>'
    Example: 'python://main.py', 'yaml://project.onex.yaml', 'markdown://debug_log.md'
    """

    author: str
    name: str
    namespace: str
    description: Optional[str] = None
    versions: OnexVersionInfo
    lifecycle: Lifecycle = Field(default=Lifecycle.ACTIVE)
    created_at: Optional[str] = None
    last_modified_at: Optional[str] = None
    license: Optional[str] = None
    # Entrypoint must be a URI: <type>://<target>
    entrypoint: EntrypointBlock = Field(
        default_factory=lambda: EntrypointBlock(
            type="yaml", target=PROJECT_ONEX_YAML_FILENAME
        )
    )
    meta_type: MetaTypeEnum = Field(default=MetaTypeEnum.PROJECT)
    tools: Optional[ToolCollection] = None
    copyright: str
    tree_generator: Optional[TreeGeneratorConfig] = None
    # Add project-specific fields as needed

    model_config = {"extra": "allow"}

    @classmethod
    def _parse_entrypoint(cls, value) -> str:
        # Accept EntrypointBlock or URI string, always return URI string
        if isinstance(value, str) and "://" in value:
            return value
        if hasattr(value, "type") and hasattr(value, "target"):
            return f"{value.type}://{value.target}"
        raise ValueError(
            f"Entrypoint must be a URI string or EntrypointBlock, got: {value}"
        )

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectMetadataBlock":
        # Convert entrypoint to EntrypointBlock if needed
        if ENTRYPOINT_KEY in data:
            entrypoint_val = data[ENTRYPOINT_KEY]
            if isinstance(entrypoint_val, str):
                data[ENTRYPOINT_KEY] = EntrypointBlock.from_uri(entrypoint_val)
            elif not isinstance(entrypoint_val, EntrypointBlock):
                raise ValueError(
                    f"entrypoint must be a URI string or EntrypointBlock, got: {entrypoint_val}"
                )
        # Convert tools to ToolCollection if needed
        if TOOLS_KEY in data and isinstance(data[TOOLS_KEY], dict):
            data[TOOLS_KEY] = ToolCollection(data[TOOLS_KEY])
        # Convert version fields to OnexVersionInfo
        version_fields = [
            METADATA_VERSION_KEY,
            PROTOCOL_VERSION_KEY,
            SCHEMA_VERSION_KEY,
        ]
        if all(f in data for f in version_fields):
            data["versions"] = OnexVersionInfo(
                metadata_version=data.pop(METADATA_VERSION_KEY),
                protocol_version=data.pop(PROTOCOL_VERSION_KEY),
                schema_version=data.pop(SCHEMA_VERSION_KEY),
            )
        if COPYRIGHT_KEY not in data:
            raise ValueError(f"Missing required field: {COPYRIGHT_KEY}")
        return cls(**data)

    def to_serializable_dict(self) -> dict:
        # Always emit entrypoint as URI string
        d = self.model_dump(exclude_none=True)
        d[ENTRYPOINT_KEY] = self._parse_entrypoint(self.entrypoint)
        # Omit empty/null/empty-string fields except protocol-required
        for k in list(d.keys()):
            if d[k] in (None, "", [], {}):
                if k not in {TOOLS_KEY}:
                    d.pop(k)
        return d


PROJECT_ONEX_YAML_PATH = (
    Path(__file__).parent.parent.parent.parent / PROJECT_ONEX_YAML_FILENAME
)


def get_canonical_versions() -> OnexVersionInfo:
    """
    Load canonical version fields from project.onex.yaml.
    Returns an OnexVersionInfo model.
    Raises FileNotFoundError or KeyError if missing.
    """
    with open(PROJECT_ONEX_YAML_PATH, "r") as f:
        data = yaml.safe_load(f)
    return OnexVersionInfo(
        metadata_version=data[METADATA_VERSION_KEY],
        protocol_version=data[PROTOCOL_VERSION_KEY],
        schema_version=data[SCHEMA_VERSION_KEY],
    )


def get_canonical_namespace_prefix() -> str:
    """
    Load the canonical namespace prefix from project.onex.yaml ('namespace' field).
    Returns a string, e.g., 'omnibase'.
    Raises FileNotFoundError or KeyError if missing.
    """
    with open(PROJECT_ONEX_YAML_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data[NAMESPACE_KEY]
