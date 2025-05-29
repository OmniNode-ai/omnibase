# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.626805'
# description: Stamped by PythonHandler
# entrypoint: python://mixin_serializable.py
# hash: fb12f01e08e479102eab393bbaaf4ca3fef0a32842a42993861c538b3f23b6a0
# last_modified_at: '2025-05-29T11:50:10.885830+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: mixin_serializable.py
# namespace: omnibase.mixin_serializable
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: d32ee1eb-7b18-4898-af1d-f92ab0d70206
# version: 1.0.0
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
