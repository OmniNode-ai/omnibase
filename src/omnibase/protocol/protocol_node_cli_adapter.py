# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_node_cli_adapter.py
# version: 1.0.0
# uuid: e1f3e769-a996-476e-a659-34ec8a77dee2
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.212774
# last_modified_at: 2025-05-28T17:20:04.643219
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9b6b30cca8632c891b304334b6ab601d9cbea4a8acd218e088d255dd85463e92
# entrypoint: python@protocol_node_cli_adapter.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_node_cli_adapter
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Protocol


class ProtocolNodeCliAdapter(Protocol):
    """
    Protocol for ONEX node CLI adapters. Converts CLI args to node input state.
    Implementations must provide a method to parse CLI args (list[str] or argparse.Namespace)
    and return the node's input state (e.g., StamperInputState).
    """

    def parse_cli_args(self, cli_args: list[str]) -> Any: ...
