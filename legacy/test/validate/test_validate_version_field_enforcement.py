#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_version_field_enforcement"
# namespace: "omninode.tools.test_validate_version_field_enforcement"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_version_field_enforcement.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
test_version_field_enforcement.py
containers.foundation.test.unit.validation.test_version_field_enforcement

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import re
from pathlib import Path

import pytest
import yaml

# Helper for version field validation (semantic versioning)
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

TEST_CASES_DIR = Path(__file__).parent / "test_cases" / "metadata" / "versioning"


@pytest.mark.parametrize(
    "case_file,should_pass",
    [
        (TEST_CASES_DIR / "valid_semver.yaml", True),
        (TEST_CASES_DIR / "invalid_version.yaml", False),
        (TEST_CASES_DIR / "deprecated_schema.yaml", True),
    ],
)
def test_version_field_enforcement(case_file, should_pass):
    with open(case_file, "r") as f:
        schema = yaml.safe_load(f)
    version = schema.get("version")
    if should_pass:
        assert version is not None
        assert SEMVER_PATTERN.match(version)
        # If deprecated, check fields
        if schema.get("deprecated"):
            assert isinstance(schema.get("deprecation_message"), str)
    else:
        # Should fail for missing or invalid version
        assert version is None or not SEMVER_PATTERN.match(version)