# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_stamper_test_case.py
# version: 1.0.0
# uuid: 641d962d-bfac-40d7-8865-15990f60def9
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.754663
# last_modified_at: 2025-05-28T17:20:04.625514
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f609b18f140d50223d28a4cb9f8f345d73ad78c57aac4327b852f259c992b1b1
# entrypoint: python@protocol_stamper_test_case.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_stamper_test_case
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Dict, Optional, Protocol

from omnibase.enums import FileTypeEnum
from omnibase.model.model_onex_message_result import OnexStatus
from omnibase.metadata.metadata_constants import get_namespace_prefix


class ProtocolStamperTestCase(Protocol):
    id: str
    file_type: FileTypeEnum
    file_path: str
    file_content: str
    expected_status: OnexStatus
    expected_metadata: Optional[Dict[str, Any]]
    description: Optional[str]
