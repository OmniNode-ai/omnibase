#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_docstrings
# namespace: omninode.tools.validate_docstrings
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:58+00:00
# last_modified_at: 2025-04-27T18:12:58+00:00
# entrypoint: validate_docstrings.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
DocstringValidator: Foundation-compliant docstring linter using pydocstyle.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationResult
from foundation.model.model_validation_issue_mixin import ValidationIssueMixin


class DocstringValidator(ValidationIssueMixin, ProtocolValidate):
    def __init__(
        self, config: Optional[Dict] = None, runner=None, logger=None, **dependencies
    ):
        super().__init__(config)
        self.runner = runner or subprocess.run
        self.config_path = self.config.get(
            "pydocstyle_config",
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), "././././././.pydocstyle")
            ),
        )
        self.version = self.config.get("version", "v1")
        self.logger = logger or dependencies.get("logger")
        self.config: dict = config or {}
        self.errors: list = []
        self.warnings: list = []
        self.failed_files: list = []

    def get_name(self) -> str:
        return "docstrings"

    def validate(self, target: Path, config: Optional[dict] = None) -> ValidationResult:
        """Run pydocstyle on the target path."""
        path = str(target.resolve())
        if self.logger:
            self.logger.debug(f"[DEBUG] Running pydocstyle on: {path}")
            self.logger.debug(f"[DEBUG] Using config: {self.config_path}")
            self.logger.debug(f"[DEBUG] CWD: {os.getcwd()}")
        result = self.runner(
            ["pydocstyle", path, f"--config={self.config_path}"],
            capture_output=True,
            text=True,
        )
        if self.logger:
            self.logger.debug(f"[DEBUG] pydocstyle return code: {result.returncode}")
            self.logger.debug(f"[DEBUG] pydocstyle stdout: {result.stdout}")
            self.logger.debug(f"[DEBUG] pydocstyle stderr: {result.stderr}")
        if result.returncode != 0:
            for line in result.stdout.splitlines():
                if line.strip():
                    self.add_error(message=line.strip(), file=path, type="error")
            self.add_failed_file(path)
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                version=self.version,
            )
        return ValidationResult(
            is_valid=True,
            errors=self.errors,
            warnings=self.warnings,
            version=self.version,
        )

    def _validate(self, *args, **kwargs):
        # No-op for abstract method requirement
        pass

    def describe_flags(self):
        """No-op for protocol compliance."""
        return None

    @staticmethod
    def cli():

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
        )
        logger = logging.getLogger(__name__)
        parser = argparse.ArgumentParser(
            description="Validate Python docstrings using pydocstyle (Foundation standard)"
        )
        parser.add_argument(
            "--path",
            default="containers/foundation/src/foundation.script.validation/",
            help="Path to lint (default: validation scripts)",
        )
        parser.add_argument(
            "--config",
            default=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "././././././.pydocstyle")
            ),
            help="Path to pydocstyle config file",
        )
        args = parser.parse_args()
        validator = DocstringValidator(config={"pydocstyle_config": args.config})
        is_valid = validator.validate(Path(args.path))
        logger.info("Docstring validation complete.")
        print(validator.model_dump())
        sys.exit(0 if is_valid.is_valid else 1)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    DocstringValidator.cli()
