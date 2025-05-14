# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "invalid_code_quality_bad_code"
# namespace: "omninode.tools.invalid_code_quality_bad_code"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:20+00:00"
# last_modified_at: "2025-05-05T13:00:20+00:00"
# entrypoint: "invalid_code_quality_bad_code.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

def very_long_function():
    a = 0
    for i in range(100):
        a += i
        for j in range(100):
            a += j
            for k in range(100):
                a += k
    return a