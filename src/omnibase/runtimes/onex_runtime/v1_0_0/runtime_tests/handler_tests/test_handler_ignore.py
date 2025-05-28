# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_handler_ignore.py
# version: 1.0.0
# uuid: 6182f63a-3317-43e4-ab2e-059569990948
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.576205
# last_modified_at: 2025-05-28T17:20:03.970919
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a36a669821653c6c63a06af8c9e0981b4ed7eac9a7f55b2ada9a0db38353537e
# entrypoint: python@test_handler_ignore.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_handler_ignore
# meta_type: tool
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
