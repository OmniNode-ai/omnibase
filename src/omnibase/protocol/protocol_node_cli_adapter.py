# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_node_cli_adapter.py
# version: 1.0.0
# uuid: 2b17115e-19fe-4532-b440-52c8431c23d5
# author: OmniNode Team
# created_at: 2025-05-23T10:28:29.026261
# last_modified_at: 2025-05-23T17:42:52.028344
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: faa36bde09ecc4591bd8eef34a18d82e91356182165ec9d4fd2233c687983072
# entrypoint: python@protocol_node_cli_adapter.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_node_cli_adapter
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
