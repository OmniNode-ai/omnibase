# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 5f2047e5-3449-4184-9575-8c64140dc959
# name: yaml_serialization_mixin.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:04.712871
# last_modified_at: 2025-05-19T16:20:04.712874
# description: Stamped Python file: yaml_serialization_mixin.py
# state_contract: none
# lifecycle: active
# hash: 90123a0c71c687491743d09a9d6c1ccf26b80eb8aa072e7a5c554bacd764fb76
# entrypoint: {'type': 'python', 'target': 'yaml_serialization_mixin.py'}
# namespace: onex.stamped.yaml_serialization_mixin.py
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
        data = self.model_dump(mode="json")
        yaml_str = yaml.safe_dump(data, sort_keys=False)
        return "\n".join(
            f"{comment_prefix}{line}" if line.strip() else ""
            for line in yaml_str.splitlines()
        )
