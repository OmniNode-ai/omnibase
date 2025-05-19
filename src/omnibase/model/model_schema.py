# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 71d41fb8-10dc-40be-a4cf-d6f8e1bcd760
# name: model_schema.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:56.056478
# last_modified_at: 2025-05-19T16:19:56.056479
# description: Stamped Python file: model_schema.py
# state_contract: none
# lifecycle: active
# hash: 6bf780285a1305f708536f9239368855df085865f625330618e106e55de8d144
# entrypoint: {'type': 'python', 'target': 'model_schema.py'}
# namespace: onex.stamped.model_schema.py
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
