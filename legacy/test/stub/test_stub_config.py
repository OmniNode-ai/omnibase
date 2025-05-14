# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_config"
# namespace: "omninode.tools.test_stub_config"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:26+00:00"
# last_modified_at: "2025-05-05T13:00:26+00:00"
# entrypoint: "test_stub_config.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ValidatorConfig']
# base_class: ['ValidatorConfig']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from foundation.base.model_base import ValidatorConfig
from pydantic import Field

# Config: Thresholds for what's considered "excessive"
DEFAULT_MOCK_RATIO_THRESHOLD = 3  # Mocks:Assertions ratio
DEFAULT_MOCK_ABSOLUTE_THRESHOLD = 10  # Absolute number of mocks
DEFAULT_PATCH_THRESHOLD = 5  # Number of patched functions/methods

# Regular expressions for identifying mocks and stubs
MOCK_PATTERNS = {
    "patch_decorator": r"@patch\([\'\"](.+?)[\'\"]\)",
    "mock_call": r"(MagicMock|Mock|patch|mock)\([^\)]*\)",
    "async_mock": r"AsyncMock\([^\)]*\)",
    "mock_return": r"\.return_value",
    "mock_side_effect": r"\.side_effect",
    "assert_called": r"assert_called",
    "assert_not_called": r"assert_not_called",
}

# Patterns for identifying test assertions
ASSERTION_PATTERNS = {
    "pytest_assert": r"assert\s+.+",
    "unittest_assert": r"self\.assert\w+\(",
    "pytest_raises": r"pytest\.raises",
}


class TestStubScannerConfig(ValidatorConfig):
    version: str = "v1"
    mock_ratio_threshold: float = Field(
        default=0.5, description="Max allowed ratio of mocks to assertions"
    )
    mock_absolute_threshold: int = Field(
        default=5, description="Max allowed number of mocks per test"
    )
    patch_threshold: int = Field(
        default=3, description="Max allowed number of patches per test"
    )
    verbose: bool = False
    staged_only: bool = False