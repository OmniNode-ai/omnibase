# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_serializable.py
# version: 1.0.0
# uuid: 99e01b2b-1d7a-4da8-a2f1-b9c75caf1832
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.897827
# last_modified_at: 2025-05-22T20:27:53.683827
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 19ccf500a793b649615f285d57a26dfaa83c996df73b79d3b4e28f831f9252b7
# entrypoint: python@mixin_serializable.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_serializable
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Dict, Protocol, Type, TypeVar

T = TypeVar("T", bound="SerializableMixin")


class SerializableMixin(Protocol):
    """
    Protocol for models that support recursive, protocol-driven serialization for ONEX/OmniNode file/block I/O.
    Implementations must provide:
      - to_serializable_dict(self) -> dict: Recursively serialize self and all sub-models, lists, dicts, and enums.
      - from_serializable_dict(cls, data: dict) -> Self: Recursively reconstruct the model and all sub-models from dicts.
    This protocol is foundational and should be implemented by any model intended for canonical serialization or deserialization.
    """

    def to_serializable_dict(self: T) -> Dict[str, Any]: ...

    @classmethod
    def from_serializable_dict(cls: Type[T], data: Dict[str, Any]) -> T: ...
