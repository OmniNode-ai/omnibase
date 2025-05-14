# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_metadata_unified_result"
# namespace: "omninode.tools.test_metadata_unified_result"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:15:00+00:00"
# last_modified_at: "2025-05-07T11:15:00+00:00"
# entrypoint: "test_metadata_unified_result.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from datetime import datetime
import json
import pytest
from foundation.model.model_unified_result import (
    UnifiedStatus,
    UnifiedMessageModel,
    UnifiedSummaryModel,
    UnifiedVersionModel,
    UnifiedRunMetadataModel,
    UnifiedResultModel,
    UnifiedBatchResultModel,
)

def test_unified_status_values():
    """Test UnifiedStatus enum values."""
    assert UnifiedStatus.success == "success"
    assert UnifiedStatus.warning == "warning"
    assert UnifiedStatus.error == "error"
    assert UnifiedStatus.skipped == "skipped"
    assert UnifiedStatus.fixed == "fixed"
    assert UnifiedStatus.partial == "partial"
    assert UnifiedStatus.info == "info"
    assert UnifiedStatus.unknown == "unknown"

def test_unified_message_model():
    """Test UnifiedMessageModel creation and validation."""
    message = UnifiedMessageModel(
        summary="Test summary",
        level="info",
        suggestions=["Fix this", "Fix that"],
        remediation="Apply patch",
        rendered_markdown="# Test",
        doc_link="https://docs.example.com",
        file="test.py",
        line=42,
        column=10,
        details="More details",
        severity="high",
        code="E123",
        context={"key": "value"},
        timestamp=datetime.now(),
        fixable=True,
        origin="test",
        example="example code",
        localized_text={"en": "text"},
        type="error"
    )
    assert message.summary == "Test summary"
    assert message.level == "info"
    assert len(message.suggestions) == 2
    assert message.file == "test.py"
    assert message.line == 42

def test_unified_summary_model():
    """Test UnifiedSummaryModel creation and validation."""
    summary = UnifiedSummaryModel(
        total=10,
        passed=7,
        failed=2,
        skipped=1,
        fixed=0,
        warnings=3,
        notes=["Note 1", "Note 2"],
        details={"key": "value"}
    )
    assert summary.total == 10
    assert summary.passed == 7
    assert len(summary.notes) == 2

def test_unified_version_model():
    """Test UnifiedVersionModel creation and validation."""
    version = UnifiedVersionModel(
        protocol_version="1.0",
        tool_version="2.0",
        schema_version="3.0",
        last_updated=datetime.now()
    )
    assert version.protocol_version == "1.0"
    assert version.tool_version == "2.0"

def test_unified_run_metadata_model():
    """Test UnifiedRunMetadataModel creation and validation."""
    start_time = datetime.now()
    metadata = UnifiedRunMetadataModel(
        start_time=start_time,
        end_time=start_time,
        duration=1.5,
        run_id="test-123"
    )
    assert metadata.start_time == start_time
    assert metadata.duration == 1.5

def test_unified_result_model():
    """Test UnifiedResultModel creation and validation."""
    result = UnifiedResultModel(
        status=UnifiedStatus.success,
        target="test.py",
        messages=[
            UnifiedMessageModel(summary="Test passed", level="info")
        ],
        summary=UnifiedSummaryModel(
            total=1,
            passed=1,
            failed=0,
            skipped=0,
            fixed=0,
            warnings=0
        ),
        metadata={"key": "value"},
        suggestions=["Fix this"],
        diff="- old\n+ new",
        auto_fix_applied=True,
        fixed_files=["fixed.py"],
        failed_files=[],
        version=UnifiedVersionModel(protocol_version="1.0"),
        duration=1.5,
        exit_code=0,
        run_id="test-123",
        child_results=[],
        output_format="json",
        cli_args=["--fix"],
        orchestrator_info={"name": "test"},
        tool_name="validator",
        skipped_reason=None,
        coverage=100.0,
        test_type="unit",
        batch_id="batch-123",
        parent_id="parent-123",
        timestamp=datetime.now()
    )
    assert result.status == UnifiedStatus.success
    assert result.target == "test.py"
    assert len(result.messages) == 1

def test_unified_batch_result_model():
    """Test UnifiedBatchResultModel creation and validation."""
    batch = UnifiedBatchResultModel(
        results=[
            UnifiedResultModel(
                status=UnifiedStatus.success,
                target="test1.py",
                messages=[
                    UnifiedMessageModel(summary="Test 1 passed", level="info")
                ]
            ),
            UnifiedResultModel(
                status=UnifiedStatus.warning,
                target="test2.py",
                messages=[
                    UnifiedMessageModel(summary="Test 2 warning", level="warning")
                ]
            )
        ],
        messages=[
            UnifiedMessageModel(summary="Batch summary", level="info")
        ],
        summary=UnifiedSummaryModel(
            total=2,
            passed=1,
            failed=0,
            skipped=0,
            fixed=0,
            warnings=1
        ),
        status=UnifiedStatus.warning,
        version=UnifiedVersionModel(protocol_version="1.0"),
        run_metadata=UnifiedRunMetadataModel(
            start_time=datetime.now(),
            duration=2.5,
            run_id="batch-123"
        ),
        metadata={"key": "value"}
    )
    assert len(batch.results) == 2
    assert batch.status == UnifiedStatus.warning

def test_export_schema():
    """Test schema export functionality."""
    schema = UnifiedBatchResultModel.export_schema()
    assert isinstance(schema, str)
    
    # Verify it's valid JSON
    schema_dict = json.loads(schema)
    assert isinstance(schema_dict, dict)
    assert "title" in schema_dict
    assert "properties" in schema_dict
    
    # Verify key model components are present
    assert "results" in schema_dict["properties"]
    assert "messages" in schema_dict["properties"]
    assert "summary" in schema_dict["properties"]
    assert "status" in schema_dict["properties"] 