# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "conftest"
# namespace: "omninode.tools.conftest"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:13+00:00"
# last_modified_at: "2025-05-05T13:00:13+00:00"
# entrypoint: "conftest.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

try:
    from foundation.test.unit.validation.test_helpers import TestHelper

    register_fixture(
        name="test_helper",
        fixture=TestHelper,
        description="Test helper for validator error/warning assertions.",
        interface=ITestHelper,
    )
except ImportError:
    pass  # Allow registry to load even if test_helpers is not available in some environments

from foundation.fixture.fixture_registry import *
from foundation.fixture.fixture_registry import setup_test_fixtures
setup_test_fixtures()

import pytest
import foundation.fixture.validator.python.python_fixture_container
from foundation.script.orchestrator.shared.shared_output_formatter import SharedOutputFormatter

@pytest.fixture(autouse=True, scope="session")
def _register_utilities():
    # Ensure file_utils and yaml_utils are registered in utility_registry for all tests
    import foundation.script.validate.common.common_file_utils  # noqa: F401
    import foundation.script.validate.common.common_yaml_utils  # noqa: F401

@pytest.fixture(scope="session")
def output_formatter():
    # DI-compliant: provided by test harness, not test file
    return SharedOutputFormatter()