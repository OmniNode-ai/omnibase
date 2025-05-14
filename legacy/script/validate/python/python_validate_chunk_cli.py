#!/usr/bin/env python3
"""
# === OmniNode:Validator_Metadata ===
# metadata_version: 0.1
# name: chunk
# namespace: foundation.script.validate
# version: 0.1.0
# author: foundation-team
# description: OmniNode Context-Aware Chunk Validator shell entrypoint. Enforces line and token count thresholds for files/chunks. Uses DI, Protocols, and metadata-driven registry discovery. Delegates to the Python implementation in validate/python/validate_python_chunk.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Validator_Metadata ===
"""

import argparse
import sys
import structlog
from typing import Any, Optional, Union
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.script.validate.python.python_validate_chunk import PythonValidateChunk
from foundation.model.model_validate import ValidationResult

class PythonValidateChunkCLI(ProtocolValidate):
    description = "Chunk Validator CLI"
    logger: Any

    def __init__(self, logger: Any = None):
        self.logger = logger or structlog.get_logger("chunk_validator_cli")

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument("file", help="Path to the file to validate")
        # No --apply or --dry-run allowed
        return parser

    def main(self, argv: Optional[list[str]] = None) -> int:
        parser = self.get_parser()
        args = parser.parse_args(argv)
        return self.run(args)

    def run(self, args) -> int:
        return self.validate_main(args)

    def validate_main(self, args) -> int:
        validator = PythonValidateChunk(logger=self.logger)
        result = validator.validate(args.file)
        self.logger.info("validation_result_json", result=result.json())
        return 0 if result.is_valid else 1

    def validate(self, target, config=None) -> Union[dict, ValidationResult]:
        validator = PythonValidateChunk(logger=self.logger)
        return validator.validate(target, config=config)

    def get_name(self) -> str:
        return "chunk"

if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(PythonValidateChunkCLI().main())
