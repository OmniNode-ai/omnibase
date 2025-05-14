# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "tool_coverage_report"
# namespace: "omninode.tools.tool_coverage_report"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "tool_coverage_report.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["OrchestratorProtocol"]
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Tool Coverage Report Orchestrator: Implements OrchestratorProtocol, uses DI, registry, and shared utilities.
See: validator_refactor_checklist.yaml, validator_testing_standards.md
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
import json
import sys
import structlog
from typing import Optional
from foundation.protocol.protocol_logger import ProtocolLogger

class ToolCoverageReportOrchestrator(OrchestratorProtocol):
    """
    DI/registry-compliant orchestrator for coverage reporting workflows.
    Implements OrchestratorProtocol and uses shared utilities.
    """
    def __init__(
        self,
        registry=None,
        di_container=None,
        logger: Optional[ProtocolLogger] = None,
        config=None,
        process_runner=None,
        vcs_client=None,
        output_formatter: Optional[OutputFormatterProtocol] = None,
        file_loader=None,
        json_loader=None,
    ):
        self.registry = registry
        self.di_container = di_container
        self.logger = logger
        self.config = config or OrchestratorConfig()
        self.process_runner = process_runner  # type: ProcessRunnerProtocol
        self.vcs_client = vcs_client  # type: VCSClientProtocol
        self.output_formatter = output_formatter or SharedOutputFormatter()
        self.file_loader = file_loader or open
        self.json_loader = json_loader or json.load

    def run(self, *args, **kwargs):
        results = self.analyze_coverage()
        return self.summarize_results(results)

    def parse_args(self, args=None):
        return OrchestratorCLIUtils.parse_args(args)

    def discover_targets(self, args=None):
        return OrchestratorFileDiscovery.discover_targets(args)

    def execute_actions(self, files, args=None):
        # TODO: Refactor main tool loop here using DI/registry
        return []

    def summarize_results(self, results):
        return self.output_formatter.format_output(results, format_type="json")

    def analyze_coverage(self):
        # Use DI for file and JSON loading
        coverage_path = getattr(self.config, "coverage_path", "coverage.json")
        try:
            with self.file_loader(coverage_path) as f:
                data = self.json_loader(f)
        except FileNotFoundError:
            if self.logger:
                self.logger.error(f"Coverage file not found: {coverage_path}")
            return {
                "status": "error",
                "messages": [
                    {"summary": f"{coverage_path} not found", "level": "error"}
                ],
                "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "fixed": 0, "warnings": 0},
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading coverage file: {e}")
            return {
                "status": "error",
                "messages": [
                    {"summary": f"Error loading {coverage_path}: {e}", "level": "error"}
                ],
                "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "fixed": 0, "warnings": 0},
            }

        if not data.get("files"):
            if self.logger:
                self.logger.error(f"Coverage file {coverage_path} is empty or contains no files")
            return {
                "status": "error",
                "messages": [
                    {"summary": f"{coverage_path} is empty or contains no files", "level": "error"}
                ],
                "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "fixed": 0, "warnings": 0},
            }

        MIN_COVERAGE = getattr(self.config, "min_coverage", 30)
        modules = {}
        for file, stats in data["files"].items():
            parts = file.split("/")
            if "foundation" in parts and "src" in parts:
                idx = parts.index("src")
                if len(parts) > idx + 2:
                    mod = parts[idx + 2]
                    modules.setdefault(mod, {"covered": 0, "total": 0})
                    executed = len(stats.get("executed_lines", []))
                    missing = len(stats.get("missing_lines", []))
                    total = executed + missing
                    modules[mod]["covered"] += executed
                    modules[mod]["total"] += total

        failed_subsystems = []
        results = []
        for mod in sorted(modules.keys()):
            if modules[mod]["total"] == 0:
                continue
            cov = (
                modules[mod]["covered"] / modules[mod]["total"] * 100
                if modules[mod]["total"] > 0
                else 0
            )
            status = "success" if cov >= MIN_COVERAGE else "error"
            if cov < MIN_COVERAGE:
                failed_subsystems.append((mod, cov))
            results.append({
                "subsystem": mod,
                "coverage": cov,
                "statements": modules[mod]["total"],
                "covered": modules[mod]["covered"],
                "status": status,
            })

        total_covered = sum(m["covered"] for m in modules.values())
        total_statements = sum(m["total"] for m in modules.values())
        overall = total_covered / total_statements * 100 if total_statements > 0 else 0
        overall_status = "success" if not failed_subsystems else "error"
        messages = []
        if failed_subsystems:
            for subsystem, coverage in failed_subsystems:
                gap = MIN_COVERAGE - coverage
                messages.append({
                    "summary": f"{subsystem} below minimum coverage: {coverage:.1f}% (gap: {gap:.1f}%)",
                    "level": "error",
                })
            messages.append({
                "summary": f"Coverage check failed! Some subsystems are below the minimum threshold ({MIN_COVERAGE}%)",
                "level": "error",
            })
        else:
            messages.append({
                "summary": f"Success! All subsystems meet the minimum coverage threshold of {MIN_COVERAGE}%",
                "level": "info",
            })
        summary = {
            "total": len(modules),
            "passed": len(modules) - len(failed_subsystems),
            "failed": len(failed_subsystems),
            "skipped": 0,
            "fixed": 0,
            "warnings": 0,
        }
        return {
            "status": overall_status,
            "target": coverage_path,
            "results": results,
            "messages": messages,
            "summary": summary,
            "overall_coverage": overall,
        }

# Update registry with actual class
OrchestratorRegistry().register("tool_coverage_report", ToolCoverageReportOrchestrator)

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    import structlog
    from foundation.protocol.protocol_logger import ProtocolLogger
    bootstrap()
    logger: ProtocolLogger = structlog.get_logger("tool_coverage_report")  # type: ignore
    config = OrchestratorConfig()
    result = ToolCoverageReportOrchestrator(config=config, logger=logger).run()
    # Print summary and exit code for CLI usage
    if result["status"] == "error":
        print(json.dumps(result, indent=2))
        logger.error("ToolCoverageReportOrchestrator finished with errors.")
        sys.exit(1)
    else:
        print(json.dumps(result, indent=2))
        logger.info("ToolCoverageReportOrchestrator finished successfully.")
        sys.exit(0)
