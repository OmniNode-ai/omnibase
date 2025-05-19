# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: a05ffb76-78e8-46af-af1e-d063b50b66de
# name: model_file_reference.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:53.991454
# last_modified_at: 2025-05-19T16:19:53.991455
# description: Stamped Python file: model_file_reference.py
# state_contract: none
# lifecycle: active
# hash: 59000a34b52ca1178456670cc7abee1431e8ad842f1d2361773b74a815baf146
# entrypoint: {'type': 'python', 'target': 'model_file_reference.py'}
# namespace: onex.stamped.model_file_reference.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Optional

from pydantic import BaseModel


class FileReferenceModel(BaseModel):
    path: str  # Use str for now; can be changed to Path if needed
    description: Optional[str] = None
