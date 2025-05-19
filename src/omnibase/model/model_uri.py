# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 8cb333a3-b964-4d32-b2cd-d611165bf1db
# name: model_uri.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.900836
# last_modified_at: 2025-05-19T16:19:52.900837
# description: Stamped Python file: model_uri.py
# state_contract: none
# lifecycle: active
# hash: 79bb784e171ee9e7d4e0a3cffff4b0581b987f7f42bc067d401f8f3e4b4da7dd
# entrypoint: {'type': 'python', 'target': 'model_uri.py'}
# namespace: onex.stamped.model_uri.py
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
