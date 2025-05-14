# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_json_utils"
# namespace: "omninode.tools.common_json_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "common_json_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
common_json_utils.py
OmniNode Foundation: Shared JSON serialization utility for validators/tools.
"""
import json

def safe_json_dumps(obj, utility_registry) -> str:
    try:
        return json.dumps(obj)
    except Exception as e:
        return f"<json serialization error: {e}>" 