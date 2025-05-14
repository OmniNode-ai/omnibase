#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_yaml_schema_linter"
# namespace: "omninode.tools.test_validate_yaml_schema_linter"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:14+00:00"
# last_modified_at: "2025-05-05T13:00:14+00:00"
# entrypoint: "test_validate_yaml_schema_linter.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
test_yaml_schema_linter.py
containers.foundation.test.unit.validation.test_yaml_schema_linter

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import subprocess
import sys
from pathlib import Path

LINTER_PATH = (
    Path(__file__).parents[5]
    / "containers"
    / "foundation"
    / "src"
    / "foundation"
    / "scripts"
    / "validation"
    / "yaml_schema_linter.py"
)
TEST_CASES_DIR = Path(__file__).parent / "test_cases" / "metadata" / "versioning"


def test_linter_valid_file():
    valid_file = TEST_CASES_DIR / "valid_semver.yaml"
    result = subprocess.run(
        [sys.executable, str(LINTER_PATH), str(valid_file)],
        capture_output=True,
        text=True,
    )
    assert "[PASS]" in result.stdout
    assert result.returncode == 0


def test_linter_invalid_file():
    invalid_file = TEST_CASES_DIR / "invalid_version.yaml"
    result = subprocess.run(
        [sys.executable, str(LINTER_PATH), str(invalid_file)],
        capture_output=True,
        text=True,
    )
    assert "[FAIL]" in result.stdout
    assert "Invalid version format" in result.stdout
    assert result.returncode != 0