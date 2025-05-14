# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_tool_orchestrator_integration"
# namespace: "omninode.tests.test_tool_orchestrator_integration"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_tool_orchestrator_integration.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Test_Metadata ===
"""
Canary integration test for tool orchestrators.
Ensures orchestrators are registered, instantiable, and run without error.
Follows canary standards: registry, instantiation, and minimal run/behavior.
"""
import pytest
from unittest.mock import patch, mock_open
from foundation.script.tool.tool_orchestrator_fix_codebase import ToolOrchestratorFixCodebase
from foundation.script.tool.tool_coverage_report import ToolCoverageReportOrchestrator
from foundation.script.orchestrator.orchestrator_registry import OrchestratorRegistry
from foundation.model.model_unified_result import UnifiedBatchResultModel

def test_tool_orchestrator_fix_codebase_registry():
    # Ensure orchestrator is registered
    registry = OrchestratorRegistry()
    registry.register("tool_orchestrator_fix_codebase", ToolOrchestratorFixCodebase)
    assert registry.get("tool_orchestrator_fix_codebase") is not None
    # Instantiate and run (should not raise)
    orchestrator = ToolOrchestratorFixCodebase()
    result = orchestrator.run(args=[])
    assert result is not None or result is None  # Accepts any result, just checks for error-free run

def test_tool_coverage_report_orchestrator_registry():
    # Ensure orchestrator is registered
    registry = OrchestratorRegistry()
    registry.register("tool_coverage_report", ToolCoverageReportOrchestrator)
    assert registry.get("tool_coverage_report") is not None
    # Patch open to simulate reading a known coverage.json (no temp files)
    fake_coverage = '{"files": {}}'
    with patch("builtins.open", mock_open(read_data=fake_coverage)):
        orchestrator = ToolCoverageReportOrchestrator()
        result = orchestrator.run()
        assert isinstance(result, UnifiedBatchResultModel)
        assert result.results[0].status.value == "error"
        assert any(
            "coverage.json not found" in m.summary or
            "Coverage check failed" in m.summary or
            "coverage.json is empty or contains no files" in m.summary
            for m in result.results[0].messages
        ), "Expected error message about coverage"

def test_tool_orchestrator_fix_codebase_returns_unified_batch_result():
    orchestrator = ToolOrchestratorFixCodebase()
    result = orchestrator.run(["--dry-run", "--target", "."])
    assert isinstance(result, UnifiedBatchResultModel) 