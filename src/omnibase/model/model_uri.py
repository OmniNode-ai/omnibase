# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_uri.py
# version: 1.0.0
# uuid: 429ef5cf-1b1d-4d04-a277-76643d7519fd
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166596
# last_modified_at: 2025-05-21T16:42:46.056384
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 841e4b41ed639f7ad4ae9758361012de3090ea3184398bdf16b6aebf5d027c2c
# entrypoint: python@model_uri.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_uri
# meta_type: tool
# === /OmniNode:Metadata ===


from pydantic import BaseModel, Field

from omnibase.model.model_enum_metadata import UriTypeEnum


class OnexUriModel(BaseModel):
    """
    Canonical Pydantic model for ONEX URIs.
    See docs/nodes/node_contracts.md and docs/nodes/structural_conventions.md for spec.
    """

    type: UriTypeEnum = Field(
        ...,
        description="ONEX URI type (tool, validator, agent, model, plugin, schema, node)",
    )
    namespace: str = Field(..., description="Namespace component of the URI")
    version_spec: str = Field(
        ..., description="Version specifier (semver or constraint)"
    )
    original: str = Field(..., description="Original URI string as provided")
