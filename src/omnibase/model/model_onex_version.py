# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_onex_version.py
# version: 1.0.0
# uuid: ec6d12ec-f21d-4dd0-934f-31c62882f282
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.688102
# last_modified_at: 2025-05-28T17:20:04.261810
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c65f06cb1ee6623f71bee7132d107265d202f94ec8793412dab33281dff3c65c
# entrypoint: python@model_onex_version.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.model_onex_version
# meta_type: tool
# === /OmniNode:Metadata ===


from pydantic import BaseModel


class OnexVersionInfo(BaseModel):
    """
    Canonical Pydantic model for ONEX version information.
    Fields:
        metadata_version (str): The metadata schema version.
        protocol_version (str): The protocol version.
        schema_version (str): The schema version.
    """

    metadata_version: str
    protocol_version: str
    schema_version: str
