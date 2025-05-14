# === OmniNode:BaseTest_Orchestrator ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "base_orchestrator_test"
# namespace: "foundation.base"
# meta_type: "base_test"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "foundation-team"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-11T00:00:00+00:00"
# last_modified_at: "2025-05-11T00:00:00+00:00"
# entrypoint: "base_orchestrator_test.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:BaseTest_Orchestrator ===

"""
CLITestIsolationMixin: Use for all CLI/Orchestrator tests to patch sys.argv and isolate from pytest arguments.
Usage:
    class MyOrchestratorTest(CLITestIsolationMixin):
        def test_something(self):
            with self.cli_args(["orchestrator", "--help"]):
                ...
"""
import sys
from contextlib import contextmanager
from typing import List

class CLITestIsolationMixin:
    @contextmanager
    def cli_args(self, args: List[str]):
        old_argv = sys.argv[:]
        sys.argv = args[:]
        try:
            yield
        finally:
            sys.argv = old_argv

class BaseOrchestratorTest(CLITestIsolationMixin):
    pass 