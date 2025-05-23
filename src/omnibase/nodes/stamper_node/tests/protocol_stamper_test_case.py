# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_stamper_test_case.py
# version: 1.0.0
# uuid: 5afd9ea3-9475-42ce-b636-5cf0c3fe82fe
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.901199
# last_modified_at: 2025-05-22T20:48:07.416679
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 471dc2867549481aa504972f65797f9a91688e10769666d66c64701ee57b6181
# entrypoint: python@protocol_stamper_test_case.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_stamper_test_case
# meta_type: tool
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
