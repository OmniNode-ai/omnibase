# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 2403f1fb-9605-4bc3-8a53-dd240220a1e8
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.968817
# last_modified_at: 2025-05-24T13:39:57.891980
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9cdf081abf61fa062af9e2bdc49212b08cf963b08d82708e179d399494f6e5d1
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.state
# meta_type: tool
# === /OmniNode:Metadata ===


"""
TEMPLATE: State models for template_node.

Replace this docstring with a description of your node's state models.
Update the class names, fields, and validation logic as needed.
"""

from typing import Optional

from pydantic import BaseModel


class TemplateInputState(BaseModel):
    """
    TEMPLATE: Input state model for template_node.

    Replace this with your node's input requirements.
    Update field names, types, and validation as needed.
    """

    version: str  # Schema version for input state
    # TEMPLATE: Replace with your required input fields
    template_required_field: (
        str  # TEMPLATE: Replace with your required input field description
    )
    # TEMPLATE: Replace with your optional input fields
    template_optional_field: Optional[str] = (
        "TEMPLATE_DEFAULT_VALUE"  # TEMPLATE: Replace with your optional input field description
    )


class TemplateOutputState(BaseModel):
    """
    TEMPLATE: Output state model for template_node.

    Replace this with your node's output structure.
    Update field names, types, and validation as needed.
    """

    version: str  # Schema version for output state (matches input)
    status: str  # Execution status: success|failure|warning
    message: str  # Human-readable result message
    # TEMPLATE: Replace with your output fields
    template_output_field: Optional[str] = (
        None  # TEMPLATE: Replace with your output field description
    )


# TEMPLATE: Add any additional state models your node needs
class TemplateAdditionalState(BaseModel):
    """
    TEMPLATE: Additional state model if needed.

    Delete this if not needed, or replace with your additional state models.
    """

    template_field: str  # TEMPLATE: Replace with your field description
