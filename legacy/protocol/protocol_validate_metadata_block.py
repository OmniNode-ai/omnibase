# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_validate_metadata_block"
# namespace: "omninode.tools.protocol_validate_metadata_block"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:32+00:00"
# last_modified_at: "2025-05-05T13:00:32+00:00"
# entrypoint: "protocol_validate_metadata_block.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Optional
from pathlib import Path
from foundation.model.model_unified_result import UnifiedResultModel

class ProtocolValidateMetadataBlock(Protocol):
    """
    Protocol for metadata block validators. All implementations must provide validate() and get_name().
    """
    def validate(self, target: Path, config: Optional[dict] = None) -> UnifiedResultModel:
        ...
    def get_name(self) -> str:
        ...
    def validate_main(self, args) -> int:
        ... 