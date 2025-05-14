# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_orchestrator_output_formatter"
# namespace: "omninode.tests.test_orchestrator_output_formatter"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_orchestrator_output_formatter.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTestableCLI']
# base_class: ['ProtocolTestableCLI']
# mock_safe: true
# === /OmniNode:Test_Metadata ===
"""
Canonical test for SharedOutputFormatter.
Follows all standards in docs/testing/testing.md: unified models, protocol compliance, registry-driven patterns, and output format assertions.
The output formatter must be injected by the test harness or runner; direct instantiation is not allowed.
"""
import pytest
from foundation.model.model_unified_result import UnifiedBatchResultModel, UnifiedResultModel, UnifiedMessageModel, UnifiedStatus
from foundation.model.model_result_cli import ModelResultCLI
from foundation.base.base_orchestrator_test import BaseOrchestratorTest

# No direct instantiation or fixture for SharedOutputFormatter allowed.
# All test functions must accept output_formatter as an explicit argument, injected by the test harness.

class TestOrchestratorOutputFormatter(BaseOrchestratorTest):
    """
    Canonical test for SharedOutputFormatter.
    Implements protocol compliance by method, not inheritance.
    """
    def main(self, argv):
        # Stub for protocol compliance; not used in these tests
        return ModelResultCLI(exit_code=0, output="stub", errors=None, result=None, metadata=None)

    def test_import_and_method(self, output_formatter):
        methods = [getattr(output_formatter, m) for m in dir(output_formatter) if callable(getattr(output_formatter, m)) and not m.startswith('__')]
        assert methods, 'No callable methods found on SharedOutputFormatter'

    def test_format_output(self, output_formatter):
        sample = UnifiedResultModel(
            status=UnifiedStatus.success,
            target="foo.txt",
            messages=[UnifiedMessageModel(summary="ok", level="info")],
            summary={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "fixed": 0, "warnings": 0}
        )
        output = output_formatter.format_output(sample, format_type="json")
        assert isinstance(output, UnifiedBatchResultModel)
        assert hasattr(output, "results")
        assert len(output.results) == 1
        result = output.results[0]
        assert result.status == UnifiedStatus.success
        assert result.target == "foo.txt"
        assert result.messages[0].summary == "ok"
        assert result.messages[0].level == "info"

    def test_text_output(self, output_formatter):
        sample_valid = UnifiedResultModel(
            status=UnifiedStatus.success,
            target="foo.txt",
            messages=[UnifiedMessageModel(summary="ok", level="info")],
            summary={"total": 1, "passed": 1, "failed": 0, "skipped": 0, "fixed": 0, "warnings": 0}
        )
        sample_invalid = UnifiedResultModel(
            status=UnifiedStatus.error,
            target="foo.txt",
            messages=[UnifiedMessageModel(summary="bad", level="error")],
            summary={"total": 1, "passed": 0, "failed": 1, "skipped": 0, "fixed": 0, "warnings": 0}
        )
        text_valid = output_formatter.render_output(sample_valid, format_type="text")
        text_invalid = output_formatter.render_output(sample_invalid, format_type="text")
        assert "✅" in text_valid
        assert "❌" in text_invalid
        assert "Validation passed" in text_valid
        assert "Validation failed" in text_invalid
        assert "bad" in text_invalid or "ok" in text_valid  # Accept either summary in output
        # JSON/YAML
        json_out = output_formatter.render_output(sample_valid, format_type="json")
        yaml_out = output_formatter.render_output(sample_valid, format_type="yaml")
        import json, yaml as yamllib
        assert json.loads(json_out)["results"][0]["status"] == "success"
        assert yamllib.safe_load(yaml_out)["results"][0]["status"] == "success"

# Standalone pytest functions for collection
def test_import_and_method(output_formatter):
    TestOrchestratorOutputFormatter().test_import_and_method(output_formatter)

def test_format_output(output_formatter):
    TestOrchestratorOutputFormatter().test_format_output(output_formatter)

def test_text_output(output_formatter):
    TestOrchestratorOutputFormatter().test_text_output(output_formatter)

# Remove lines 36-88 (TestOrchestratorOutputFormatter class and its methods)
# ... existing code ... 