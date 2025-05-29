# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.813577'
# description: Stamped by PythonHandler
# entrypoint: python://template_type.py
# hash: f85c5e7815078648a0f99ed2bb11a9843d5ce4f62ff946049e456f28e536354b
# last_modified_at: '2025-05-29T11:50:10.781924+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: template_type.py
# namespace: omnibase.template_type
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 0546e615-0213-4b0a-8cac-b67d73a7c281
# version: 1.0.0
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
