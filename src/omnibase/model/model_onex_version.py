# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_onex_version.py
# version: 1.0.0
# uuid: c9bbd897-24b2-4473-8d34-f30471f019e3
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.701759
# last_modified_at: 2025-05-22T21:19:13.628911
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 7e7544ab3dd055764d69fc54d2fc8378b6d57944b71559a9fb4b0e7e6f22ee6b
# entrypoint: python@model_onex_version.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_onex_version
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
