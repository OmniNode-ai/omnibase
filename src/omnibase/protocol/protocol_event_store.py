# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.138714'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_event_store.py
# hash: 8499949482530fa069fc79a1a97298ad0f4e57b634d784f2504868e71043a1a3
# last_modified_at: '2025-05-29T11:50:12.093868+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_event_store.py
# namespace: omnibase.protocol_event_store
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: ede6a46e-5aa6-45de-aed6-b3cdf6e00d36
# version: 1.0.0
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
