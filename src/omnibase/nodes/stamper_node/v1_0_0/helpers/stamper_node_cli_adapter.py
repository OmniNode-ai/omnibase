# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: stamper_node_cli_adapter.py
# version: 1.0.0
# uuid: 4040f584-4482-4fec-80ae-bef13e1386cf
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.651644
# last_modified_at: 2025-05-28T17:20:04.276237
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b3ca197d4e142e5fdd6a96646cc1dfd43d81ca59210594504cbc28855438f28a
# entrypoint: python@stamper_node_cli_adapter.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.stamper_node_cli_adapter
# meta_type: tool
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
