# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-21309 AC5: the installer's shell suites, run under pytest.

`uv run pytest -q tests/installer` runs the clone-only suite (the clone-only
install path must be unchanged by the finish step) and every finish-step suite.
Each suite drives the real scripts and fails here on any non-zero exit.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SUITES = [
    "tests/test_install_clone_only.sh",
    "tests/installer/test_finish_step_disabled.sh",
    "tests/installer/test_finish_step_default_on.sh",
    "tests/installer/test_finish_step_enabled.sh",
    "tests/installer/test_finish_step_name.sh",
    "tests/installer/test_finish_step_guards.sh",
]


@pytest.mark.parametrize("suite", SUITES)
def test_suite_passes(suite: str) -> None:
    if suite.startswith("tests/installer/test_finish_step") and sys.platform != "darwin":
        pytest.skip("the finish step runs only on macOS")
    result = subprocess.run(
        ["bash", suite], cwd=REPO, capture_output=True, text=True, timeout=600
    )
    assert result.returncode == 0, result.stdout + result.stderr
