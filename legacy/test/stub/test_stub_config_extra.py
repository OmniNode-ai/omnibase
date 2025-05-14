#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_stub_config_extra"
# namespace: "omninode.tools.test_stub_config_extra"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:26+00:00"
# last_modified_at: "2025-05-05T13:00:26+00:00"
# entrypoint: "test_stub_config_extra.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ValidatorConfig']
# base_class: ['ValidatorConfig']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""config.py
containers.foundation.src.foundation.script.validation.test_stub.config.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

from foundation.script.validation.models import ValidatorConfig
from pydantic import Field


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