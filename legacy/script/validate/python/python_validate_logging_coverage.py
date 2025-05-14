#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_logging_coverage
# namespace: omninode.tools.validate_logging_coverage
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:03+00:00
# last_modified_at: 2025-04-27T18:13:03+00:00
# entrypoint: validate_logging_coverage.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_logging_coverage.py containers.foundation.src.foundation.script.va
lidation.validate_logging_coverage.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationIssue, ValidationResult
from pydantic import BaseModel


class LoggingCoverageValidatorConfig(BaseModel):
    min_ratio: float = 2.0  # Default: at least 2 logs per function
    max_ratio: Optional[float] = None  # Optional: max logs per function
    required_levels: List[str] = [
        "info",
        "warning",
        "error",
    ]  # Require these levels per file/class
    allow_debug_in_prod: bool = False
    enforce_structured: bool = True
    enforce_canonical_logger: bool = True
    require_context_id: bool = True
    environment: str = "prod"  # dev, prod, test, debug
    log_spam_threshold: int = 10  # Warn if >N logs at same level in a function
    test_code_strictness: str = "standard"  # standard, strict, relaxed
    exclude_dirs: List[str] = ["__pycache__", ".venv", ".git", "build", "dist"]
    overrides: Dict[str, Any] = {}  # Per-module/dir overrides
    # TODO: Add more config as needed


    name="logging_coverage",
    version="v2",
    group="standards",
    description="Comprehensive logging coverage enforcement.",
)
class LoggingCoverageValidator(ProtocolValidate):
    def __init__(self, config: dict = None, **dependencies):
        # Accept config as either a dict or a LoggingCoverageValidatorConfig instance.
        # Always pass a dict to ProtocolValidate (for .get()), always set self.pydantic_config to a LoggingCoverageValidatorConfig instance.
        # All internal logic should use self.pydantic_config for type safety.
        if isinstance(config, LoggingCoverageValidatorConfig):
            self.pydantic_config = config
            config_dict = (
                config.model_dump() if hasattr(config, "model_dump") else config.dict()
            )
        else:
            self.pydantic_config = LoggingCoverageValidatorConfig(**(config or {}))
            config_dict = (
                self.pydantic_config.model_dump()
                if hasattr(self.pydantic_config, "model_dump")
                else self.pydantic_config.dict()
            )
        super().__init__(config_dict, **dependencies)
        self.config = (
            self.pydantic_config
        )  # For backward compatibility, but use self.pydantic_config in this class.

    def validate(self, target, config: dict = None) -> ValidationResult:
        """Validate comprehensive logging coverage in the target directory.

        Returns a ValidationResult object.
        """
        target = Path(target) if not isinstance(target, Path) else target
        errors = []
        warnings = []
        suggestions = []
        cfg = self.config
        # --- Environment-aware profile application ---
        env = getattr(cfg, "environment", "prod")
        fields_set = getattr(cfg, "model_fields_set", set())
        env_profiles = {
            "prod": {
                "min_ratio": 2.0,
                "required_levels": ["info", "warning", "error"],
                "allow_debug_in_prod": False,
                "enforce_structured": True,
                "enforce_canonical_logger": True,
                "require_context_id": True,
            },
            "dev": {
                "min_ratio": 1.0,
                "required_levels": ["info", "warning"],
                "allow_debug_in_prod": True,
                "enforce_structured": False,
                "enforce_canonical_logger": False,
                "require_context_id": False,
            },
            "test": {
                "min_ratio": 0.5,
                "required_levels": ["info"],
                "allow_debug_in_prod": True,
                "enforce_structured": False,
                "enforce_canonical_logger": False,
                "require_context_id": False,
            },
            "debug": {
                "min_ratio": 1.0,
                "required_levels": ["debug", "info", "warning", "error"],
                "allow_debug_in_prod": True,
                "enforce_structured": False,
                "enforce_canonical_logger": False,
                "require_context_id": False,
            },
        }
        profile = env_profiles.get(env, env_profiles["dev"])
        for k, v in profile.items():
            if k in fields_set:
                continue
            setattr(cfg, k, v)
        min_ratio = cfg.min_ratio
        required_levels = cfg.required_levels
        allow_debug = cfg.allow_debug_in_prod
        for file_path in target.rglob("*.py"):
            if any(ex in file_path.parts for ex in cfg.exclude_dirs):
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
                num_functions = 0
                num_logging = 0
                level_counts = {
                    level: 0
                    for level in ["debug", "info", "warning", "error", "critical"]
                }
                trivial_functions = 0

                def is_trivial_function(node):
                    if not isinstance(node, ast.FunctionDef):
                        return False
                    body = node.body
                    if len(body) == 0:
                        return True
                    if len(body) == 1 and isinstance(
                        body[0], (ast.Return, ast.Pass, ast.Raise)
                    ):
                        return True
                    return False

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if is_trivial_function(node):
                            trivial_functions += 1
                        else:
                            num_functions += 1
                    elif isinstance(node, ast.Call):
                        func = node.func
                        if isinstance(func, ast.Attribute):
                            attr = func.attr
                            if attr in level_counts:
                                level_counts[attr] += 1
                                num_logging += 1
                if num_functions > 0:
                    ratio = num_logging / num_functions
                    if ratio < min_ratio:
                        errors.append(
                            ValidationIssue(
                                message=f"File {file_path} has insufficient logging: {num_logging} logging statements for {num_functions} non-trivial functions (ratio {ratio:.2f}, required {min_ratio})",
                                file=str(file_path),
                                type="error",
                            )
                        )
                    if cfg.max_ratio is not None and ratio > cfg.max_ratio:
                        warnings.append(
                            ValidationIssue(
                                message=f"File {file_path} may have excessive logging: {num_logging} logging statements for {num_functions} non-trivial functions (ratio {ratio:.2f}, max allowed {cfg.max_ratio})",
                                file=str(file_path),
                                type="warning",
                            )
                        )
                    missing_levels = [
                        level
                        for level in required_levels
                        if level_counts.get(level, 0) == 0
                        and (level != "debug" or allow_debug)
                    ]
                    if missing_levels:
                        errors.append(
                            ValidationIssue(
                                message=f"File {file_path} does not contain required log levels: {', '.join(missing_levels)} (required by config/environment)",
                                file=str(file_path),
                                type="error",
                            )
                        )
                structured_logging_found = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func = node.func
                        if isinstance(func, ast.Attribute):
                            for kw in getattr(node, "keywords", []):
                                if kw.arg == "extra":
                                    structured_logging_found = True
                                if kw.arg not in ("exc_info", "stack_info", "extra"):
                                    structured_logging_found = True
                if (
                    cfg.enforce_structured
                    and num_functions > 0
                    and not structured_logging_found
                ):
                    errors.append(
                        ValidationIssue(
                            message=f"File {file_path} does not use structured/contextual logging (required by config)",
                            file=str(file_path),
                            type="error",
                        )
                    )
                if cfg.enforce_canonical_logger:
                    found_non_canonical = False
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            func = node.func
                            if isinstance(func, ast.Attribute):
                                if (
                                    getattr(func.value, "id", None) == "logging"
                                    and func.attr == "getLogger"
                                ) or (
                                    getattr(func.value, "id", None) == "logging"
                                    and func.attr
                                    in ["info", "debug", "warning", "error", "critical"]
                                ):
                                    found_non_canonical = True
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name == "logging":
                                    found_non_canonical = True
                    if found_non_canonical:
                        errors.append(
                            ValidationIssue(
                                message=f"File {file_path} uses non-canonical logger (raw 'logging' or 'logging.getLogger'). Use 'foundation.logging.get_logger' or DI-provided logger.",
                                file=str(file_path),
                                type="error",
                            )
                        )
                if cfg.require_context_id and num_functions > 0:
                    found_context_id = False
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            for kw in getattr(node, "keywords", []):
                                if kw.arg == "extra" and isinstance(kw.value, ast.Dict):
                                    for k in kw.value.keys:
                                        if isinstance(k, ast.Constant) and k.value in (
                                            "correlation_id",
                                            "context_id",
                                        ):
                                            found_context_id = True
                                if kw.arg in ("correlation_id", "context_id"):
                                    found_context_id = True
                    if not found_context_id:
                        errors.append(
                            ValidationIssue(
                                message=f"File {file_path} does not include a correlation_id or context_id in any log statement (required by config)",
                                file=str(file_path),
                                type="error",
                            )
                        )
            except Exception as e:
                warnings.append(
                    ValidationIssue(
                        message=f"Could not parse {file_path}: {e}",
                        file=str(file_path),
                        type="warning",
                    )
                )
        return ValidationResult(
            is_valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata=None,
            version=None,
        )

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for LoggingCoverageValidator."
        )

    @classmethod
    def metadata(cls):
        return {
            "name": "logging_coverage",
            "group": "standards",
            "description": "Comprehensive logging coverage enforcement.",
            "version": "v2",
        }

    def get_name(self) -> str:
        return "logging_coverage"
