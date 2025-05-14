# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "__init__"
# namespace: "omninode.tools.__init__"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:25+00:00"
# last_modified_at: "2025-05-05T13:00:25+00:00"
# entrypoint: "__init__.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Abstract base class for all shared test fixture in the foundation container.
All fixture must inherit from this class, be registry-registered, and support DI.
"""

from typing import Any, Protocol


class BaseTestFixture(Protocol):
    """Protocol for all test fixtures. Must be registry-registered and DI-compliant."""
    def get_fixture(self, *args, **kwargs) -> Any:
        """Return the fixture instance or value. Must be implemented by all concrete fixture."""
        pass