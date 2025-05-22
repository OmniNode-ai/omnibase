# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_serializable.py
# version: 1.0.0
# uuid: '99e01b2b-1d7a-4da8-a2f1-b9c75caf1832'
# author: OmniNode Team
# created_at: '2025-05-22T14:03:21.897827'
# last_modified_at: '2025-05-22T18:05:26.906564'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: mixin_serializable.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_serializable
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
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
