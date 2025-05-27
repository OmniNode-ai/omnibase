# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: centralized_fixture_registry.py
# version: 1.0.0
# uuid: d0bfa84f-fb51-4847-8ecd-32970fc199da
# author: OmniNode Team
# created_at: 2025-05-25T13:17:23.930943
# last_modified_at: 2025-05-25T17:18:14.235050
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5dde0607f156919a5df67a0320f7a32188a1f1122587ebbe84c0882d8d8cc8f2
# entrypoint: python@centralized_fixture_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.centralized_fixture_registry
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Centralized fixture registry for ONEX system.

This module provides an enhanced fixture registry that integrates with the
CentralizedFixtureLoader and supports both shared and node-local fixtures.
"""

from typing import Callable, List, Optional
from unittest import mock

import pytest

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.core.structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.fixtures.fixture_loader import CentralizedFixtureLoader
from omnibase.fixtures.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase
from omnibase.fixtures.protocol_cli_dir_fixture_registry import (
    ProtocolCLIDirFixtureRegistry,
)


class CentralizedFixtureRegistry(ProtocolCLIDirFixtureRegistry):
    """
    Enhanced fixture registry that supports centralized fixture management.

    This registry integrates with the CentralizedFixtureLoader to provide
    access to both shared and node-local fixtures through a unified interface.
    """

    def __init__(self, fixture_loader: Optional[CentralizedFixtureLoader] = None):
        """
        Initialize the centralized fixture registry.

        Args:
            fixture_loader: Optional fixture loader instance. If not provided,
                          a default loader will be created.
        """
        self.fixture_loader = fixture_loader or CentralizedFixtureLoader()
        self._cases_cache: Optional[List[ProtocolCLIDirFixtureCase]] = None

    def all_cases(self) -> List[ProtocolCLIDirFixtureCase]:
        """
        Get all available fixture cases.

        Returns:
            List of all fixture cases from both shared and node-local sources.
        """
        if self._cases_cache is None:
            self._load_cases()
        return self._cases_cache or []

    def get_case(self, case_id: str) -> ProtocolCLIDirFixtureCase:
        """
        Get a specific fixture case by ID.

        Args:
            case_id: The ID of the fixture case to retrieve.

        Returns:
            The fixture case with the specified ID.

        Raises:
            KeyError: If no case with the specified ID is found.
        """
        cases = self.all_cases()
        for case in cases:
            # Check if the case has a case_id attribute before accessing it
            if hasattr(case, "case_id") and case.case_id == case_id:
                return case
        raise OnexError(
            f"Fixture case '{case_id}' not found", CoreErrorCode.RESOURCE_NOT_FOUND
        )

    def filter_cases(
        self, predicate: Callable[[ProtocolCLIDirFixtureCase], bool]
    ) -> List[ProtocolCLIDirFixtureCase]:
        """
        Filter fixture cases using a predicate function.

        Args:
            predicate: Function that takes a fixture case and returns True
                      if the case should be included in the results.

        Returns:
            List of fixture cases that match the predicate.
        """
        return [case for case in self.all_cases() if predicate(case)]

    def _load_cases(self) -> None:
        """Load all fixture cases from the fixture loader."""
        self._cases_cache = []

        try:
            fixtures = self.fixture_loader.discover_fixtures()

            for fixture_name in fixtures:
                try:
                    # Load the fixture data
                    fixture_data = self.fixture_loader.load_fixture(fixture_name)

                    # Convert fixture data to test cases
                    cases = self._convert_fixture_to_cases(fixture_name, fixture_data)
                    self._cases_cache.extend(cases)

                except Exception as e:
                    # Log warning but continue processing other fixtures
                    emit_log_event(
                        LogLevelEnum.WARNING,
                        f"Warning: Could not load fixture '{fixture_name}': {e}",
                        node_id="centralized_fixture_registry",
                    )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Warning: Could not discover fixtures: {e}",
                node_id="centralized_fixture_registry",
            )
            self._cases_cache = []

    def _convert_fixture_to_cases(
        self, fixture_name: str, fixture_data: dict
    ) -> List[ProtocolCLIDirFixtureCase]:
        """
        Convert fixture data to ProtocolCLIDirFixtureCase instances.

        Args:
            fixture_name: Name of the fixture.
            fixture_data: Loaded fixture data.

        Returns:
            List of fixture cases extracted from the data.
        """
        cases = []

        # Handle different fixture data formats
        if isinstance(fixture_data, dict):
            if "test_cases" in fixture_data:
                # Standard test case format
                for i, test_case in enumerate(fixture_data["test_cases"]):
                    case_id = test_case.get("id", f"{fixture_name}_{i}")
                    case = self._create_fixture_case(case_id, test_case, fixture_name)
                    cases.append(case)
            else:
                # Single test case format
                case_id = fixture_data.get("id", fixture_name)
                case = self._create_fixture_case(case_id, fixture_data, fixture_name)
                cases.append(case)

        return cases

    def _create_fixture_case(
        self, case_id: str, case_data: dict, fixture_name: str
    ) -> ProtocolCLIDirFixtureCase:
        """
        Create a ProtocolCLIDirFixtureCase from case data.

        Args:
            case_id: ID for the test case.
            case_data: Test case data.
            fixture_name: Name of the source fixture.

        Returns:
            A ProtocolCLIDirFixtureCase instance.
        """
        # Create a mock fixture case with the required attributes
        # In a real implementation, this would create an actual instance
        case = mock.MagicMock(spec=ProtocolCLIDirFixtureCase)
        case.case_id = case_id
        case.fixture_name = fixture_name
        case.data = case_data

        # Add common attributes that might be expected
        case.input = case_data.get("input", {})
        case.expected_output = case_data.get("expected_output", {})
        case.description = case_data.get(
            "description", f"Test case from {fixture_name}"
        )

        return case

    def refresh_cache(self) -> None:
        """Refresh the fixture cases cache by reloading from the fixture loader."""
        self._cases_cache = None
        self.fixture_loader._discover_all_fixtures()

    def get_fixtures_by_source(
        self, source_pattern: str
    ) -> List[ProtocolCLIDirFixtureCase]:
        """
        Get fixture cases from a specific source pattern.

        Args:
            source_pattern: Pattern to match against fixture sources
                          (e.g., "central", "node:stamper_node").

        Returns:
            List of fixture cases from matching sources.
        """
        return self.filter_cases(
            lambda case: hasattr(case, "fixture_name")
            and source_pattern in case.fixture_name
        )


@pytest.fixture
def centralized_fixture_registry() -> CentralizedFixtureRegistry:
    """Pytest fixture for the centralized fixture registry."""
    return CentralizedFixtureRegistry()


@pytest.fixture
def cli_fixture_registry() -> ProtocolCLIDirFixtureRegistry:
    """
    Enhanced CLI fixture registry that uses centralized fixture management.

    This fixture provides backward compatibility while enabling access to
    both shared and node-local fixtures.
    """
    return CentralizedFixtureRegistry()
