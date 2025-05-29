# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.688102'
# description: Stamped by PythonHandler
# entrypoint: python://model_onex_version.py
# hash: 605538ba887b61c860f6665f3b4a52f389993b353e84563be6435fdbf574b5cd
# last_modified_at: '2025-05-29T11:50:11.021200+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onex_version.py
# namespace: omnibase.model_onex_version
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: ec6d12ec-f21d-4dd0-934f-31c62882f282
# version: 1.0.0
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
