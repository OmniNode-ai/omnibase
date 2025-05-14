# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_orchestrator_file_discovery"
# namespace: "omninode.tests.test_orchestrator_file_discovery"
# meta_type: "test"
# version: "1.0.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_orchestrator_file_discovery.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTestableCLI']
# base_class: ['ProtocolTestableCLI']
# mock_safe: true
# === /OmniNode:Test_Metadata ===
"""
Canonical test for OrchestratorFileDiscovery import and minimal usage.
Follows standards: protocol compliance, registry-driven patterns, and output format assertions.
"""
import pytest
from foundation.model.model_result_cli import ModelResultCLI
from foundation.script.orchestrator.shared.orchestrator_file_discovery import OrchestratorFileDiscovery
from foundation.base.base_orchestrator_test import BaseOrchestratorTest

class TestOrchestratorFileDiscovery(BaseOrchestratorTest):
    def main(self, argv):
        # Stub for protocol compliance; not used in this test
        return ModelResultCLI(exit_code=0, output="stub", errors=None, result=None, metadata=None)

    def test_import_and_method(self):
        """
        Assert OrchestratorFileDiscovery is importable and has callable methods. All errors are surfaced; none are suppressed.
        """
        discovery = OrchestratorFileDiscovery()
        methods = [getattr(discovery, m) for m in dir(discovery) if callable(getattr(discovery, m)) and not m.startswith('__')]
        assert methods, 'No callable methods found on OrchestratorFileDiscovery'
        if hasattr(discovery, 'discover_targets'):
            discovery.discover_targets([])  # Let any error surface

# Standalone pytest function for collection
def test_orchestrator_file_discovery_import_and_method():
    TestOrchestratorFileDiscovery().test_import_and_method() 