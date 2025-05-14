#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_performance"
# namespace: "omninode.tools.python_validate_performance"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "python_validate_performance.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate', 'ValidatorConfig']
# base_class: ['ProtocolValidate', 'ValidatorConfig']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_performance.py containers.foundation.src.foundation.script.validat
ion.validate_performance.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import logging
import re
from pathlib import Path
from typing import List

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.script.validate.common.common_file_utils import find_files



class PerformanceValidatorConfig(ValidatorConfig):
    version: str = "v1"
    # Add config fields as needed


class PerformanceValidator(ProtocolValidate):
    """Validates performance optimization practices."""

    def __init__(self, config=None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = PerformanceValidatorConfig(**(config or {}))
        self.logger = dependencies.get("logger") or logging.getLogger(__name__)

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="performance",
            group="quality",
            description="Validates performance optimization practices.",
            version="v1",
        )

    def get_name(self) -> str:
        """Get the validator name."""
        return "performance"

    def validate(
        self, target: Path, config: PerformanceValidatorConfig = None
    ) -> ValidationResult:
        """Validate performance practices.

        Args:
            target: Path to directory containing code

        Returns:
            ValidationResult: Result of the validation
        """
        # Clear previous messages
        self.errors.clear()
        self.warnings.clear()
        is_valid = True

        # Find Python files
        python_files = find_files(
            target,
            pattern="*.py",
            ignore_patterns=["**/__pycache__/**", "**/tests/**", "**/venv/**"],
        )

        if not python_files:
            self.errors.append(
                ValidationIssue(message="No Python files found", file=str(target))
            )
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                version=self.config.version,
            )

        # Validate each file
        for file in python_files:
            file_is_valid = True
            try:
                with open(file) as f:
                    content = f.read()

                # Parse AST for static analysis
                tree = ast.parse(content)

                # Validate database optimization
                file_is_valid &= self._validate_database_optimization(
                    tree, content, file
                )

                # Validate resource management
                file_is_valid &= self._validate_resource_management(tree, content, file)

                # Validate caching strategy
                file_is_valid &= self._validate_caching_strategy(tree, content, file)

                # Validate asynchronous processing
                file_is_valid &= self._validate_async_processing(tree, content, file)

                # Validate benchmarking
                file_is_valid &= self._validate_benchmarking(tree, content, file)

            except Exception as e:
                self.errors.append(
                    ValidationIssue(
                        message=f"Failed to analyze {file.name}: {e}", file=str(file)
                    )
                )
                file_is_valid = False
            # If any warnings were added for this file, fail validation for this file
            if len(self.warnings) > 0:
                file_is_valid = False
            is_valid &= file_is_valid

        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=self.config.version,
        )

    def _validate_database_optimization(
        self, tree: ast.AST, content: str, file: Path
    ) -> bool:
        """Validate database optimization practices."""
        is_valid = True

        # Check for proper connection pooling
        pool_config_required = {
            "pool_size": "Connection pool size not configured",
            "max_overflow": "Connection pool max overflow not configured",
            "pool_timeout": "Connection pool timeout not configured",
            "pool_recycle": "Connection pool recycle time not configured",
        }

        # Check for SQL anti-patterns
        sql_anti_patterns = [
            (r"SELECT \* FROM", "Avoid SELECT * queries"),
            (r"(?<!ORDER\s)BY\s+\d+", "Avoid positional ORDER BY"),
            (r"NOT\s+IN\s*\(\s*SELECT", "Avoid NOT IN with subqueries"),
        ]

        # Parse and analyze SQL queries in the code
        sql_queries = self._extract_sql_queries(content)
        for query in sql_queries:
            # Check for anti-patterns
            for pattern, message in sql_anti_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    self.errors.append(
                        ValidationIssue(
                            message=f"SQL anti-pattern detected: {message}",
                            file=str(file),
                            details={"query": query},
                        )
                    )
                    is_valid = False

            # Check for proper indexing hints
            if not self._has_indexing_hints(query):
                self.warnings.append(
                    ValidationIssue(
                        message="Consider adding indexing hints for better performance",
                        file=str(file),
                        details={"query": query},
                    )
                )

        # Check for proper pagination
        if self._has_pagination(tree):
            if not self._has_keyset_pagination(tree):
                self.warnings.append(
                    ValidationIssue(
                        message="Consider using keyset pagination for better performance",
                        file=str(file),
                    )
                )

        return is_valid

    def _validate_resource_management(
        self, tree: ast.AST, content: str, file: Path
    ) -> bool:
        """Validate resource management practices."""
        is_valid = True

        # Check for proper resource limits in container configs
        if "docker-compose.yml" in str(file) or "Dockerfile" in str(file):
            resource_limits = ["cpus", "memory", "pids_limit", "ulimits"]

            for limit in resource_limits:
                if limit not in content.lower():
                    self.warnings.append(
                        ValidationIssue(
                            message=f"Resource limit '{limit}' not configured",
                            file=str(file),
                        )
                    )

        # Check for resource cleanup
        for node in ast.walk(tree):
            # Check for proper file handling
            if isinstance(node, ast.With):
                continue
            # Check for proper connection handling
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"connect", "Connection"}:
                        # Can't check parent in AST without custom logic, so skip for now
                        self.errors.append(
                            ValidationIssue(
                                message=f"Use context managers for database connections in {file} (line {getattr(node, 'lineno', '?')})",
                                file=str(file),
                                line=getattr(node, "lineno", None),
                            )
                        )
                        is_valid = False

        return is_valid

    def _validate_caching_strategy(
        self, tree: ast.AST, content: str, file: Path
    ) -> bool:
        """Validate caching strategy implementation."""
        is_valid = True

        # Check for caching decorators
        cache_decorators = {"cached", "cache", "lru_cache", "ttl_cache"}

        # Check for Redis caching
        redis_caching_funcs = {"get", "set", "setex", "hget", "hset"}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function should be cached
                if self._should_be_cached(node):
                    has_cache = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            if decorator.id in cache_decorators:
                                has_cache = True
                                break

                    if not has_cache:
                        self.warnings.append(
                            ValidationIssue(
                                message="Consider caching this function",
                                file=str(file),
                                line=node.lineno,
                            )
                        )

        return is_valid

    def _validate_async_processing(
        self, tree: ast.AST, content: str, file: Path
    ) -> bool:
        """Validate asynchronous processing implementation."""
        is_valid = True
        has_async = False
        # Check for blocking operations in async functions
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                has_async = True
                blocking_calls = self._find_blocking_calls(node)
                for call in blocking_calls:
                    self.errors.append(
                        ValidationIssue(
                            message=f"Blocking operation '{call}' in async function",
                            file=str(file),
                            line=node.lineno,
                        )
                    )
                    is_valid = False
        # Only emit async pattern warnings if the file contains async code
        if has_async:
            async_patterns = {
                "asyncio.gather": "Concurrent execution",
                "asyncio.wait": "Parallel execution",
                "asyncio.create_task": "Task creation",
            }
            for pattern, purpose in async_patterns.items():
                if pattern not in content:
                    self.warnings.append(
                        ValidationIssue(
                            message=f"Consider using {pattern} for {purpose}",
                            file=str(file),
                        )
                    )
        return is_valid

    def _validate_benchmarking(self, tree: ast.AST, content: str, file: Path) -> bool:
        """Validate benchmarking practices."""
        is_valid = True
        # Only emit performance test warnings if the file is a test file and has at least one test function
        if "test" in str(file):
            has_test_func = any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("test_")
                for node in ast.walk(tree)
            )
            if has_test_func:
                perf_markers = {"@pytest.mark.benchmark", "@pytest.mark.performance"}
                has_perf_tests = any(marker in content for marker in perf_markers)
                if not has_perf_tests:
                    self.warnings.append(
                        ValidationIssue(
                            message="Consider adding performance tests", file=str(file)
                        )
                    )
        return is_valid

    def _extract_sql_queries(self, content: str) -> List[str]:
        """Extract SQL queries from code content."""
        queries = []
        # Find SQL strings (basic implementation)
        sql_patterns = [
            r"SELECT.*?FROM.*?(?:WHERE|GROUP BY|ORDER BY|LIMIT|$)",
            r"INSERT INTO.*?VALUES",
            r"UPDATE.*?SET.*?WHERE",
            r"DELETE FROM.*?WHERE",
        ]

        for pattern in sql_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            queries.extend(match.group(0) for match in matches)

        return queries

    def _has_indexing_hints(self, query: str) -> bool:
        """Check if SQL query includes indexing hints."""
        # Basic check for common indexing hints
        index_hints = ["USE INDEX", "FORCE INDEX", "IGNORE INDEX"]
        return any(hint in query.upper() for hint in index_hints)

    def _has_pagination(self, tree: ast.AST) -> bool:
        """Check if code implements pagination."""
        pagination_params = {"limit", "offset", "page", "per_page"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id in pagination_params:
                    return True
        return False

    def _has_keyset_pagination(self, tree: ast.AST) -> bool:
        """Check if code implements keyset pagination."""
        keyset_indicators = ["last_id", "cursor", "after", "before"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id in keyset_indicators:
                    return True
        return False

    def _should_be_cached(self, node: ast.FunctionDef) -> bool:
        """Determine if a function should be cached based on its
        characteristics."""
        # Flag functions with loops or with a body longer than 3 lines
        has_loop = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(node))
        if has_loop or len(node.body) > 3:
            return True
        # Check if function has database queries
        has_db_ops = False
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    if n.func.id in {"query", "execute", "fetchall", "fetchone"}:
                        has_db_ops = True
                        break
        return has_db_ops

    def _find_blocking_calls(self, node: ast.AsyncFunctionDef) -> List[str]:
        """Find blocking operations in async functions."""
        blocking_calls = []
        blocking_functions = {
            "sleep",
            "open",
            "read",
            "write",
            "requests.get",
            "requests.post",
            "subprocess.run",
        }

        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    if n.func.id in blocking_functions:
                        blocking_calls.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    call = f"{n.func.value.id}.{n.func.attr}"
                    if call in blocking_functions:
                        blocking_calls.append(call)

        return blocking_calls

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid