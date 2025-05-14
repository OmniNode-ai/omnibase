# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_validate_error"
# namespace: "omninode.tools.test_metadata_validate_error"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:00:00+00:00"
# last_modified_at: "2025-05-07T11:00:00+00:00"
# entrypoint: "test_metadata_validate_error.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["UnifiedResultModel"]
# base_class: ["UnifiedMessageModel"]
# protocol_version: "1.0.0"
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.model.model_unified_result import (
    UnifiedMessageModel,
    UnifiedResultModel,
    UnifiedStatus,
    UnifiedSummaryModel,
    UnifiedVersionModel,
)
from pydantic_core import ValidationError

def test_unified_message_model_basic():
    """Test basic UnifiedMessageModel functionality."""
    msg = UnifiedMessageModel(summary="Test message", level="error")
    assert msg.summary == "Test message"
    assert msg.level == "error"

def test_unified_message_model_context():
    """Test context field for UnifiedMessageModel."""
    msg = UnifiedMessageModel(summary="Test message", level="warning", context={"key": "value"})
    assert msg.context["key"] == "value"

def test_unified_message_model_file_line():
    """Test file and line fields for UnifiedMessageModel."""
    msg = UnifiedMessageModel(summary="Test message", level="info", file="test.py", line=42)
    assert msg.file == "test.py"
    assert msg.line == 42

def test_unified_status_enum():
    """Test UnifiedStatus enum values."""
    assert UnifiedStatus.success.value == "success"
    assert UnifiedStatus.error.value == "error"
    assert UnifiedStatus.warning.value == "warning"
    assert UnifiedStatus.skipped.value == "skipped"
    assert UnifiedStatus.fixed.value == "fixed"
    assert UnifiedStatus.partial.value == "partial"
    assert UnifiedStatus.info.value == "info"
    assert UnifiedStatus.unknown.value == "unknown"

def test_unified_result_model_basic():
    """Test basic UnifiedResultModel functionality."""
    result = UnifiedResultModel(
        status=UnifiedStatus.error,
        messages=[UnifiedMessageModel(summary="Test error", level="error")],
        summary=UnifiedSummaryModel(
            total=1,
            passed=0,
            failed=1,
            skipped=0,
            fixed=0,
            warnings=0
        ),
        version=UnifiedVersionModel(protocol_version="1.0.0")
    )
    assert result.status == UnifiedStatus.error
    assert len(result.messages) == 1
    assert result.summary.failed == 1
    assert result.version.protocol_version == "1.0.0"

def test_unified_result_model_with_warnings():
    """Test UnifiedResultModel with warning messages."""
    result = UnifiedResultModel(
        status=UnifiedStatus.warning,
        messages=[UnifiedMessageModel(summary="Test warning", level="warning")],
        summary=UnifiedSummaryModel(
            total=1,
            passed=0,
            failed=0,
            skipped=0,
            fixed=0,
            warnings=1
        ),
        version=UnifiedVersionModel(protocol_version="1.0.0")
    )
    assert result.status == UnifiedStatus.warning
    assert result.summary.warnings == 1

# Additional tests for serialization, context, and error handling can be added as needed for unified models. 