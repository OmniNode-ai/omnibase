import pytest
from foundation.script.orchestrator.orchestrator_registry import OrchestratorRegistry
from foundation.protocol.protocol_orchestrator import OrchestratorProtocol
from foundation.script.validate.validate_orchestrator import ValidateOrchestrator
from foundation.script.tool.tool_coverage_report import ToolCoverageReportOrchestrator
from foundation.script.tool.tool_orchestrator_fix_codebase import ToolOrchestratorFixCodebase
from foundation.script.tool.struct.struct_tool_index_cli import StructToolIndexCLI
from foundation.base.base_orchestrator_test import BaseOrchestratorTest

# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_orchestrator_registry"
# namespace: "omninode.tests.test_orchestrator_registry"
# meta_type: "test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_orchestrator_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Test_Metadata ===
"""
Canary registry test for orchestrator discovery and drift.
Ensures all orchestrators are registered and discoverable via the central registry.
Follows canary standards for registry-based test implementation.
"""

class TestOrchestratorRegistry(BaseOrchestratorTest):
    """
    Hybrid pattern: Subclass from BaseOrchestratorTest for standards compliance.
    All orchestrator registry tests must use this pattern.
    """
    def test_orchestrator_registry_import_and_list(self):
        registry = OrchestratorRegistry()
        result = registry.list()
        assert isinstance(result, list)

    def test_orchestrator_registry_drift(self):
        registry = OrchestratorRegistry()
        expected = {
            "validate_orchestrator": ValidateOrchestrator,
            "tool_coverage_report": ToolCoverageReportOrchestrator,
            "tool_orchestrator_fix_codebase": ToolOrchestratorFixCodebase,
            "struct_tool_index_cli": StructToolIndexCLI,
        }
        # Register all orchestrators
        for name, cls in expected.items():
            registry.register(name, cls)
        # Check all expected names are present
        registered_names = set(registry.list())
        assert registered_names == set(expected.keys()), f"Registry entries do not match expected: {registered_names} != {set(expected.keys())}"
        # Check all registered classes are correct
        for name in expected:
            orchestrator_cls = registry.get(name)
            assert orchestrator_cls is expected[name], f"Registry class for {name} does not match expected"
        # Protocol conformance is enforced by static analysis (mypy/pyright), not at runtime. Canary protocol: registry, identity, and drift checks only.

# Standalone pytest functions for collection

def test_orchestrator_registry_import_and_list():
    TestOrchestratorRegistry().test_orchestrator_registry_import_and_list()

def test_orchestrator_registry_drift():
    TestOrchestratorRegistry().test_orchestrator_registry_drift() 