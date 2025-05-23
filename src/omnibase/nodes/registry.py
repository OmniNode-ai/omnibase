# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: registry.py
# version: 1.0.0
# uuid: 86e95fa9-5cb5-4040-b58e-932206bf99d7
# author: OmniNode Team
# created_at: 2025-05-23T14:27:53.067433
# last_modified_at: 2025-05-23T20:18:58.592961
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4713224bc254d158c1fc92b697e456ffc66bfe0c8c3620b983cbfb166948ec8e
# entrypoint: python@registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.registry
# meta_type: tool
# === /OmniNode:Metadata ===


# Node CLI Registry (interim solution)
# This will be replaced by a dynamic plugin/registry system in a future milestone.

from omnibase.nodes.stamper_node.v1_0_0.cli_stamp import app as stamper_cli_app

NODE_CLI_REGISTRY = {
    "stamper_node@v1_0_0": stamper_cli_app,
    # Add other nodes/versions as needed
}
