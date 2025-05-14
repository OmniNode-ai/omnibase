#!/usr/bin/env python3
"""
# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: chunk_tool
# namespace: foundation.script.tool
# version: 0.1.0
# author: foundation-team
# description: OmniNode Context-Aware Chunk Tool shell entrypoint. Supports dry-run and apply modes for chunk processing. Uses DI, Protocols, and metadata-driven registry discovery. Delegates to the Python implementation in tool/python/tool_python_chunk.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===
"""
import argparse
import sys
import structlog
from typing import Any, Optional
from foundation.protocol.protocol_tool import ProtocolTool
from foundation.script.tool.python.python_tool_chunk import PythonToolChunk
from foundation.script.validate.python.python_validate_chunk import PythonChunkValidator

class PythonToolChunkCLI(ProtocolTool):
    description = "Chunk Tool CLI"
    logger: Any

    def __init__(self, logger: Any = None):
        self.logger = logger or structlog.get_logger("chunk_tool_cli")

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument("file", help="Path to the file to process")
        parser.add_argument("--apply", action="store_true", help="Actually modify files (default: dry-run, no changes)")
        return parser

    def main(self, argv: Optional[list[str]] = None) -> int:
        parser = self.get_parser()
        args = parser.parse_args(argv)
        return self.run(args)

    def run(self, args) -> int:
        if not getattr(args, "apply", False):
            self.logger.info("[DRY RUN] No changes written. Use --apply to modify files.")
            return self.dry_run_main(args)
        return self.apply_main(args)

    def dry_run_main(self, args) -> int:
        validator = PythonChunkValidator(logger=self.logger)
        tool = PythonToolChunk(validator=validator, logger=self.logger)
        result = tool.process(args.file)
        self.logger.info("tool_result_json", result=result.json())
        return 0 if result.is_valid else 1

    def apply_main(self, args) -> int:
        # For this tool, assume apply is a no-op or placeholder for future modification logic
        validator = PythonChunkValidator(logger=self.logger)
        tool = PythonToolChunk(validator=validator, logger=self.logger)
        result = tool.process(args.file)
        self.logger.info("tool_result_json", result=result.json())
        # In a real tool, file-modifying logic would go here
        return 0 if result.is_valid else 1

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(PythonToolChunkCLI().main())
