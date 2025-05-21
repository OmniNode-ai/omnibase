from pathlib import Path

import pytest

from src.omnibase.runtime.handlers.handler_ignore import IgnoreFileHandler


@pytest.fixture
def sample_ignore_path(tmp_path):
    # Copy the sample_ignore.onexignore fixture to a temp directory
    fixture_dir = Path(__file__).parent / "testcases"
    src = fixture_dir / "sample_ignore.onexignore"
    dst = tmp_path / ".onexignore"
    dst.write_text(src.read_text())
    return dst


@pytest.mark.node
def test_ignore_handler_can_handle(sample_ignore_path):
    handler = IgnoreFileHandler()
    assert handler.can_handle(sample_ignore_path, sample_ignore_path.read_text())


@pytest.mark.node
def test_ignore_handler_handle_method(sample_ignore_path):
    handler = IgnoreFileHandler()
    # This is a stub; update as real logic is ported
    assert handler.handle(sample_ignore_path)
