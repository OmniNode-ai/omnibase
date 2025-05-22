# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_metadata_config.py
# version: 1.0.0
# uuid: 63881d65-745a-4c13-8f72-b69f61f1277a
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165778
# last_modified_at: 2025-05-21T16:42:46.081557
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6059e7280d56b8087a37a5cf2e1f8531575c0274a070a6856e09a29266f19334
# entrypoint: python@model_metadata_config.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_metadata_config
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Dict, Optional

from pydantic import BaseModel


class MetadataConfigModel(BaseModel):
    # Example config fields; add more as needed
    timeout: Optional[int] = None
    retries: Optional[int] = None
    enable_cache: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None  # Arbitrary settings, extensible
    # Arbitrary extra fields allowed for extensibility
    model_config = {"extra": "allow"}
