# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: registry.py
# version: 1.0.0
# uuid: e80cc5d6-56cf-4e99-9651-4f4ca882d4bd
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.382516
# last_modified_at: 2025-05-28T17:20:04.649844
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4b21cd3f8b99ff0cebdd2d38e8f87a06b5b729062b4d0efc9bc1c41d71c0d38b
# entrypoint: python@registry.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.registry
# meta_type: tool
# === /OmniNode:Metadata ===


# Node CLI Registry (interim solution)
# This will be replaced by a dynamic plugin/registry system in a future milestone.

from omnibase.nodes.stamper_node.v1_0_0.cli_stamp import app as stamper_cli_app

NODE_CLI_REGISTRY = {
    "stamper_node@v1_0_0": stamper_cli_app,
    # Add other nodes/versions as needed
}
