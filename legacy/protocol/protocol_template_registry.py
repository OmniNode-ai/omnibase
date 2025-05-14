# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_registry_template"
# namespace: "omninode.tools.protocol_registry_template"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-12T00:00:00+00:00"
# last_modified_at: "2025-05-12T00:00:00+00:00"
# entrypoint: "protocol_registry_template.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["RegistryProtocol"]
# base_class: ["RegistryProtocol"]
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Protocol for template registries, extending RegistryProtocol with template-specific methods.
"""
from foundation.protocol.protocol_registry import RegistryProtocol
from typing import Protocol, Optional, runtime_checkable

@runtime_checkable
class ProtocolRegistryTemplate(RegistryProtocol, Protocol):
    def register_templates(self) -> None:
        ...
    def get_template_for_extension(self, ext: str) -> Optional[str]:
        ... 