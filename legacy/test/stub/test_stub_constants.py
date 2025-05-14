#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_constants"
# namespace: "omninode.tools.test_stub_constants"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:27+00:00"
# last_modified_at: "2025-05-05T13:00:27+00:00"
# entrypoint: "test_stub_constants.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""test_stub_constants.py containers.foundation.src.foundation.script.validati
on.test_stub.test_stub_constants.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

# --- Move MOCK_PATTERNS, ASSERTION_PATTERNS, and threshold defaults here from validate_test_stub.py ---

DEFAULT_MOCK_RATIO_THRESHOLD = 3  # Mocks:Assertions ratio
DEFAULT_MOCK_ABSOLUTE_THRESHOLD = 10  # Absolute number of mocks
DEFAULT_PATCH_THRESHOLD = 5  # Number of patched functions/methods

MOCK_PATTERNS = {
    "patch_decorator": r'@patch\([\'"](.+?)[\'"]\)',
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