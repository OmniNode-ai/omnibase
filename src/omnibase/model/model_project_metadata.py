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
from typing import Any, Dict, Literal, Optional

import yaml
from pydantic import BaseModel, Field

from omnibase.enums.metadata import Lifecycle, MetaTypeEnum
from omnibase.model.model_entrypoint import EntrypointBlock
from omnibase.model.model_tool_collection import ToolCollection


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
    metadata_version: Literal["0.1.0"] = "0.1.0"
    protocol_version: Literal["0.1.0"] = "0.1.0"
    schema_version: Literal["0.1.0"] = "0.1.0"
    lifecycle: Lifecycle = Field(default=Lifecycle.ACTIVE)
    created_at: Optional[str] = None
    last_modified_at: Optional[str] = None
    license: Optional[str] = None
    # Entrypoint must be a URI: <type>://<target>
    entrypoint: EntrypointBlock = Field(
        default_factory=lambda: EntrypointBlock(type="yaml", target="project.onex.yaml")
    )
    meta_type: MetaTypeEnum = Field(default=MetaTypeEnum.PROJECT)
    tools: Optional[ToolCollection] = None
    copyright: str
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
        if "entrypoint" in data:
            entrypoint_val = data["entrypoint"]
            if isinstance(entrypoint_val, str):
                data["entrypoint"] = EntrypointBlock.from_uri(entrypoint_val)
            elif not isinstance(entrypoint_val, EntrypointBlock):
                raise ValueError(
                    f"entrypoint must be a URI string or EntrypointBlock, got: {entrypoint_val}"
                )
        # Convert tools to ToolCollection if needed
        if "tools" in data and isinstance(data["tools"], dict):
            data["tools"] = ToolCollection(data["tools"])
        if "copyright" not in data:
            raise ValueError("Missing required field: copyright")
        return cls(**data)

    def to_serializable_dict(self) -> dict:
        # Always emit entrypoint as URI string
        d = self.model_dump(exclude_none=True)
        d["entrypoint"] = self._parse_entrypoint(self.entrypoint)
        # Omit empty/null/empty-string fields except protocol-required
        for k in list(d.keys()):
            if d[k] in (None, "", [], {}):
                if k not in {"tools"}:
                    d.pop(k)
        return d


PROJECT_ONEX_YAML_PATH = (
    Path(__file__).parent.parent.parent.parent / "project.onex.yaml"
)


def get_canonical_versions() -> dict:
    """
    Load canonical version fields from project.onex.yaml.
    Returns a dict with keys: metadata_version, protocol_version, schema_version.
    Raises FileNotFoundError or KeyError if missing.
    """
    with open(PROJECT_ONEX_YAML_PATH, "r") as f:
        data = yaml.safe_load(f)
    return {
        "metadata_version": data["metadata_version"],
        "protocol_version": data["protocol_version"],
        "schema_version": data["schema_version"],
    }


def get_canonical_namespace_prefix() -> str:
    """
    Load the canonical namespace prefix from project.onex.yaml ('namespace' field).
    Returns a string, e.g., 'omnibase'.
    Raises FileNotFoundError or KeyError if missing.
    """
    with open(PROJECT_ONEX_YAML_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["namespace"]
