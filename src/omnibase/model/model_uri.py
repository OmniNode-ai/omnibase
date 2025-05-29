# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.092013'
# description: Stamped by PythonHandler
# entrypoint: python://model_uri.py
# hash: 88945a0d83d0460d04fc3b46a84ec53c73db8f08c2166804ac9b8af25bcd9316
# last_modified_at: '2025-05-29T11:50:11.082634+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_uri.py
# namespace: omnibase.model_uri
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 0a5a30cb-c79b-4b9b-9b0d-701127774de4
# version: 1.0.0
# === /OmniNode:Metadata ===


from pydantic import BaseModel, Field

from omnibase.enums import UriTypeEnum


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
