# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_registry_test_case"
# namespace: "omninode.tools.protocol_registry_test_case"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:32+00:00"
# last_modified_at: "2025-05-05T13:00:32+00:00"
# entrypoint: "protocol_registry_test_case.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import List, Protocol


class ProtocolRegistryTestCase(Protocol):
    def get_test_case(self, validator: str, name: str, case_type: str) -> str:
        """Return the absolute path to the test case file for the given validator, name, and case type (valid/invalid)."""
        ...

    def list_test_cases(self, validator: str, case_type: str) -> List[str]:
        """Return a list of all test case file names for the given validator and case type (valid/invalid)."""
        ...