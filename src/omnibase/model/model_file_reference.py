# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.930335'
# description: Stamped by PythonHandler
# entrypoint: python://model_file_reference.py
# hash: 78decacded4ccce23e10b5b17474226cadcef3eacb4ee02c1625f948035d09bc
# last_modified_at: '2025-05-29T11:50:10.941744+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_file_reference.py
# namespace: omnibase.model_file_reference
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: a6123e65-a025-4a18-a21b-1d5675103033
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Optional

from pydantic import BaseModel


class FileReferenceModel(BaseModel):
    path: str  # Use str for now; can be changed to Path if needed
    description: Optional[str] = None
