# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: yaml_serialization_mixin.py
# version: 1.0.0
# uuid: c6e00167-374c-4fed-a721-bf6cfcd45776
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163194
# last_modified_at: 2025-05-21T16:42:46.065153
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 04d7876252926007553dc122710d1047167261e81531f19cf98e7f617733484a
# entrypoint: {'type': 'python', 'target': 'yaml_serialization_mixin.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.yaml_serialization_mixin
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any

import yaml


class YAMLSerializationMixin:
    """
    Mixin for protocol-compliant YAML serialization with comment prefixing.
    Provides to_yaml_block(comment_prefix) for stamping and hashing.
    """

    def to_yaml_block(self: Any, comment_prefix: str) -> str:
        """
        Serialize the model as YAML, prefixing each line with comment_prefix.
        Ensures all Enums are serialized as their .value (mode='json').
        """
        # typing_and_protocols rule: ensure self is a model, not a dict
        if isinstance(self, dict):
            print(
                "[DEBUG] Converting self from dict to NodeMetadataBlock before model_dump (per typing_and_protocols rule)"
            )
            from omnibase.model.model_node_metadata import NodeMetadataBlock

            self = NodeMetadataBlock(**self)
        data = self.model_dump(mode="json")
        yaml_str = yaml.safe_dump(data, sort_keys=False)
        return "\n".join(
            f"{comment_prefix}{line}" if line.strip() else ""
            for line in yaml_str.splitlines()
        )
