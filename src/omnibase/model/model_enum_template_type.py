# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: f756804e-09d6-4edc-bbab-ffa3771dea35
# name: model_enum_template_type.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:54.833312
# last_modified_at: 2025-05-19T16:19:54.833313
# description: Stamped Python file: model_enum_template_type.py
# state_contract: none
# lifecycle: active
# hash: d5b0dff740e189a45780e892ed92f4990b29d6f67df3e099749034db5f8a676d
# entrypoint: {'type': 'python', 'target': 'model_enum_template_type.py'}
# namespace: onex.stamped.model_enum_template_type.py
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
