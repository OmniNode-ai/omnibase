# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 88e1d734-8e04-4fdd-b81c-69bf2f3eb9a1
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.707298
# last_modified_at: 2025-05-22T21:19:13.462454
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d4298116406c04c5905fc5e7319f8f18682d5ed541cf3195fdba7761f369fe1d
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.state
# meta_type: tool
# === /OmniNode:Metadata ===


from pydantic import BaseModel


class StamperInputState(BaseModel):
    """Input state contract for the stamper node (node-local).

    version: Schema version for input state (must be injected at construction).
    """

    version: str
    file_path: str
    author: str = "OmniNode Team"
    # Add more fields as needed


class StamperOutputState(BaseModel):
    """Output state contract for the stamper node (node-local).

    version: Schema version for output state (must be injected at construction).
    """

    version: str
    status: str
    message: str
    # Add more fields as needed
