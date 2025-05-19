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
