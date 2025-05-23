# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_handler_ignore.py
# version: 1.0.0
# uuid: 273beee8-f449-4f95-a110-960e3e05d324
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.716997
# last_modified_at: 2025-05-22T21:19:13.489905
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 79bc936c2590553bcafc656e0a1ef3e0da2dffbf46951d2d9e53ea6f014e9e20
# entrypoint: python@test_handler_ignore.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_handler_ignore
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
