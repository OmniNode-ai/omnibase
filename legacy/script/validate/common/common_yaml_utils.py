# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_yaml_utils"
# namespace: "omninode.tools.common_yaml_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "common_yaml_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolYamlUtils']
# base_class: ['ProtocolYamlUtils']
# mock_safe: true
# === /OmniNode:Metadata ===



from typing import Optional, Tuple, Any
import yaml
from foundation.protocol.protocol_yaml_utils import ProtocolYamlUtils

class YamlUtils(ProtocolYamlUtils):
    def safe_yaml_load(self, content: str) -> Tuple[Optional[dict], Optional[str]]:
        """Safely load YAML content. Returns (data, error_message)."""
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                return None, "YAML content is not a dictionary."
            return data, None
        except Exception as e:
            return None, str(e)

# Singleton instance for use
yaml_utils = YamlUtils()

# Add utility_registry as an argument to functions/classes that require it, or retrieve from DI container
# utility_registry.register('yaml_utils', yaml_utils) 