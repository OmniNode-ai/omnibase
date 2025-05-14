#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_test_metrics_quality"
# namespace: "omninode.tools.common_test_metrics_quality"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "common_test_metrics_quality.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from pathlib import Path
from typing import Dict, List, Optional
from foundation.model.model_validate import ValidationIssue
from .common_test_metrics_core import analyze_test_file

def validate_test_quality(
    container_path: Path, config: Optional[Dict] = None
) -> List[ValidationIssue]:
    errors = []
    if config is None:
        config = {}
    tests_path = container_path / "tests"
    if not tests_path.exists():
        return [
            ValidationIssue(
                type="error",
                message="Missing tests directory",
                file=str(container_path),
            )
        ]
    min_test_count = config.get("min_test_count", 1)
    min_assertions = config.get("min_assertions_per_test", 1)
    for test_file in tests_path.rglob("test_*.py"):
        metrics = analyze_test_file(test_file.read_text())
        if metrics:
            if metrics.test_count < min_test_count:
                errors.append(
                    ValidationIssue(
                        type="error",
                        message=f"{test_file}: Too few tests in file",
                        file=str(test_file),
                    )
                )
            if metrics.assertion_count < min_assertions:
                errors.append(
                    ValidationIssue(
                        type="error",
                        message=f"{test_file}: Too few assertions per test",
                        file=str(test_file),
                    )
                )
            if metrics.coverage < 0.8:
                errors.append(
                    ValidationIssue(
                        type="error",
                        message=f"{test_file}: Test coverage below 80%",
                        file=str(test_file),
                    )
                )
    return errors 