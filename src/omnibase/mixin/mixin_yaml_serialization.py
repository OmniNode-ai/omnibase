# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_yaml_serialization.py
# version: 1.0.0
# uuid: af94dddd-cf94-4d45-9368-2c90c7804ad3
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.646053
# last_modified_at: 2025-05-28T17:20:05.463509
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4102c8cdaa7d4f2a0a24b4a561a985e7a6cc8937cacaf3dd55d2f8595d68cbcd
# entrypoint: python@mixin_yaml_serialization.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.mixin_yaml_serialization
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Any, Dict

import yaml

if TYPE_CHECKING:
    from typing import Protocol

    class HasModelDump(Protocol):
        def model_dump(self, mode: str = "json") -> Dict[str, Any]: ...


class YAMLSerializationMixin:
    """
    Pure mixin for protocol-compliant YAML serialization with comment prefixing.
    - Requires self to implement model_dump(mode="json") (e.g., Pydantic BaseModel).
    - No Protocol, no generics, no metaclass.
    - Compatible with Pydantic BaseModel inheritance.
    """

    def to_yaml_block(self: "HasModelDump", comment_prefix: str) -> str:
        """
        Serialize the model as YAML, prefixing each line with comment_prefix.
        Ensures all Enums are serialized as their .value (mode='json').
        Args:
            comment_prefix: String to prefix each line of YAML output.
        Returns:
            YAML string with each line prefixed by comment_prefix.
        """
        # Use to_serializable_dict if available (for compact entrypoint format)
        if hasattr(self, "to_serializable_dict"):
            data = self.to_serializable_dict()
        else:
            data = self.model_dump(mode="json")

        yaml_str = yaml.dump(
            data,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            indent=2,
            width=120,
        )
        yaml_str = yaml_str.replace("\xa0", " ")
        yaml_str = yaml_str.replace("\r\n", "\n").replace("\r", "\n")
        assert "\r" not in yaml_str, "Carriage return found in YAML string"
        yaml_str.encode("utf-8")
        if comment_prefix:
            yaml_str = "\n".join(
                f"{comment_prefix}{line}" if line.strip() else ""
                for line in yaml_str.splitlines()
            )
        return yaml_str
