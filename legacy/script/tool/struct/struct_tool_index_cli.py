# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "struct_tool_index_cli"
# namespace: "omninode.tools.struct_tool_index_cli"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:01+00:00"
# last_modified_at: "2025-05-05T12:44:01+00:00"
# entrypoint: "struct_tool_index_cli.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["OrchestratorProtocol", "CLIToolMixin", "ProtocolCLITool"]
# base_class: ["CLIToolMixin", "ProtocolCLITool"]
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Struct Tool Index Orchestrator: Implements OrchestratorProtocol, uses DI, registry, and shared utilities.
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
from foundation.bootstrap.bootstrap import bootstrap
from foundation.protocol.protocol_cli_tool import ProtocolCLITool, CLIToolMixin
from foundation.script.tool.struct.struct_index import StructIndex
from foundation.util.util_tree_format_utils import UtilTreeFormatUtils
from foundation.util.util_file_output_writer import UtilFileOutputWriter
from foundation.util.util_hash_utils import UtilHashUtils
from pathlib import Path
import argparse
import sys
from foundation.protocol.protocol_output_formatter import OutputFormatterProtocol
from foundation.model.model_unified_result import UnifiedBatchResultModel, UnifiedResultModel, UnifiedMessageModel, UnifiedSummaryModel, UnifiedStatus
from typing import Optional
from foundation.protocol.protocol_logger import ProtocolLogger

class StructToolIndexCLI(CLIToolMixin, ProtocolCLITool, OrchestratorProtocol):
    description = "StructIndex: Canonical directory tree indexer."

    def __init__(self, registry=None, di_container=None, logger: ProtocolLogger = None, config=None, process_runner=None, vcs_client=None, output_formatter: Optional[OutputFormatterProtocol] = None):
        self.registry = registry
        self.di_container = di_container
        self.logger: ProtocolLogger = logger
        self.config = config or OrchestratorConfig()
        self.process_runner = process_runner  # type: ProcessRunnerProtocol
        self.vcs_client = vcs_client  # type: VCSClientProtocol
        self.output_formatter = output_formatter or SharedOutputFormatter()

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--target", type=str, required=True, help="Root directory to index")
        parser.add_argument("--max-depth", type=int, default=-1, help="Maximum directory depth (-1 for unlimited)")
        parser.add_argument("--include", type=str, default=None, help="Glob pattern to include (e.g. *.py)")
        parser.add_argument("--exclude", type=str, default=None, help="Glob pattern to exclude")
        parser.add_argument("--follow-symlinks", action="store_true", help="Follow symlinks")
        parser.add_argument("--write", action="store_true", help="Write .tree/.yaml files (default: dry-run)")
        parser.add_argument("--yaml", action="store_true", help="Output .tree.yaml files as well")
        parser.add_argument("--flat", action="store_true", help="Output .tree.flat files (flat list)")
        parser.add_argument("--with-metadata", action="store_true", help="Include file size/mtime in output")
        parser.add_argument("--output-dir", type=str, default=None, help="Directory to write output files (preserves relative structure)")

    def run(self, args=None):
        if args is None:
            args = self.parse_args()
        result = self._run_existing(args)
        return self.summarize_results(result, args)

    def _run_existing(self, args):
        root = Path(args.target).resolve()
        output_dir = Path(args.output_dir).resolve() if args.output_dir else None
        if not root.exists() or not root.is_dir():
            self.logger.error(f"Target directory does not exist: {root}")
            return {
                "status": "error",
                "target": str(root),
                "messages": [
                    {"summary": f"Target directory does not exist: {root}", "level": "error"}
                ],
                "summary": {"total": 0, "passed": 0, "failed": 1, "skipped": 0, "fixed": 0, "warnings": 0},
            }
        indexer = StructIndex(
            self.logger,
            tree_format_utils=UtilTreeFormatUtils,
            file_output_writer=UtilFileOutputWriter,
            hash_utils=UtilHashUtils,
        )
        node = indexer.build_tree(
            root,
            max_depth=args.max_depth,
            include=args.include,
            exclude=args.exclude,
            follow_symlinks=args.follow_symlinks,
            flat=args.flat,
            with_metadata=args.with_metadata,
            verbose=getattr(args, 'verbose', False)
        )
        if node:
            indexer.write_tree_files(
                root,
                node,
                write=args.write,
                as_yaml=args.yaml,
                flat=args.flat,
                with_metadata=args.with_metadata,
                verbose=getattr(args, 'verbose', False),
                output_dir=output_dir
            )
            return {
                "status": "success",
                "target": str(root),
                "messages": [
                    {"summary": f"Tree index generated for {root}", "level": "info"}
                ],
                "summary": {"total": 1, "passed": 1, "failed": 0, "skipped": 0, "fixed": 0, "warnings": 0},
                "node": node.model_dump() if hasattr(node, 'model_dump') else node.dict() if hasattr(node, 'dict') else None
            }
        else:
            self.logger.warning(f"No tree generated for {root}")
            return {
                "status": "error",
                "target": str(root),
                "messages": [
                    {"summary": f"No tree generated for {root}", "level": "error"}
                ],
                "summary": {"total": 1, "passed": 0, "failed": 1, "skipped": 0, "fixed": 0, "warnings": 0},
            }

    def parse_args(self, args=None):
        parser = argparse.ArgumentParser(description=self.description)
        self.add_arguments(parser)
        return parser.parse_args(args)

    def discover_targets(self, args=None):
        return OrchestratorFileDiscovery.discover_targets(args)

    def execute_actions(self, files, args=None):
        # TODO: Refactor main tool loop here using DI/registry
        return []

    def summarize_results(self, results, args=None):
        # Convert legacy dict to UnifiedBatchResultModel
        if isinstance(results, dict):
            status = UnifiedStatus(results.get("status", "unknown"))
            messages = [UnifiedMessageModel(**m) for m in results.get("messages", [])]
            summary = UnifiedSummaryModel(**results.get("summary", {})) if results.get("summary") else None
            node = results.get("node")
            unified_result = UnifiedResultModel(
                status=status,
                target=results.get("target"),
                messages=messages,
                summary=summary,
                metadata={"node": node} if node else None
            )
            batch = UnifiedBatchResultModel(
                results=[unified_result],
                messages=messages,
                summary=summary,
                status=status
            )
            return batch
        return results

# Register orchestrator in registry (after class definition)
OrchestratorRegistry().register("struct_tool_index_cli", StructToolIndexCLI)

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    import structlog
    from foundation.protocol.protocol_logger import ProtocolLogger
    bootstrap()
    logger: ProtocolLogger = structlog.get_logger("struct_tool_index_cli")  # type: ignore
    result = StructToolIndexCLI(logger=logger).run()
    # Print summary and exit code for CLI usage
    # Use attribute access for UnifiedBatchResultModel
    status = getattr(result, "status", None)
    if status == "error":
        print(result.model_dump())
        logger.error("StructToolIndexCLI finished with errors.")
        sys.exit(1)
    else:
        print(result.model_dump())
        logger.info("StructToolIndexCLI finished successfully.")
        sys.exit(0) 