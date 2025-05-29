# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.382516'
# description: Stamped by PythonHandler
# entrypoint: python://registry.py
# hash: 010190fdca4198db61756702bf298780bdd19d6bb31185793c3e9cb74569fefe
# last_modified_at: '2025-05-29T11:50:11.631835+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: registry.py
# namespace: omnibase.registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e80cc5d6-56cf-4e99-9651-4f4ca882d4bd
# version: 1.0.0
# === /OmniNode:Metadata ===


# Node CLI Registry (interim solution)
# This will be replaced by a dynamic plugin/registry system in a future milestone.

from omnibase.nodes.stamper_node.v1_0_0.cli_stamp import app as stamper_cli_app

NODE_CLI_REGISTRY = {
    "stamper_node@v1_0_0": stamper_cli_app,
    # Add other nodes/versions as needed
}
