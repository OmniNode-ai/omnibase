"""
Test module for model_unified_result.py.

This module contains test cases for UnifiedResultModel, UnifiedBatchResultModel,
and related models in the unified result system.
"""

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_model_unified_result"
# namespace: "foundation.test.model"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T18:25:48+00:00"
# last_modified_at: "2025-05-07T18:25:48+00:00"
# entrypoint: "test_model_unified_result.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['test']
# base_class: ['test']
# mock_safe: true
# === /OmniNode:Metadata ===

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

def test_unified_status_enum():
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
        summary="Test message",
        level="info",
        file="test.py",
        line=42,
        details="Detailed test message"
    )
    assert message.summary == "Test message"
    assert message.level == "info"
    assert message.file == "test.py"
    assert message.line == 42
    assert message.details == "Detailed test message"

def test_unified_summary_model():
    """Test UnifiedSummaryModel creation and validation."""
    summary = UnifiedSummaryModel(
        total=10,
        passed=8,
        failed=1,
        skipped=1,
        fixed=0,
        warnings=2,
        notes=["Note 1", "Note 2"]
    )
    assert summary.total == 10
    assert summary.passed == 8
    assert summary.failed == 1
    assert summary.skipped == 1
    assert summary.fixed == 0
    assert summary.warnings == 2
    assert summary.notes == ["Note 1", "Note 2"]

def test_unified_version_model():
    """Test UnifiedVersionModel creation and validation."""
    version = UnifiedVersionModel(
        protocol_version="1.0.0",
        tool_version="2.0.0",
        schema_version="1.0.0",
        last_updated=datetime.now()
    )
    assert version.protocol_version == "1.0.0"
    assert version.tool_version == "2.0.0"
    assert version.schema_version == "1.0.0"
    assert isinstance(version.last_updated, datetime)

def test_unified_run_metadata_model():
    """Test UnifiedRunMetadataModel creation and validation."""
    start_time = datetime.now()
    metadata = UnifiedRunMetadataModel(
        start_time=start_time,
        end_time=start_time,
        duration=1.5,
        run_id="test-run-123"
    )
    assert metadata.start_time == start_time
    assert metadata.end_time == start_time
    assert metadata.duration == 1.5
    assert metadata.run_id == "test-run-123"

def test_unified_result_model():
    """Test UnifiedResultModel creation and validation."""
    result = UnifiedResultModel(
        status=UnifiedStatus.success,
        target="test.py",
        messages=[
            UnifiedMessageModel(
                summary="Test passed",
                level="info"
            )
        ],
        summary=UnifiedSummaryModel(
            total=1,
            passed=1,
            failed=0,
            skipped=0,
            fixed=0,
            warnings=0
        )
    )
    assert result.status == UnifiedStatus.success
    assert result.target == "test.py"
    assert len(result.messages) == 1
    assert result.messages[0].summary == "Test passed"
    assert result.summary.total == 1
    assert result.summary.passed == 1

def test_unified_batch_result_model():
    """Test UnifiedBatchResultModel creation and validation."""
    result1 = UnifiedResultModel(
        status=UnifiedStatus.success,
        target="test1.py",
        messages=[UnifiedMessageModel(summary="Test 1 passed", level="info")]
    )
    result2 = UnifiedResultModel(
        status=UnifiedStatus.warning,
        target="test2.py",
        messages=[UnifiedMessageModel(summary="Test 2 warning", level="warning")]
    )
    
    batch_result = UnifiedBatchResultModel(
        results=[result1, result2],
        messages=[UnifiedMessageModel(summary="Batch completed", level="info")],
        summary=UnifiedSummaryModel(
            total=2,
            passed=1,
            failed=0,
            skipped=0,
            fixed=0,
            warnings=1
        ),
        status=UnifiedStatus.warning
    )
    
    assert len(batch_result.results) == 2
    assert batch_result.results[0].status == UnifiedStatus.success
    assert batch_result.results[1].status == UnifiedStatus.warning
    assert batch_result.status == UnifiedStatus.warning
    assert batch_result.summary.total == 2
    assert batch_result.summary.warnings == 1

def test_unified_batch_result_model_export_schema():
    """Test UnifiedBatchResultModel.export_schema() method."""
    schema = UnifiedBatchResultModel.export_schema()
    schema_dict = json.loads(schema)
    
    # Verify schema structure
    assert isinstance(schema_dict, dict)
    assert "title" in schema_dict
    assert schema_dict["title"] == "UnifiedBatchResultModel"
    assert "type" in schema_dict
    assert schema_dict["type"] == "object"
    assert "properties" in schema_dict
    
    # Verify required properties
    assert "results" in schema_dict["properties"]
    assert "messages" in schema_dict["properties"]
    assert "summary" in schema_dict["properties"]
    assert "status" in schema_dict["properties"]
    assert "version" in schema_dict["properties"]
    assert "run_metadata" in schema_dict["properties"]
    assert "metadata" in schema_dict["properties"]

def test_unified_result_model_with_child_results():
    """Test UnifiedResultModel with nested child results."""
    child1 = UnifiedResultModel(
        status=UnifiedStatus.success,
        target="child1.py",
        messages=[UnifiedMessageModel(summary="Child 1 passed", level="info")]
    )
    child2 = UnifiedResultModel(
        status=UnifiedStatus.warning,
        target="child2.py",
        messages=[UnifiedMessageModel(summary="Child 2 warning", level="warning")]
    )
    
    parent = UnifiedResultModel(
        status=UnifiedStatus.warning,
        target="parent.py",
        messages=[UnifiedMessageModel(summary="Parent test", level="info")],
        child_results=[child1, child2]
    )
    
    assert len(parent.child_results) == 2
    assert parent.child_results[0].status == UnifiedStatus.success
    assert parent.child_results[1].status == UnifiedStatus.warning
    assert parent.status == UnifiedStatus.warning

def test_unified_result_model_with_coverage():
    """Test UnifiedResultModel with coverage information."""
    result = UnifiedResultModel(
        status=UnifiedStatus.success,
        target="test_coverage.py",
        messages=[UnifiedMessageModel(summary="Coverage test", level="info")],
        coverage=98.5,
        test_type="unit"
    )
    
    assert result.coverage == 98.5
    assert result.test_type == "unit"

def test_unified_result_model_with_orchestrator_info():
    """Test UnifiedResultModel with orchestrator information."""
    orchestrator_info = {
        "orchestrator": "test-orchestrator",
        "pipeline": "test-pipeline",
        "stage": "validation"
    }
    
    result = UnifiedResultModel(
        status=UnifiedStatus.success,
        target="test.py",
        messages=[UnifiedMessageModel(summary="Orchestrator test", level="info")],
        orchestrator_info=orchestrator_info
    )
    
    assert result.orchestrator_info == orchestrator_info
    assert result.orchestrator_info["orchestrator"] == "test-orchestrator"
    assert result.orchestrator_info["pipeline"] == "test-pipeline"
    assert result.orchestrator_info["stage"] == "validation" 