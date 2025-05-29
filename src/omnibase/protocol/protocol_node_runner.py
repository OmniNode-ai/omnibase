# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.223369'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_node_runner.py
# hash: 1d89fe906987f419c1d7a6b1b26b93e026d114f687f114142cc213da06458252
# last_modified_at: '2025-05-29T11:50:12.146490+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_node_runner.py
# namespace: omnibase.protocol_node_runner
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8ac235b7-27e0-4431-9cae-789ee1996d0d
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Protocol


class ProtocolNodeRunner(Protocol):
    """
    Canonical protocol for ONEX node runners (runtime/ placement).
    Requires a run(*args, **kwargs) -> Any method for node execution and event emission.
    All node runner implementations must conform to this interface.
    """

    def run(self, *args: Any, **kwargs: Any) -> Any: ...
