# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_schema.py
# version: 1.0.0
# uuid: 5969cf5b-0da5-4c89-9867-8859e8184773
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166458
# last_modified_at: 2025-05-21T16:42:46.078121
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8a8b6a3415e65146efef5e91ada49af571b50e83c2fbfd1a262b019187e86aab
# entrypoint: python@model_schema.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_schema
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SchemaModel(BaseModel):
    """
    Minimal Pydantic model for ONEX JSON schema files.
    Includes canonical fields and is extensible for M1+.
    """

    schema_uri: Optional[str] = Field(None)
    title: Optional[str] = None
    type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None
    # TODO: Add more fields and validation logic in M1+
