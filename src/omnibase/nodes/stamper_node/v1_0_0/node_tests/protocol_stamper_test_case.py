# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.754663'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_stamper_test_case.py
# hash: d97d00535fca6795462e1abcd997d177d27f39e376a864b9ee62f1c11a84b16e
# last_modified_at: '2025-05-29T11:50:11.793427+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_stamper_test_case.py
# namespace: omnibase.protocol_stamper_test_case
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 641d962d-bfac-40d7-8865-15990f60def9
# version: 1.0.0
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
