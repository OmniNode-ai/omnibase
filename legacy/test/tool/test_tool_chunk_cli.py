# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_tool_chunk_cli"
# namespace: "omninode.tools.test_tool_chunk_cli"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:28+00:00"
# last_modified_at: "2025-05-05T13:00:28+00:00"
# entrypoint: "test_tool_chunk_cli.py"
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

SCRIPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../script/tool/tool_chunk.py")
)


@pytest.mark.parametrize(
    "line_count,expected_success",
    [
        (100, True),  # valid
        (600, False),  # invalid (over hard limit)
    ],
)
def test_tool_chunk_cli(line_count, expected_success):
    content = "line\n" * line_count
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        fname = f.name
    try:
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, fname], capture_output=True, text=True
        )
        # Find the tool_result_json log line and extract the JSON
        match = re.search(r"tool_result_json.*result=(\{.*\})", result.stdout)
        assert match, f"No tool_result_json log line found in output: {result.stdout}"
        result_json = json.loads(match.group(1))
        if expected_success:
            assert result.returncode == 0
            assert result_json["is_valid"] is True
        else:
            assert result.returncode != 0
            assert result_json["is_valid"] is False
    finally:
        os.remove(fname)