# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_stamper_test_case.py
# version: 1.0.0
# uuid: '5afd9ea3-9475-42ce-b636-5cf0c3fe82fe'
# author: OmniNode Team
# created_at: '2025-05-22T14:03:21.901199'
# last_modified_at: '2025-05-22T18:05:26.837659'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: protocol_stamper_test_case.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_stamper_test_case
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


from typing import Any, Dict, Optional, Protocol

from omnibase.model.model_enum_file_type import FileTypeEnum
from omnibase.model.model_onex_message_result import OnexStatus


class ProtocolStamperTestCase(Protocol):
    id: str
    file_type: FileTypeEnum
    file_path: str
    file_content: str
    expected_status: OnexStatus
    expected_metadata: Optional[Dict[str, Any]]
    description: Optional[str]
