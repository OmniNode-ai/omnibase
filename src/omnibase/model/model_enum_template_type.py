# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_enum_template_type.py
# version: 1.0.0
# uuid: e90c010e-0b00-4dc5-a7d7-d1c540b06b02
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165419
# last_modified_at: 2025-05-21T16:42:46.044499
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 60a9a4ef61b042df4e1883e4af05b6322c99bcabd51acd75bf9edab9a0e5f6cb
# entrypoint: {'type': 'python', 'target': 'model_enum_template_type.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_enum_template_type
# meta_type: tool
# === /OmniNode:Metadata ===

from enum import Enum


class TemplateTypeEnum(str, Enum):
    """
    Canonical template types for metadata stamping and registry.
    """

    MINIMAL = "minimal"
    EXTENDED = "extended"
    YAML = "yaml"
    MARKDOWN = "markdown"
