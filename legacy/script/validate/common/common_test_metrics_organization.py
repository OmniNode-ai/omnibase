#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_test_metrics_organization"
# namespace: "omninode.tools.common_test_metrics_organization"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "common_test_metrics_organization.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from pathlib import Path
from typing import Dict, List, Optional
from foundation.model.model_validate import ValidationIssue
from .common_test_metrics_core import analyze_test_file

DEFAULT_TEST_DIRS = ["unit", "integration", "e2e"]
DEFAULT_TEST_FILE_PATTERNS = ["test_*.py", "*_test.py"]
DEFAULT_COVERAGE_THRESHOLDS = {"total": 80}

def validate_test_organization(
    container_path: Path, config: Optional[Dict] = None
) -> List[ValidationIssue]:
    errors = []
    if config is None:
        config = {}
    test_dirs = config.get("test_dirs", DEFAULT_TEST_DIRS)
    test_patterns = config.get("test_patterns", DEFAULT_TEST_FILE_PATTERNS)
    tests_path = container_path / "tests"
    if not tests_path.exists():
        return [
            ValidationIssue(
                type="error",
                message="Missing tests directory",
                file=str(container_path),
            )
        ]
    for test_dir in test_dirs:
        dir_path = tests_path / test_dir
        if not dir_path.exists():
            errors.append(
                ValidationIssue(
                    type="error",
                    message=f"Missing test directory: tests/{test_dir}",
                    file=str(dir_path),
                )
            )
        else:
            has_tests = False
            for pattern in test_patterns:
                if list(dir_path.glob(pattern)):
                    has_tests = True
                    break
            if not has_tests:
                errors.append(
                    ValidationIssue(
                        type="error",
                        message=f"No test files found in tests/{test_dir}",
                        file=str(dir_path),
                    )
                )
    if not (tests_path / "conftest.py").exists():
        errors.append(
            ValidationIssue(
                type="error",
                message="Missing conftest.py in tests directory",
                file=str(tests_path),
            )
        )
    min_assertions = config.get("min_assertions_per_test", 1)
    require_parameterized = config.get("require_parameterized_tests", True)
    for test_file in tests_path.rglob("test_*.py"):
        metrics = analyze_test_file(test_file.read_text())
        if metrics:
            if metrics.assertion_count < min_assertions:
                errors.append(
                    ValidationIssue(
                        type="error",
                        message=f"{test_file}: Too few assertions per test",
                        file=str(test_file),
                    )
                )
            if (
                require_parameterized
                and metrics.test_count > 0
                and metrics.parametrized_test_count == 0
            ):
                errors.append(
                    ValidationIssue(
                        type="error",
                        message=f"{test_file}: No parameterized tests found",
                        file=str(test_file),
                    )
                )
    return errors 