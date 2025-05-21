# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_file_reference.py
# version: 1.0.0
# uuid: 83f88ff9-16f7-4b9c-8d66-e959f3e7b61e
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165564
# last_modified_at: 2025-05-21T16:42:46.069661
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 0c59baded2e2c7184f4cd87018cee41dce0dd9ccfea4a9d50d0098f50f62f36d
# entrypoint: {'type': 'python', 'target': 'model_file_reference.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_file_reference
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Optional

from pydantic import BaseModel


class FileReferenceModel(BaseModel):
    path: str  # Use str for now; can be changed to Path if needed
    description: Optional[str] = None
