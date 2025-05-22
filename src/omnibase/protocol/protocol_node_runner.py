# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_node_runner.py
# version: 1.0.0
# uuid: d7d2d8cc-365b-41e4-9117-8c39685100e1
# author: OmniNode Team
# created_at: 2025-05-22T05:34:29.792572
# last_modified_at: 2025-05-22T20:50:39.708144
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 39476bcfd37a557da05671076ae497d42f9c4ed2ac268d77004a2f0ae81f1c46
# entrypoint: python@protocol_node_runner.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_node_runner
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
