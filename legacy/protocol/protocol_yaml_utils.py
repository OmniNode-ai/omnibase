# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_yaml_utils"
# namespace: "omninode.tools.protocol_yaml_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-04T22:57:24+00:00"
# last_modified_at: "2025-05-04T22:57:24+00:00"
# entrypoint: "protocol_yaml_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Optional, Tuple, Any

class ProtocolYamlUtils(Protocol):
    def safe_yaml_load(self, content: str) -> Tuple[Optional[dict], Optional[str]]:
        """Safely load YAML content. Returns (data, error_message)."""
        ... 