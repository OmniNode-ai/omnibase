# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_logging"
# namespace: "omninode.tools.test_python_fixture_logging"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:24+00:00"
# last_modified_at: "2025-05-05T13:00:24+00:00"
# entrypoint: "test_python_fixture_logging.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture']
# base_class: ['BaseTestFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Shared logging/caplog fixture for validator tests.
Fixture is registry-registered, DI-compliant, and provides log capture/assertion.
"""

import logging
from typing import Any

from foundation.script.validate.validate_registry import register_fixture
from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture


class CaplogFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for capturing log output in tests."""

    def get_fixture(self) -> Any:
        class CaplogContext:
            def __init__(self):
                self.records = []
                self.handler = logging.Handler()
                self.handler.emit = self.records.append

            def __enter__(self):
                logging.getLogger().addHandler(self.handler)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                logging.getLogger().removeHandler(self.handler)

        return CaplogContext


# Register the caplog fixture in the registry
register_fixture(
    name="caplog_fixture",
    fixture=CaplogFixture,
    description="Fixture for capturing log output in tests",
)