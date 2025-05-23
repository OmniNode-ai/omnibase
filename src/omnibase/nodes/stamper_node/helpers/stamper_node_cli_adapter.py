# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: stamper_node_cli_adapter.py
# version: 1.0.0
# uuid: 5cf4f676-f83b-42b2-841c-53ca03cdbf4e
# author: OmniNode Team
# created_at: 2025-05-23T10:28:34.110776
# last_modified_at: 2025-05-23T17:42:52.034241
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9e0f4f5713dba59cba181f12f56a3539c4575ca00c96aaa3de958fa25f441aba
# entrypoint: python@stamper_node_cli_adapter.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.stamper_node_cli_adapter
# meta_type: tool
# === /OmniNode:Metadata ===


import argparse

from omnibase.nodes.stamper_node.models.state import StamperInputState
from omnibase.protocol.protocol_node_cli_adapter import ProtocolNodeCliAdapter
from omnibase.runtime.utils.onex_version_loader import OnexVersionLoader


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
        schema_version = OnexVersionLoader().get_onex_versions().schema_version
        return StamperInputState(
            file_path=args.file_path,
            author=args.author,
            version=schema_version,
        )
