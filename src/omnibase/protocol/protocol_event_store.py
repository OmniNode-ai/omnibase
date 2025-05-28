# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_event_store.py
# version: 1.0.0
# uuid: ede6a46e-5aa6-45de-aed6-b3cdf6e00d36
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.138714
# last_modified_at: 2025-05-28T17:20:04.076397
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 59e4f18327406b45823d5cac6cd805bcc61b734d88f2f8ee9b6206fdc92a7b2b
# entrypoint: python@protocol_event_store.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_event_store
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
