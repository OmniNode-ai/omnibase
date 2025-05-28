# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_node_runner.py
# version: 1.0.0
# uuid: 8ac235b7-27e0-4431-9cae-789ee1996d0d
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.223369
# last_modified_at: 2025-05-28T17:20:04.409250
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 85981f45e49523af0805ad26c9b721717bc2db48a1f05d41d55798f5731a598b
# entrypoint: python@protocol_node_runner.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_node_runner
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Protocol


class ProtocolNodeRunner(Protocol):
    """
    Canonical protocol for ONEX node runners (runtime/ placement).
    Requires a run(*args, **kwargs) -> Any method for node execution and event emission.
    All node runner implementations must conform to this interface.
    """

    def run(self, *args: Any, **kwargs: Any) -> Any: ...
