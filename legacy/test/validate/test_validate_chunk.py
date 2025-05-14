# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_chunk"
# namespace: "omninode.tools.test_validate_chunk"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:19+00:00"
# last_modified_at: "2025-05-05T17:01:19+00:00"
# entrypoint: "test_validate_chunk.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import os
import tempfile
from typing import Generator, Any

import pytest
from foundation.script.validate.validate_registry import (
    get_registered_fixture,
    register_fixture,
)
from foundation.model.model_validate import ValidationResult, ValidationIssue


# Dummy validator that simulates pass, soft warning, and hard fail based on line count and token count
class ProtocolValidateFixtureChunkDummy:
    def __init__(self, chunk_metrics):
        self.tokenizer = None
        self.chunk_metrics = chunk_metrics

    def validate(self, fname):
        content = self.chunk_metrics.read_file(fname)
        line_count = self.chunk_metrics.count_lines(fname)
        # Use injected tokenizer if present
        if self.tokenizer:
            token_count = self.chunk_metrics.count_tokens(content, self.tokenizer)
        else:
            token_count = self.chunk_metrics.count_tokens(content)
        warnings = []
        # Line-based logic
        if line_count < 400:
            is_valid = True
        elif line_count < 500:
            is_valid = True
            warnings.append(ValidationIssue(type="warning", message="soft warning", file=fname))
        else:
            is_valid = False
        # Token-based logic (soft token limit = 1800)
        if token_count > 1800:
            warnings.append(ValidationIssue(type="warning", message="soft token warning", file=fname))
        errors = []
        if not is_valid:
            errors.append(ValidationIssue(type="error", message="hard fail", file=fname))
        # Always return a ValidationResult
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata={"line_count": line_count, "token_count": token_count},
        )


class ProtocolValidateFixtureChunkDummyFixture:
    def get_fixture(self, python=True):
        return ProtocolValidateFixtureChunkDummy(chunk_metrics=utility_registry['chunk_metrics'])


# Register the dummy fixture for this test run
register_fixture(
    name="chunk_validator_fixture",
    fixture=ProtocolValidateFixtureChunkDummyFixture,
    description="DI/registry-compliant dummy fixture for chunk validator test isolation.",
)


@pytest.fixture
def chunk_validator() -> Generator[Any, None, None]:
    fixture_cls = get_registered_fixture("chunk_validator_fixture")
    return fixture_cls().get_fixture(python=True)


def test_chunk_validator_pass(chunk_validator: Any) -> None:
    # Create a file under the soft limit
    content = "line\n" * 100
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        fname = f.name
    try:
        result = chunk_validator.validate(fname)
        assert result.is_valid
        assert result.metadata["line_count"] == 100
        assert not result.errors
    finally:
        os.remove(fname)


def test_chunk_validator_soft_warning(chunk_validator: Any) -> None:
    # Create a file just over the soft line limit
    content = "line\n" * 460
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        fname = f.name
    try:
        result = chunk_validator.validate(fname)
        assert result.is_valid
        assert result.metadata["line_count"] == 460
        assert result.warnings
        assert not result.errors
    finally:
        os.remove(fname)


def test_chunk_validator_hard_fail(chunk_validator: Any) -> None:
    # Create a file over the hard line limit
    content = "line\n" * 600
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        fname = f.name
    try:
        result = chunk_validator.validate(fname)
        assert not result.is_valid
        assert result.metadata["line_count"] == 600
        assert result.errors
    finally:
        os.remove(fname)