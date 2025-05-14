# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_cli_tool"
# namespace: "omninode.tools.protocol_cli_tool"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:01+00:00"
# last_modified_at: "2025-05-05T12:44:01+00:00"
# entrypoint: "protocol_cli_tool.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Any, Optional, List
import argparse
import logging
import sys

class ProtocolCLITool(Protocol):
    """
    Protocol for all CLI tool entrypoints in the Foundation codebase.
    Enforces standard methods for argument parsing, execution, and main entrypoint.
    """
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        ...

    def run(self, args: argparse.Namespace) -> int:
        ...

    def main(self, argv: Optional[List[str]] = None) -> int:
        ...

class CLIToolMixin:
    """
    Mixin for CLI tools providing standard argument parsing, logger setup, and error handling.
    Implements main() and get_parser() for CLI entrypoints.
    """
    description: str = "CLI Tool"
    logger: Any = None

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=getattr(self, 'description', self.__class__.__name__))
        parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
        self.add_arguments(parser)
        return parser

    def setup_logger(self, verbose: bool = False, name: Optional[str] = None) -> logging.Logger:
        logger = logging.getLogger(name or self.__class__.__name__)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(handler)
        logger.setLevel(logging.INFO if verbose else logging.WARNING)
        self.logger = logger
        return logger

    def main(self, argv: Optional[List[str]] = None) -> int:
        parser = self.get_parser()
        args = parser.parse_args(argv)
        self.setup_logger(getattr(args, 'verbose', False))
        try:
            return self.run(args)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error: {e}")
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1 