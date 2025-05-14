#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_performance_antipatterns
# namespace: omninode.tools.validate_performance_antipatterns
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:05+00:00
# last_modified_at: 2025-04-27T18:13:05+00:00
# entrypoint: validate_performance_antipatterns.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_performance_antipatterns.py containers.foundation.src.foundation.sc
ripts.validation.validate_performance_antipatterns.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)


class PerformanceAntipatternsValidatorConfig(ValidatorConfig):
    version: str = "v1"
    exclude_dirs: List[str] = []
    flag_n_plus_one: bool = True
    flag_inefficient_loops: bool = True
    flag_blocking_in_async: bool = True
    max_loop_length: int = 20


    name="performance_antipatterns",
    version="v1",
    group="quality",
    description="Detects common performance anti-patterns (N+1 queries, inefficient loops, blocking calls in async code).",
)
class PerformanceAntipatternsValidator(ProtocolValidate):
    """Detects common performance anti-patterns (N+1 queries, inefficient
    loops, blocking calls in async code)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = PerformanceAntipatternsValidatorConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="performance_antipatterns",
            group="quality",
            description="Detects common performance anti-patterns (N+1 queries, inefficient loops, blocking calls in async code).",
            version="v1",
        )

    def get_name(self) -> str:
        return "performance_antipatterns"

    def validate(
        self,
        target: Path,
        config: Optional[PerformanceAntipatternsValidatorConfig] = None,
    ) -> ValidationResult:
        cfg = config or self.config
        errors = []
        warnings = []
        suggestions = []
        is_valid = True
        python_files = [
            f
            for f in target.rglob("*.py")
            if not any(ex in f.parts for ex in cfg.exclude_dirs)
        ]
        for file in python_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(file))
                for node in ast.walk(tree):
                    # Inefficient loops: flag long loops
                    if cfg.flag_inefficient_loops and isinstance(
                        node, (ast.For, ast.While)
                    ):
                        loop_len = len(node.body)
                        if loop_len > cfg.max_loop_length:
                            is_valid = False
                            msg = f"{file}:{node.lineno}: Loop has {loop_len} statements (max allowed: {cfg.max_loop_length})"
                            errors.append(msg)
                            suggestions.append(
                                f"Refactor loop at line {node.lineno} in {file} to reduce body size or split logic."
                            )
                    # Blocking calls in async code
                    if cfg.flag_blocking_in_async and isinstance(
                        node, ast.AsyncFunctionDef
                    ):
                        for sub in ast.walk(node):
                            # Detect time.sleep, requests, etc. as blocking
                            if isinstance(sub, ast.Call):
                                # time.sleep or similar (module.function)
                                if isinstance(sub.func, ast.Attribute):
                                    if (
                                        sub.func.attr == "sleep"
                                        and getattr(sub.func.value, "id", None)
                                        == "time"
                                    ):
                                        is_valid = False
                                        msg = f"{file}:{sub.lineno}: Blocking call 'time.sleep' in async function '{node.name}'"
                                        errors.append(msg)
                                        suggestions.append(
                                            f"Replace blocking call 'time.sleep' with async equivalent in '{node.name}'."
                                        )
                                # Direct calls (e.g., requests, open, etc.)
                                if isinstance(sub.func, ast.Name):
                                    if sub.func.id in {
                                        "requests",
                                        "subprocess",
                                        "os",
                                        "open",
                                    }:
                                        is_valid = False
                                        msg = f"{file}:{sub.lineno}: Blocking call '{sub.func.id}' in async function '{node.name}'"
                                        errors.append(msg)
                                        suggestions.append(
                                            f"Replace blocking call '{sub.func.id}' with async equivalent in '{node.name}'."
                                        )
                    # N+1 query pattern (simple heuristic: loop with DB call inside)
                    if cfg.flag_n_plus_one and isinstance(node, (ast.For, ast.While)):
                        for sub in ast.walk(node):
                            if isinstance(sub, ast.Call) and isinstance(
                                sub.func, ast.Attribute
                            ):
                                if sub.func.attr in {
                                    "execute",
                                    "fetchone",
                                    "fetchall",
                                    "get",
                                    "filter",
                                    "all",
                                }:
                                    is_valid = False
                                    msg = f"{file}:{sub.lineno}: Possible N+1 query pattern in loop at line {node.lineno} (calls '{sub.func.attr}')"
                                    errors.append(msg)
                                    suggestions.append(
                                        f"Consider refactoring loop at line {node.lineno} in {file} to batch DB/API calls."
                                    )
            except Exception as e:
                warnings.append(f"Could not parse {file}: {e}")
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            version=cfg.version,
        )

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for PerformanceAntipatternsValidator."
        )
