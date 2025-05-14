#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_scanner_extra"
# namespace: "omninode.tools.test_stub_scanner_extra"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:27+00:00"
# last_modified_at: "2025-05-05T13:00:27+00:00"
# entrypoint: "test_stub_scanner_extra.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""scanner.py
containers.foundation.src.foundation.script.validation.test_stub.scanner.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""


# Config: Thresholds for what's considered "excessive"
DEFAULT_MOCK_RATIO_THRESHOLD = 3
DEFAULT_MOCK_ABSOLUTE_THRESHOLD = 10
DEFAULT_PATCH_THRESHOLD = 5

MOCK_PATTERNS = {
    "patch_decorator": r"@patch\([\'\"](.+?)[\'\"]\)",
    "mock_call": r"(MagicMock|Mock|patch|mock)\([^\)]*\)",
    "async_mock": r"AsyncMock\([^\)]*\)",
    "mock_return": r"\.return_value",
    "mock_side_effect": r"\.side_effect",
    "assert_called": r"assert_called",
    "assert_not_called": r"assert_not_called",
}

ASSERTION_PATTERNS = {
    "pytest_assert": r"assert\s+.+",
    "unittest_assert": r"self\.assert\w+\(",
    "pytest_raises": r"pytest\.raises",
}


class TestStubScanner:
    """Scanner for identifying excessive stubbing in tests."""

    # .. (copy all methods from the original TestStubScanner class)
    # .. existing code ..