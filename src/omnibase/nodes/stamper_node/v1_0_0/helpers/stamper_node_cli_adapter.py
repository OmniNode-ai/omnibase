# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.651644'
# description: Stamped by PythonHandler
# entrypoint: python://stamper_node_cli_adapter.py
# hash: e3fe2451848589a5d649d450b089983d4ecd8f967f75a85087989277fcd68e80
# last_modified_at: '2025-05-29T11:50:11.738502+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: stamper_node_cli_adapter.py
# namespace: omnibase.stamper_node_cli_adapter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4040f584-4482-4fec-80ae-bef13e1386cf
# version: 1.0.0
# === /OmniNode:Metadata ===


import argparse

from omnibase.protocol.protocol_node_cli_adapter import ProtocolNodeCliAdapter

from ..models.state import StamperInputState, create_stamper_input_state


class StamperNodeCliAdapter(ProtocolNodeCliAdapter):
    """
    Canonical CLI adapter for stamper_node. Converts CLI args to StamperInputState.
    """

    def parse_cli_args(self, cli_args: list[str]) -> StamperInputState:
        parser = argparse.ArgumentParser(description="ONEX Stamper Node CLI Adapter")
        parser.add_argument("file_path", type=str, help="Path to file to stamp")
        parser.add_argument(
            "--author", type=str, default="OmniNode Team", help="Author name"
        )
        args = parser.parse_args(cli_args)

        # Use factory function to create input state with proper version handling
        return create_stamper_input_state(file_path=args.file_path, author=args.author)
