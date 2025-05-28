# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_serializable.py
# version: 1.0.0
# uuid: d32ee1eb-7b18-4898-af1d-f92ab0d70206
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.626805
# last_modified_at: 2025-05-28T17:20:03.920477
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: be9bda639926164fc95888bb66cf507d99afd5f109f487c8d86a42374e8bf6af
# entrypoint: python@mixin_serializable.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.mixin_serializable
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
