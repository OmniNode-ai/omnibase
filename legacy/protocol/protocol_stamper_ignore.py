# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_stamper_ignore"
# namespace: "omninode.tools.protocol_stamper_ignore"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-04T15:04:46+00:00"
# last_modified_at: "2025-05-04T15:04:46+00:00"
# entrypoint: "protocol_stamper_ignore.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, List

class ProtocolStamperIgnore(Protocol):
    def get_ignore_files(self) -> List[str]:
        ... 