# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 3ba19b30-a3e5-4a06-b3a8-e55c437f4408
# name: model_doc_link.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:57.253092
# last_modified_at: 2025-05-19T16:19:57.253093
# description: Stamped Python file: model_doc_link.py
# state_contract: none
# lifecycle: active
# hash: d42c56d4059cca2032853db67ba982267ad671e4cf60d59b8fb112a826b54e02
# entrypoint: {'type': 'python', 'target': 'model_doc_link.py'}
# namespace: onex.stamped.model_doc_link.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Optional

from pydantic import BaseModel


class DocLinkModel(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
