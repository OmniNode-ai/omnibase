# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "non_entrypoint"
# namespace: "omninode.tools.non_entrypoint"
# meta_type: "test_case"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:30:00+00:00"
# last_modified_at: "2025-05-07T11:30:00+00:00"
# entrypoint: "non_entrypoint.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTest']
# base_class: ['ProtocolTest']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Valid test case that is not an entrypoint.
"""

def some_function():
    """Some function."""
    return "Hello, World!" 