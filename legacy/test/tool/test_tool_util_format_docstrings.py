# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_tool_util_format_docstrings"
# namespace: "omninode.tools.test_tool_util_format_docstrings"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:28+00:00"
# last_modified_at: "2025-05-05T13:00:28+00:00"
# entrypoint: "test_tool_util_format_docstrings.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "./././src/foundation/scripts/utils")
    ),
)
from util_format_docstrings import run_docformatter


def test_dry_run_success():
    # Mock subprocess_runner to simulate docformatter --check
    class Result:
        def __init__(self):
            self.stdout = "All files are properly formatted."
            self.stderr = ""
            self.returncode = 0

    def fake_runner(cmd, capture_output, text):
        return Result()

    exit_code = run_docformatter("some/path", True, subprocess_runner=fake_runner)
    assert exit_code == 0


def test_dry_run_failure():
    # Mock subprocess_runner to simulate docformatter --check with issues
    class Result:
        def __init__(self):
            self.stdout = "Some files need reformatting."
            self.stderr = "error: not formatted"
            self.returncode = 1

    def fake_runner(cmd, capture_output, text):
        return Result()

    exit_code = run_docformatter("some/path", True, subprocess_runner=fake_runner)
    assert exit_code == 0  # dry-run always exits 0


def test_invalid_path():
    # Mock subprocess_runner to simulate docformatter error
    class Result:
        def __init__(self):
            self.stdout = ""
            self.stderr = "No such file or directory"
            self.returncode = 2

    def fake_runner(cmd, capture_output, text):
        return Result()

    exit_code = run_docformatter("invalid/path", True, subprocess_runner=fake_runner)
    assert exit_code == 0  # dry-run always exits 0


def test_real_invocation():
    # This test runs the function in dry-run mode on a small directory (should not fail)
    exit_code = run_docformatter(
        "containers/foundation/src/foundation/scripts/utils", True
    )
    assert exit_code == 0