# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_event_store.py
# version: 1.0.0
# uuid: d610832a-44a6-4176-9f65-c5b60bef20e8
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.711280
# last_modified_at: 2025-05-22T21:19:13.630283
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3abd7a3515ac2ca973bd54d1fffd55d51f90fce642562dae366d670b4acc14b1
# entrypoint: python@protocol_event_store.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_event_store
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_onex_event import OnexEvent


class ProtocolEventStore(Protocol):
    """
    Canonical protocol for ONEX event stores (runtime/ placement).
    Requires store_event(event: OnexEvent) -> None and close() -> None methods for event durability.
    All event store implementations must conform to this interface.
    """

    def store_event(self, event: OnexEvent) -> None: ...

    def close(self) -> None: ...
