#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_chunk"
# namespace: "omninode.tools.python_validate_chunk"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "python_validate_chunk.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolTestableCLI', 'ProtocolValidate']
# base_class: ['ProtocolTestableCLI', 'ProtocolValidate']
# mock_safe: true
# === /OmniNode:Metadata ===




"""
"""

import argparse
from typing import Any, Optional

import structlog
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.util.util_chunk_metrics import UtilChunkMetrics, ChunkMetricsProtocol
from foundation.protocol.protocol_testable_cli import ProtocolTestableCLI
from foundation.model.model_result_cli import ModelResultCLI
from foundation.model.model_unified_result import UnifiedResultModel, UnifiedStatus, UnifiedMessageModel

# Configurable thresholds (could be loaded from config in future)
MAX_LINES = 500
SOFT_LINE_LIMIT = 450
MAX_TOKENS = 2048
SOFT_TOKEN_LIMIT = 1800


class PythonValidateChunk(ProtocolValidate, ProtocolTestableCLI):
    description: str = (
        "Python implementation for the OmniNode Context-Aware Chunk Validator. Enforces line and token count thresholds for files/chunks."
    )

    def __init__(
        self,
        config: Optional[dict] = None,
        logger: Optional[Any] = None,
        chunk_metrics: Optional[ChunkMetricsProtocol] = None,
        **dependencies: Any,
    ) -> None:
        self.logger = logger or structlog.get_logger(__name__)
        self.max_lines = config.get("max_lines", MAX_LINES) if config else MAX_LINES
        self.soft_line_limit = (
            config.get("soft_line_limit", SOFT_LINE_LIMIT)
            if config
            else SOFT_LINE_LIMIT
        )
        self.max_tokens = config.get("max_tokens", MAX_TOKENS) if config else MAX_TOKENS
        self.soft_token_limit = (
            config.get("soft_token_limit", SOFT_TOKEN_LIMIT)
            if config
            else SOFT_TOKEN_LIMIT
        )
        self.tokenizer = dependencies.get("tokenizer")
        self.chunk_metrics = chunk_metrics or UtilChunkMetrics

    def validate(self, target: str, config: Optional[dict] = None) -> UnifiedResultModel:
        import os
        target_str = str(target)
        if not target_str.endswith(".py"):
            reason = "File extension is not .py; skipping chunk validation."
            self.logger.info(
                f"[SKIP] {target_str}: {reason}",
                file=target_str,
                reason=reason,
            )
            return UnifiedResultModel(
                is_valid=True,
                errors=[],
                warnings=[],
                metadata={"file": target_str, "skip_reason": reason},
                status=UnifiedStatus.INVALID_EXTENSION,
            )
        if not os.path.isfile(target_str):
            reason = f"Target path {target_str} does not exist or is not a file."
            self.logger.error(
                f"[ERROR] {target_str}: {reason}",
                file=target_str,
                reason=reason,
            )
            return UnifiedResultModel(
                is_valid=False,
                errors=[
                    UnifiedMessageModel(
                        type="error",
                        summary=reason,
                        file=target_str,
                        severity="error",
                        level="error"
                    )
                ],
                warnings=[],
                metadata={"file": target_str, "error_reason": reason},
                status=UnifiedStatus.ERROR,
            )
        # Read file
        content = self.chunk_metrics.read_file(target_str)
        line_count = self.chunk_metrics.count_lines(target_str)
        token_count = self.chunk_metrics.count_tokens(content, self.tokenizer)
        self.logger.info(
            "validation_result",
            file=target_str,
            line_count=line_count,
            token_count=token_count,
            max_lines=self.max_lines,
            soft_line_limit=self.soft_line_limit,
            max_tokens=self.max_tokens,
            soft_token_limit=self.soft_token_limit,
        )
        errors = []
        warnings = []
        # Line count checks
        if line_count > self.max_lines:
            errors.append(
                UnifiedMessageModel(
                    type="error",
                    summary=f"Line count {line_count} exceeds max {self.max_lines}",
                    file=target_str,
                    severity="error",
                    level="error"
                )
            )
        elif line_count > self.soft_line_limit:
            warnings.append(
                UnifiedMessageModel(
                    type="warning",
                    summary=f"Line count {line_count} exceeds soft limit {self.soft_line_limit}",
                    file=target_str,
                    severity="warning",
                    level="warning"
                )
            )
        # Token count checks
        if token_count > self.max_tokens:
            errors.append(
                UnifiedMessageModel(
                    type="error",
                    summary=f"Token count {token_count} exceeds max {self.max_tokens}",
                    file=target_str,
                    severity="error",
                    level="error"
                )
            )
        elif token_count > self.soft_token_limit:
            warnings.append(
                UnifiedMessageModel(
                    type="warning",
                    summary=f"Token count {token_count} exceeds soft limit {self.soft_token_limit}",
                    file=target_str,
                    severity="warning",
                    level="warning"
                )
            )
        is_valid = not errors
        self.logger.info(
            "validation_metadata",
            file=target_str,
            line_count=line_count,
            token_count=token_count,
            errors=[e.summary for e in errors],
            warnings=[w.summary for w in warnings],
            is_valid=is_valid,
        )
        if errors:
            status = UnifiedStatus.INVALID
        elif warnings:
            status = UnifiedStatus.WARNING
        else:
            status = UnifiedStatus.VALID
        return UnifiedResultModel(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata={
                "file": target_str,
                "line_count": line_count,
                "token_count": token_count,
                "max_lines": self.max_lines,
                "soft_line_limit": self.soft_line_limit,
                "max_tokens": self.max_tokens,
                "soft_token_limit": self.soft_token_limit,
            },
            status=status,
        )

    def get_name(self) -> str:
        return "python_chunk"

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument("target", type=str, help="Target file to validate")
        return parser

    def main(self, argv: list) -> ModelResultCLI:
        """ProtocolTestableCLI-compliant main method. Returns ModelResultCLI."""
        parser = self.get_parser()
        args = parser.parse_args(argv)
        result = self.validate(args.target)
        return ModelResultCLI(
            exit_code=0 if result.is_valid else 1,
            output=None,  # Optionally, add summary or log output here
            errors=[e.summary for e in result.errors] if result.errors else None,
            result=result.model_dump(),
            metadata={
                "file": args.target,
                "line_count": result.metadata.get("line_count") if result.metadata else None,
                "token_count": result.metadata.get("token_count") if result.metadata else None,
            },
        )

    def run(self, args) -> int:
        result = self.validate(args.target)
        return 0 if result.is_valid else 1

    def validate_main(self, args) -> int:
        return self.run(args)

    @classmethod
    def metadata(cls) -> "MetadataBlockModel":
        from foundation.model.model_metadata import MetadataBlockModel
        return MetadataBlockModel(
            metadata_version="0.1",
            name="python_validate_chunk",
            namespace="omninode.tools.python_validate_chunk",
            version="0.1.0",
            entrypoint="python_validate_chunk.py",
            protocols_supported=["O.N.E. v0.1"],
            author="OmniNode Team",
            owner="jonah@omninode.ai",
            copyright="Copyright (c) 2025 OmniNode.ai",
            created_at="2025-05-05T18:25:48+00:00",
            last_modified_at="2025-05-05T18:25:48+00:00",
            protocol_version="0.1.0",
            description="Python implementation for the OmniNode Context-Aware Chunk Validator. Enforces line and token count thresholds for files/chunks.",
            tags=["python", "chunk", "validator"],
            dependencies=[],
            config={}
        )


# Minimal structlog config (if not already present in project)
try:
    structlog.get_config()
except Exception:
    structlog.configure(
        processors=[structlog.processors.JSONRenderer()],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )