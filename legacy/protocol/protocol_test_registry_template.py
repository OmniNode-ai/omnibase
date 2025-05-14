# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_test_registry_template"
# namespace: "omninode.tools.protocol_test_registry_template"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-12T00:00:00+00:00"
# last_modified_at: "2025-05-12T00:00:00+00:00"
# entrypoint: "protocol_test_registry_template.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolTestRegistryTemplate"]
# base_class: ["object"]
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Protocol for registry test classes, specifying required test methods for the hybrid pattern.
"""
from typing import Protocol

class ProtocolTestRegistryTemplate(Protocol):
    def test_protocol_compliance(self) -> None: ...
    def test_registry_empty_before_registration(self) -> None: ...
    def test_register_and_lookup_templates(self) -> None: ... 