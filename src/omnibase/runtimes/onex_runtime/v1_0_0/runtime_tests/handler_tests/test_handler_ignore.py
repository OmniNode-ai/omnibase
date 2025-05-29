# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.576205'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_ignore.py
# hash: 2c902ca4718315561cd99105b997d9dba77aded762e46a3f7642ded5622ff0b3
# last_modified_at: '2025-05-29T11:50:12.365019+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_ignore.py
# namespace: omnibase.test_handler_ignore
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
