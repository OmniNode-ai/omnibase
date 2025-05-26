# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: template_type.py
# version: 1.0.0
# uuid: e90c010e-0b00-4dc5-a7d7-d1c540b06b02
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165419
# last_modified_at: 2025-05-26T18:58:45.686497
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ffdab0eb05014ad2a0568c5977f59e03788e21b45d03a7af2f6bb26fe95471bd
# entrypoint: python@template_type.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.template_type
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
