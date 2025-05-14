# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "tool_orchestrator_fix_codebase"
# namespace: "omninode.tools.tool_orchestrator_fix_codebase"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "tool_orchestrator_fix_codebase.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["OrchestratorProtocol"]
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Tool Orchestrator (Fix Codebase): Implements OrchestratorProtocol, uses DI, ToolRegistry, and shared utilities.
This script is now registry-driven and only runs the standardized metadata stamper (metadata_stamper).
FixerRegistry is deprecated and not used here. See validator_refactor_checklist.yaml, validator_testing_standards.md
"""

from foundation.protocol.protocol_orchestrator import OrchestratorProtocol
from foundation.script.orchestrator.orchestrator_registry import OrchestratorRegistry
from foundation.script.orchestrator.orchestrator_config import OrchestratorConfig
from foundation.script.orchestrator.shared.orchestrator_cli_utils import OrchestratorCLIUtils
from foundation.script.orchestrator.shared.orchestrator_file_discovery import OrchestratorFileDiscovery
from foundation.script.orchestrator.shared.shared_output_formatter import SharedOutputFormatter
from foundation.protocol.protocol_process_runner import ProcessRunnerProtocol
from foundation.protocol.protocol_vcs_client import VCSClientProtocol
from foundation.protocol.protocol_output_formatter import OutputFormatterProtocol
from foundation.bootstrap.bootstrap import bootstrap
from foundation.model.model_unified_result import UnifiedBatchResultModel, UnifiedResultModel, UnifiedMessageModel, UnifiedSummaryModel, UnifiedStatus
from foundation.script.tool.tool_registry import ToolRegistry, populate_tool_registry
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from pathlib import Path
import sys
from typing import Optional
import logging

class ToolOrchestratorFixCodebase(OrchestratorProtocol):
    """
    DI/registry-compliant orchestrator for codebase fixing workflows.
    Implements OrchestratorProtocol and uses ToolRegistry for standardized fixers.
    Only the metadata stamper (metadata_stamper) is supported.
    """
    def __init__(self, registry=None, di_container=None, logger=None, config=None, process_runner=None, vcs_client=None, output_formatter: Optional[OutputFormatterProtocol] = None):
        self.registry = registry
        self.di_container = di_container
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or OrchestratorConfig()
        self.process_runner = process_runner  # type: ProcessRunnerProtocol
        self.vcs_client = vcs_client  # type: VCSClientProtocol
        self.output_formatter = output_formatter or SharedOutputFormatter()

    def run(self, args=None):
        # Parse args using DI/registry
        if args is None:
            args = self.parse_args()
        # Discover files to fix
        files = []
        if hasattr(args, 'targets') and args.targets:
            for t in args.targets:
                p = Path(t)
                if p.is_file() and p.suffix == ".py":
                    files.append(p)
                elif p.is_dir():
                    files.extend([f for f in p.rglob("*.py") if f.is_file()])
        else:
            files = [p for p in Path(".").rglob("*.py") if p.is_file()]
        if not files:
            msg = "No files to fix."
            if self.logger:
                self.logger.info(msg)
            result = UnifiedResultModel(
                status=UnifiedStatus.skipped,
                target=None,
                messages=[UnifiedMessageModel(summary=msg, level="info")],
                summary=UnifiedSummaryModel(total=0, passed=0, failed=0, skipped=0, fixed=0, warnings=0)
            )
            return UnifiedBatchResultModel(results=[result], messages=[UnifiedMessageModel(summary=msg, level="info")], summary=result.summary, status=UnifiedStatus.skipped)

        # --- Registry-driven metadata stamper discovery ---
        tool_registry = ToolRegistry()
        template_registry = MetadataRegistryTemplate()
        populate_tool_registry(tool_registry, template_registry)
        stamper_cls = tool_registry.get_tool("metadata_stamper")
        if not stamper_cls:
            msg = "No metadata stamper registered in tool_registry."
            if self.logger:
                self.logger.error(msg)
            result = UnifiedResultModel(
                status=UnifiedStatus.error,
                target=None,
                messages=[UnifiedMessageModel(summary=msg, level="error")],
                summary=UnifiedSummaryModel(total=0, passed=0, failed=1, skipped=0, fixed=0, warnings=0)
            )
            return UnifiedBatchResultModel(results=[result], messages=[UnifiedMessageModel(summary=msg, level="error")], summary=result.summary, status=UnifiedStatus.error)
        stamper = stamper_cls(logger=self.logger)

        # Run metadata stamper on all files
        batch_results = []
        for path in files:
            file_msgs = []
            file_status = UnifiedStatus.success
            try:
                changed = stamper.stamp_file(path, overwrite=not getattr(args, 'dry_run', False), logger=self.logger)
                if changed:
                    file_msgs.append(UnifiedMessageModel(summary=f"metadata_stamper fixed {path}", level="info"))
                else:
                    file_msgs.append(UnifiedMessageModel(summary=f"No changes needed for {path}", level="info"))
            except Exception as e:
                file_msgs.append(UnifiedMessageModel(summary=f"metadata_stamper failed on {path}: {e}", level="error"))
                file_status = UnifiedStatus.error
            summary = UnifiedSummaryModel(
                total=1,
                passed=1 if file_status == UnifiedStatus.success else 0,
                failed=1 if file_status == UnifiedStatus.error else 0,
                skipped=1 if file_status == UnifiedStatus.skipped else 0,
                fixed=1 if any("fixed" in m.summary for m in file_msgs) else 0,
                warnings=sum(1 for m in file_msgs if m.level == "warning")
            )
            batch_results.append(UnifiedResultModel(
                status=file_status,
                target=str(path),
                messages=file_msgs,
                summary=summary
            ))
        # Aggregate batch summary
        total = len(batch_results)
        passed = sum(1 for r in batch_results if r.status == UnifiedStatus.success)
        failed = sum(1 for r in batch_results if r.status == UnifiedStatus.error)
        skipped = sum(1 for r in batch_results if r.status == UnifiedStatus.skipped)
        fixed = sum(1 for r in batch_results for m in r.messages if "fixed" in m.summary)
        warnings = sum(1 for r in batch_results for m in r.messages if m.level == "warning")
        batch_summary = UnifiedSummaryModel(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            fixed=fixed,
            warnings=warnings
        )
        batch_status = UnifiedStatus.success if failed == 0 else UnifiedStatus.error
        return UnifiedBatchResultModel(
            results=batch_results,
            messages=[m for r in batch_results for m in r.messages],
            summary=batch_summary,
            status=batch_status
        )

    def parse_args(self, args=None):
        return OrchestratorCLIUtils.parse_args(args)

    def discover_targets(self, args=None):
        return OrchestratorFileDiscovery.discover_targets(args)

    def execute_actions(self, files, args=None):
        # No-op: Only metadata stamper is supported
        return []

    def summarize_results(self, results):
        return self.output_formatter.format_output(results, format_type="json")

# Update registry with actual class
OrchestratorRegistry().register("tool_orchestrator_fix_codebase", ToolOrchestratorFixCodebase)

if __name__ == "__main__":
    bootstrap()
    orchestrator = ToolOrchestratorFixCodebase()
    orchestrator.run()
