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


from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import yaml
from pathlib import Path


class ProjectMetadataBlock(BaseModel):
    """
    Canonical ONEX project-level metadata block.
    Mirrors NodeMetadataBlock but for project root.

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
    lifecycle: str = Field(default="active")
    created_at: Optional[str] = None
    last_modified_at: Optional[str] = None
    license: Optional[str] = None
    # Entrypoint must be a URI: <type>://<target>
    entrypoint: str = Field(default="yaml://project.onex.yaml")
    meta_type: str = Field(default="project")
    tools: Optional[Dict[str, Any]] = None
    copyright: str
    # Add project-specific fields as needed

    model_config = {"extra": "allow"}

    @classmethod
    def _parse_entrypoint(cls, value: str) -> str:
        # Accept only URI format
        if isinstance(value, str) and "://" in value:
            return value
        raise ValueError(
            f"Entrypoint must be a URI string: <type>://<target>, got: {value}"
        )

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectMetadataBlock":
        # Accept only URI entrypoint format
        if "entrypoint" in data:
            data["entrypoint"] = cls._parse_entrypoint(data["entrypoint"])
        if "copyright" not in data:
            raise ValueError("Missing required field: copyright")
        return cls(**data)

    def to_serializable_dict(self) -> dict:
        # Always emit entrypoint as URI
        d = self.dict(exclude_none=True)
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
