#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: cli_base
# namespace: omninode.tools.cli_base
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:07+00:00
# last_modified_at: 2025-04-27T18:13:07+00:00
# entrypoint: cli_base.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
cli_base.py
OmniNode Foundation: Abstract base class for CLI utility scripts.
"""
import abc
import argparse
import logging
from pathlib import Path


class BaseUtilityCLI(abc.ABC):
    """
    Abstract base class for CLI utility scripts.
    Enforces: --help/usage, file/dir/no-arg dispatch, logging, and exit codes.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.args = self.parse_args()

    @abc.abstractmethod
    def cli_main(self) -> int:
        """
        Main entrypoint for the CLI utility. Should return exit code.
        """
        pass

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description=self.__class__.__doc__ or "CLI Utility"
        )
        parser.add_argument(
            "target",
            nargs="?",
            default=None,
            help="File or directory to process (default: staged files)",
        )
        parser.add_argument(
            "--log-level", default="INFO", help="Set log level (default: INFO)"
        )
        return parser.parse_args()

    def dispatch(self):
        logging.basicConfig(
            level=getattr(logging, self.args.log_level.upper(), logging.INFO)
        )
        if self.args.target is None:
            return self.handle_staged()
        path = Path(self.args.target)
        if path.is_file():
            return self.handle_file(path)
        elif path.is_dir():
            return self.handle_directory(path)
        else:
            self.logger.error(
                f"Target {self.args.target} is not a valid file or directory."
            )
            return 1

    @abc.abstractmethod
    def handle_staged(self) -> int:
        """Handle the case where no target is specified (e.g., staged files)."""
        pass

    @abc.abstractmethod
    def handle_file(self, file_path: Path) -> int:
        """Handle a single file."""
        pass

    @abc.abstractmethod
    def handle_directory(self, dir_path: Path) -> int:
        """Handle a directory (recursively process .py files)."""
        pass

    def __call__(self):
        return self.cli_main()


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    import sys

    sys.exit(BaseUtilityCLI().cli_main())
