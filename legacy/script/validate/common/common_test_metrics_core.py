#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_test_metrics_core"
# namespace: "omninode.tools.common_test_metrics_core"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "common_test_metrics_core.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel', 'NodeVisitor', 'ValidationResult']
# base_class: ['BaseModel', 'NodeVisitor', 'ValidationResult']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import ast
import logging
from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field
from foundation.model.model_validate import ValidationIssue

@dataclass
class TestMetrics:
    test_count: int = 0
    assertion_count: int = 0
    async_test_count: int = 0
    parametrized_test_count: int = 0
    fixture_count: int = 0
    mock_count: int = 0
    docstring_coverage: float = 0.0

class ValidationResult(BaseModel):
    errors: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)
    is_valid: bool = True

    def add_error(
        self, error: str, file: str = None, line: int = None, details: dict = None
    ) -> None:
        self.errors.append(
            ValidationIssue(
                type="error", message=error, file=file, line=line, details=details
            )
        )
        self.is_valid = False

@dataclass
class TestQualityResult(ValidationResult):
    metrics: TestMetrics = field(default_factory=TestMetrics)

class CoverageResult(ValidationResult):
    total_coverage: float = 0.0
    unit_coverage: float = 0.0
    integration_coverage: float = 0.0
    e2e_coverage: float = 0.0
    uncovered_lines: dict = Field(default_factory=dict)
    success: bool = True

class TestCoverageValidationResult(ValidationResult):
    total_coverage: float = 0.0
    unit_coverage: float = 0.0
    integration_coverage: float = 0.0
    e2e_coverage: float = 0.0
    uncovered_lines: dict = Field(default_factory=dict)
    test_metrics: dict = Field(default_factory=dict)

class TestAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.test_count = 0
        self.assertion_count = 0
        self.parametrize_count = 0
        self.fixture_count = 0
        self.mock_count = 0
        self.async_test_count = 0
        self.docstring_count = 0

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            self.test_count += 1
            if node.decorator_list:
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "fixture":
                        self.fixture_count += 1
                    elif isinstance(decorator, ast.Attribute):
                        if decorator.attr == "fixture":
                            self.fixture_count += 1
                        elif decorator.attr == "parametrize":
                            self.parametrize_count += 1
                    elif isinstance(decorator, ast.Call):
                        if (
                            isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "pytest"
                        ):
                            if getattr(decorator.func, "attr", "") == "fixture":
                                self.fixture_count += 1
                            elif (
                                getattr(decorator.func, "attr", "")
                                == "mark.parametrize"
                            ):
                                self.parametrize_count += 1
                        elif isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr == "fixture":
                                self.fixture_count += 1
                            elif decorator.func.attr == "parametrize":
                                self.parametrize_count += 1
            if ast.get_docstring(node):
                self.docstring_count += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if node.name.startswith("test_"):
            self.async_test_count += 1
            if ast.get_docstring(node):
                self.docstring_count += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id.startswith("assert"):
                self.assertion_count += 1
            elif node.func.id in ["Mock", "MagicMock", "AsyncMock", "patch"]:
                self.mock_count += 1
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr.startswith("assert_"):
                self.assertion_count += 1
            elif node.func.attr in ["patch", "Mock", "MagicMock", "AsyncMock"]:
                self.mock_count += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.assertion_count += 1
        self.generic_visit(node)

def analyze_test_file(code: str) -> TestMetrics:
    metrics = TestMetrics()
    try:
        tree = ast.parse(code)
        analyzer = TestAnalyzer()
        analyzer.visit(tree)
        metrics.test_count = analyzer.test_count
        metrics.assertion_count = analyzer.assertion_count
        metrics.async_test_count = analyzer.async_test_count
        metrics.parametrized_test_count = analyzer.parametrize_count
        metrics.fixture_count = analyzer.fixture_count
        metrics.mock_count = analyzer.mock_count
        total_tests = metrics.test_count
        if total_tests > 0:
            metrics.docstring_coverage = (analyzer.docstring_count / total_tests) * 100
    except Exception as e:
        logging.getLogger(__name__).error(f"Error analyzing test file: {str(e)}")
    return metrics 