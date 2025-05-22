# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_yaml_serialization.py
# version: 1.0.0
# uuid: a41ba62a-36d2-4ade-ae80-1431cfb76738
# author: OmniNode Team
# created_at: 2025-05-22T14:05:24.976763
# last_modified_at: 2025-05-22T20:44:58.960712
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ff710b3b45d18830e05826457de9c315e3fe538267d4527d3e2ec160e3a9e63c
# entrypoint: python@mixin_yaml_serialization.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_yaml_serialization
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
        data = self.model_dump(mode="json")
        yaml_str = yaml.dump(
            data, sort_keys=True, default_flow_style=False, allow_unicode=True
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
