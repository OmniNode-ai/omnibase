# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_chunk_cli"
# namespace: "omninode.tools.test_validate_chunk_cli"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_validate_chunk_cli.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import json
import os
import re
import subprocess
import sys
import tempfile

import pytest
from foundation.util.util_chunk_metrics import UtilChunkMetrics
from foundation.registry.cli_registry import cli_registry
from foundation.test.test_case_registry import TEST_CASE_REGISTRY

SCRIPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../script/validate/python/python_validate_chunk.py")
)


@pytest.mark.parametrize(
    "case_name,expected_pass",
    [
        ("valid_chunk_short", True),
        ("invalid_chunk_hard_fail", False),
    ],
)
def test_validate_chunk_cli(case_name, expected_pass):
    if expected_pass:
        fname = TEST_CASE_REGISTRY.get_test_case("chunk", case_name, "valid")
    else:
        fname = TEST_CASE_REGISTRY.get_test_case("chunk", case_name, "invalid")
    cli = cli_registry.get('python_validate_chunk')
    result = cli.main([fname])
    assert isinstance(result.exit_code, int)
    if expected_pass:
        assert result.exit_code == 0
        assert result.result["is_valid"] is True
    else:
        assert result.exit_code != 0
        assert result.result["is_valid"] is False