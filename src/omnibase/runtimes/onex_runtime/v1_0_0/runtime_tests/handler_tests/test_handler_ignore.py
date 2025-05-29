# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.576205'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_ignore
# hash: 62dc65639dfc278ff0368f159a6032c2f9b3de92d71aa20aa3d46c9037c7e02b
# last_modified_at: '2025-05-29T14:14:00.740330+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_ignore.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.runtime_tests.handler_tests.test_handler_ignore
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 6182f63a-3317-43e4-ab2e-059569990948
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path

import pytest

from omnibase.handlers.handler_ignore import IgnoreFileHandler


@pytest.fixture
def sample_ignore_path(tmp_path: Path) -> Path:
    # Copy the sample_ignore.onexignore fixture to a temp directory
    fixture_dir = Path(__file__).parent / "testcases"
    src = fixture_dir / "sample_ignore.onexignore"
    dst = tmp_path / ".onexignore"
    dst.write_text(src.read_text())
    return dst


@pytest.mark.node
def test_ignore_handler_can_handle(sample_ignore_path: Path) -> None:
    handler = IgnoreFileHandler()
    assert handler.can_handle(sample_ignore_path, sample_ignore_path.read_text())


@pytest.mark.node
def test_ignore_handler_stamp_method(sample_ignore_path: Path) -> None:
    handler = IgnoreFileHandler()
    content = sample_ignore_path.read_text()
    result = handler.stamp(sample_ignore_path, content)
    assert result is not None
    assert result.target == str(sample_ignore_path)
