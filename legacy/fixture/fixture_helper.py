# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_fixture_helper"
# namespace: "omninode.tools.test_fixture_helper"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:24+00:00"
# last_modified_at: "2025-05-05T13:00:24+00:00"
# entrypoint: "test_fixture_helper.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ITestHelper']
# base_class: ['ITestHelper']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Test helpers for OmniNode validator error/warning assertions.
"""
from typing import List, Optional

from foundation.model.model_validate import ValidationIssue
from foundation.script.validate.validate_registry import register_fixture


class TestHelper:
    """Concrete implementation for validator error/warning assertions."""

    def assert_has_error(
        self, errors: List[ValidationIssue], substring: str, file: Optional[str] = None
    ) -> None:
        for err in errors:
            if substring.lower() in err.message.lower() and (
                file is None or err.file == file
            ):
                return
        raise AssertionError(
            f"No error found with substring '{substring}' and file '{file}' in: {[e.message for e in errors]}"
        )

    def assert_has_warning(
        self,
        warnings: List[ValidationIssue],
        substring: str,
        file: Optional[str] = None,
    ) -> None:
        for warn in warnings:
            if substring.lower() in warn.message.lower() and (
                file is None or warn.file == file
            ):
                return
        raise AssertionError(
            f"No warning found with substring '{substring}' and file '{file}' in: {[w.message for w in warnings]}"
        )

    def assert_issue_fields(
        self, issue: ValidationIssue, required_fields: Optional[List[str]] = None
    ) -> None:
        required = required_fields or ["message", "file", "type"]
        for field in required:
            if not getattr(issue, field, None):
                raise AssertionError(f"ValidationIssue missing required field: {field}")

# Register TestHelper in the fixture registry
register_fixture(
    name="test_helper",
    fixture=TestHelper,
    description="Test helper for validator error/warning assertions",
    interface=TestHelper,
)