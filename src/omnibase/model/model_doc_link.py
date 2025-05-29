# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.906782'
# description: Stamped by PythonHandler
# entrypoint: python://model_doc_link.py
# hash: 2cb0ad449c7fab1d253bd74e9195dcac5bab7253a5b1ac5d8a3845c7d633c29a
# last_modified_at: '2025-05-29T11:50:10.930558+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_doc_link.py
# namespace: omnibase.model_doc_link
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 2143088c-92c9-4de5-bc43-4d7628509dcb
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Optional

from pydantic import BaseModel


class DocLinkModel(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
