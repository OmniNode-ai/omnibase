# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_doc_link.py
# version: 1.0.0
# uuid: c68bca36-a993-47c2-8327-b43242b8062d
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164915
# last_modified_at: 2025-05-21T16:42:46.063616
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d09b259ebe832425c9ce7e33381edca95297a5072d4bdca385a8e89cfd32eda0
# entrypoint: {'type': 'python', 'target': 'model_doc_link.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_doc_link
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Optional

from pydantic import BaseModel


class DocLinkModel(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
