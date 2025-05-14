# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_validate_chunk"
# namespace: "omninode.tools.test_python_validate_chunk"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:18+00:00"
# last_modified_at: "2025-05-05T13:00:18+00:00"
# entrypoint: "test_python_validate_chunk.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
metadata:
  name: python_validate_chunk_test
  tuple: chunk
  type: validator
  language: python
  registry: true
"""

import os
import tempfile
from typing import Any, Generator

import pytest
from foundation.script.validate.validate_registry import get_registered_fixture
from foundation.test.test_case_registry import TEST_CASE_REGISTRY

TEST_DIR = os.path.dirname(__file__)


@pytest.fixture
def chunk_validator() -> Generator[Any, None, None]:
    fixture_cls = get_registered_fixture("chunk_validator_fixture")
    return fixture_cls().get_fixture(python=True)


def test_chunk_valid_short(chunk_validator: Any) -> None:
    fname: str = TEST_CASE_REGISTRY.get_test_case("chunk", "valid_chunk_short", "valid")
    result = chunk_validator.validate(fname)
    assert result.is_valid
    assert not result.errors


def test_chunk_soft_warning(chunk_validator: Any) -> None:
    fname: str = TEST_CASE_REGISTRY.get_test_case(
        "chunk", "valid_chunk_soft_warning", "valid"
    )
    result = chunk_validator.validate(fname)
    assert result.is_valid
    assert result.warnings
    assert not result.errors


def test_chunk_hard_fail(chunk_validator: Any) -> None:
    fname: str = TEST_CASE_REGISTRY.get_test_case(
        "chunk", "invalid_chunk_hard_fail", "invalid"
    )
    result = chunk_validator.validate(fname)
    assert not result.is_valid
    assert result.errors


def test_chunk_tokenizer_branch(chunk_validator: Any) -> None:
    class MockTokenizer:
        def encode(self, content):
            return list(content)  # 1 token per char

    validator = chunk_validator
    validator.tokenizer = MockTokenizer()
    content = "a" * 100  # 100 tokens
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".py") as f:
        f.write(content)
        fname = f.name
    try:
        result = validator.validate(fname)
        assert result.is_valid
        assert result.metadata["token_count"] == 100
    finally:
        os.remove(fname)


def test_chunk_soft_token_warning(chunk_validator: Any) -> None:
    # Create a file that exceeds the soft token limit but not the hard limit
    content = "a" * 7205  # 1801 tokens (1801*4 > 7201)
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".py") as f:
        f.write(content)
        fname = f.name
    try:
        result = chunk_validator.validate(fname)
        assert result.is_valid
        assert result.warnings
    finally:
        os.remove(fname)