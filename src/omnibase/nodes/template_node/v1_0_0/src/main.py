# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: main.py
# version: 1.0.0
# uuid: 99d1613e-974d-49e6-bddb-978194339ceb
# author: OmniNode Team
# created_at: 2025-05-24T09:35:52.271253
# last_modified_at: 2025-05-24T13:39:57.887030
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8707444c9773a64fcc9776aeb5d5627526d7a1292bb125e6f4b3462602d1bae5
# entrypoint: python@main.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.main
# meta_type: tool
# === /OmniNode:Metadata ===


"""
TEMPLATE: Main entrypoint for template_node.

This file serves as the canonical entrypoint for the template_node.
Replace the import and function call with your node's implementation.
"""

# TEMPLATE: Update this import to match your state models
from ..models.state import TemplateInputState, TemplateOutputState

# TEMPLATE: Update this import to match your node's main function
from ..node import run_template_node

# Re-export the main function for external use
# TEMPLATE: Update the function name to match your node
__all__ = ["run_template_node", "TemplateInputState", "TemplateOutputState"]

if __name__ == "__main__":
    # TEMPLATE: Update this to call your node's main function
    from ..node import main

    main()
