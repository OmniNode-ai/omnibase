# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_registry_consistency"
# namespace: "omninode.tools.test_python_fixture_registry_consistency"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:24+00:00"
# last_modified_at: "2025-05-05T13:00:24+00:00"
# entrypoint: "test_python_fixture_registry_consistency.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
DI/registry-compliant fixture for PythonValidateRegistryConsistency (Python)
"""

from foundation.script.validate.python.python_validate_registry_consistency import PythonValidateRegistryConsistency
from foundation.script.validate.validate_registry import register_fixture

class PythonTestFixtureRegistryConsistency:
    """Fixture for DI-compliant instantiation of PythonValidateRegistryConsistency."""
    def get_fixture(self, **kwargs):
        return PythonValidateRegistryConsistency(**kwargs)

register_fixture(
    name="python_test_fixture_registry_consistency",
    fixture=PythonTestFixtureRegistryConsistency,
    description="DI/registry-compliant fixture for PythonValidateRegistryConsistency (Python)",
) 