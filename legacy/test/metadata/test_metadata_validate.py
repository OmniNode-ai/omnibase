# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_validate"
# namespace: "omninode.tools.test_metadata_validate"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:20:00+00:00"
# last_modified_at: "2025-05-07T11:20:00+00:00"
# entrypoint: "test_metadata_validate.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["UnifiedResultModel"]
# base_class: ["UnifiedMessageModel"]
# protocol_version: "1.0.0"
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.model.model_unified_result import (
    UnifiedResultModel,
    UnifiedMessageModel,
    UnifiedStatus,
    UnifiedVersionModel,
    UnifiedSummaryModel,
)
from pydantic_core import ValidationError

def test_unified_message_model():
    """Test UnifiedMessageModel creation and validation."""
    message = UnifiedMessageModel(
        summary="Test error",
        level="error",
        file="test.py",
        line=42,
        details="Extra details",
        type="error",
        suggestion="Fix this",
        context={"info": "Test context"},
        validator="test_validator",
        timestamp="2025-05-07T11:20:00Z"
    )
    assert message.level == "error"
    assert message.summary == "Test error"
    assert message.file == "test.py"
    assert message.line == 42

def test_unified_message_model_file_validation():
    """Test UnifiedMessageModel file field validation."""
    # Test with string file path (valid)
    message = UnifiedMessageModel(
        summary="Test error",
        level="error",
        file="test.py"
    )
    assert message.file == "test.py"

    # Test with None file path (valid)
    message = UnifiedMessageModel(
        summary="Test error",
        level="error",
        file=None
    )
    assert message.file is None

    # Test with non-string file path (invalid)
    with pytest.raises(ValidationError, match="Input should be a valid string"):
        UnifiedMessageModel(
            summary="Test error",
            level="error",
            file=42  # Integer instead of string
        )

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        UnifiedMessageModel(
            summary="Test error",
            level="error",
            file=["test.py"]  # List instead of string
        )

def test_unified_status_enum():
    """Test UnifiedStatus enum values."""
    assert UnifiedStatus.success.value == "success"
    assert UnifiedStatus.error.value == "error"
    assert UnifiedStatus.warning.value == "warning"
    assert UnifiedStatus.skipped.value == "skipped"

def test_unified_result_model():
    """Test UnifiedResultModel creation and validation."""
    summary = UnifiedSummaryModel(
        total=1,
        passed=1,
        failed=0,
        skipped=0,
        fixed=0,
        warnings=0,
        notes=["Test summary"]
    )
    result = UnifiedResultModel(
        status=UnifiedStatus.warning,
        messages=[
            UnifiedMessageModel(
                summary="Test warning",
                level="warning",
                file="test.py"
            )
        ],
        version=UnifiedVersionModel(protocol_version="1.0.0"),
        metadata={"key": "value"},
        child_results=[],
        summary=summary
    )
    assert result.status == UnifiedStatus.warning
    assert len(result.messages) == 1
    assert result.version.protocol_version == "1.0.0"
    assert result.summary.notes[0] == "Test summary"

def test_unified_version_model():
    """Test UnifiedVersionModel creation and validation."""
    version = UnifiedVersionModel(protocol_version="1.0.0")
    assert version.protocol_version == "1.0.0" 