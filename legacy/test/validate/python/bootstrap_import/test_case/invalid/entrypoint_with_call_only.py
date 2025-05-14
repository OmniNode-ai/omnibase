# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "entrypoint_with_call_only"
# namespace: "omninode.tools.entrypoint_with_call_only"
# meta_type: "test_case"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:30:00+00:00"
# last_modified_at: "2025-05-07T11:30:00+00:00"
# entrypoint: "entrypoint_with_call_only.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTest']
# base_class: ['ProtocolTest']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Invalid test case that has bootstrap call but no import.
"""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    bootstrap()  # Missing import
    main() 