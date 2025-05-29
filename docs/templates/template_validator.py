# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:07.624471'
# description: Stamped by PythonHandler
# entrypoint: python://template_validator.py
# hash: 06650e494dce9eb6026ec6d9b039d5e76f0d5198c963355a9548fa60e36346bb
# last_modified_at: '2025-05-29T13:51:13.713213+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: template_validator.py
# namespace: py://omnibase.docs.templates.template_validator_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 93e95ddc-1ec3-455f-a381-6ff5a1f4321f
# version: 1.0.0
# === /OmniNode:Metadata ===


from abc import ABC, abstractmethod
from typing import Any, List, Optional, Protocol


class ValidationResult(Protocol):
    is_valid: bool
    errors: Optional[List[Any]]


class Validatable(Protocol):
    def validate(self, path: str) -> ValidationResult: ...


class PythonTestProtocolValidate(ABC):
    """
    Canonical base class for all Python validator/tool test classes.
    Enforces standard structure for agent-driven automation, snapshotting, and meta-validation.
    Requires get_tool() to return a Validatable or processable object.
    """

    @abstractmethod
    def get_tool(self) -> Any:
        """
        Must return an object with a `validate(path: str)` or `process(path: str)` method
        that returns an object with: `is_valid: bool`, `errors: Optional[List[Any]]`.
        """
        ...

    def _run(self, tool: Any, path: str) -> Any:
        if hasattr(tool, "validate"):
            return tool.validate(path)
        elif hasattr(tool, "process"):
            return tool.process(path)
        raise NotImplementedError("Tool must have validate() or process() method.")

    def run_valid_case(self, case_path: str) -> Any:
        """Run the validator/tool on a valid test case and return the result."""
        tool = self.get_tool()
        return self._run(tool, case_path)

    def run_invalid_case(self, case_path: str) -> Any:
        """Run the validator/tool on an invalid test case and return the result."""
        tool = self.get_tool()
        return self._run(tool, case_path)

    def assert_valid(self, result: Any) -> None:
        assert getattr(result, "is_valid", False), "Expected result to be valid."

    def assert_invalid(self, result: Any) -> None:
        assert not getattr(result, "is_valid", True), "Expected result to be invalid."

    def assert_failure_contains(self, result: Any, expected: str) -> None:
        """Assert that the result contains the expected failure message."""
        assert any(
            expected in (getattr(e, "message", str(e)))
            for e in getattr(result, "errors", [])
        ), f"Expected '{expected}' in errors."

    def log_result(self, result: Any, case_path: str) -> None:
        """Optional agent logging hook."""
        print(f"[LOG] Case: {case_path} | Valid: {getattr(result, 'is_valid', '?')}")

    def assert_snapshot(self, result: Any, snapshot_path: str) -> None:
        """Optional: Assert that the result matches a stored snapshot (stub for agent use)."""
        # Implement snapshot comparison logic here
        pass

    def meta_validate(self, result: Any) -> None:
        """Optional: Perform meta-validation on the result (stub for agent use)."""
        # Implement meta-validation logic here
        pass

    # Optional: Add snapshot or meta-validation hooks here for future agent use.
