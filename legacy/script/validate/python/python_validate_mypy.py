#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_mypy
# namespace: omninode.tools.validate_mypy
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-29T00:00:00+00:00
# last_modified_at: 2025-04-29T00:00:00+00:00
# entrypoint: validate_mypy.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
MypyValidator: Foundation-compliant static type checker using mypy.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationResult


class MypyValidator(ProtocolValidate):
    def __init__(
        self, config: Optional[Dict] = None, runner=None, logger=None, **dependencies
    ):
        super().__init__(config)
        self.runner = runner or subprocess.run
        self.config_path = self.config.get(
            "mypy_config",
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), "././././././pyproject.toml")
            ),
        )
        self.version = self.config.get("version", "v1")
        self.logger = logger or dependencies.get("logger")

    def get_name(self) -> str:
        return "mypy"

    def validate(self, target: Path, config: Optional[dict] = None) -> ValidationResult:
        """Run mypy on the target path."""
        path = str(target.resolve())
        if self.logger:
            self.logger.debug(f"[DEBUG] Running mypy on: {path}")
            self.logger.debug(f"[DEBUG] Using config: {self.config_path}")
            self.logger.debug(f"[DEBUG] CWD: {os.getcwd()}")
        # Run mypy with the config file
        result = self.runner(
            [
                "mypy",
                path,
                f"--config-file={self.config_path}",
                "--show-error-codes",
                "--no-color-output",
            ],
            capture_output=True,
            text=True,
        )
        if self.logger:
            self.logger.debug(f"[DEBUG] mypy return code: {result.returncode}")
            self.logger.debug(f"[DEBUG] mypy stdout: {result.stdout}")
            self.logger.debug(f"[DEBUG] mypy stderr: {result.stderr}")
        if result.returncode != 0:
            for line in result.stdout.splitlines():
                if line.strip():
                    # Parse mypy output: filename:line: col: error_type: message
                    parts = line.split(":", 3)
                    if len(parts) >= 4:
                        file, line_num, col, rest = parts
                        message = rest.strip()
                        self.add_error(
                            message=message,
                            file=file.strip(),
                            line=int(line_num.strip()),
                            type="error",
                        )
                    else:
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

    @staticmethod
    def cli():

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
        )
        logger = logging.getLogger(__name__)
        parser = argparse.ArgumentParser(
            description="Validate Python type hints and Protocol/DI/registry compliance using mypy (Foundation standard)"
        )
        parser.add_argument(
            "--path",
            default="containers/foundation/src/foundation/",
            help="Path to lint (default: foundation source)",
        )
        parser.add_argument(
            "--config",
            default=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "././././././pyproject.toml")
            ),
            help="Path to mypy config file",
        )
        args = parser.parse_args()
        validator = MypyValidator(config={"mypy_config": args.config})
        is_valid = validator.validate(Path(args.path))
        logger.info("Mypy validation complete.")
        print(validator.model_dump())
        sys.exit(0 if is_valid.is_valid else 1)


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    MypyValidator.cli()
