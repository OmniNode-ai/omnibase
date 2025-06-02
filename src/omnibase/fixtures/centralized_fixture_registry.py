"""
Centralized fixture registry for ONEX system.

This module provides an enhanced fixture registry that integrates with the
CentralizedFixtureLoader and supports both shared and node-local fixtures.
"""

from typing import Callable, List, Optional
from unittest import mock

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.fixtures.cli_stamp_fixtures import (
    CLIDirFixtureCase,
    FileEntryModel,
    SubdirEntryModel,
)
from omnibase.fixtures.fixture_loader import CentralizedFixtureLoader
from omnibase.model.model_fixture_data import FixtureDataModel
from omnibase.model.model_log_entry import LogContextModel
from omnibase.protocol.protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase
from omnibase.protocol.protocol_cli_dir_fixture_registry import (
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
            if hasattr(case, "id") and case.id == case_id:
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
                    fixture_data = self.fixture_loader.load_fixture(fixture_name)
                    cases = self._convert_fixture_to_cases(fixture_name, fixture_data)
                    self._cases_cache.extend(cases)
                except Exception as e:
                    emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        f"Warning: Could not load fixture '{fixture_name}': {e}",
                        context=LogContextModel(
                            calling_module=__name__,
                            calling_function="_load_cases",
                            calling_line=__import__("inspect").currentframe().f_lineno,
                            timestamp="auto",
                            node_id="centralized_fixture_registry",
                        ),
                        node_id="centralized_fixture_registry",
                        event_bus=self._event_bus,
                    )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Warning: Could not discover fixtures: {e}",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="_load_cases",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp="auto",
                    node_id="centralized_fixture_registry",
                ),
                node_id="centralized_fixture_registry",
                event_bus=self._event_bus,
            )
            self._cases_cache = []

    def _convert_fixture_to_cases(
        self, fixture_name: str, fixture_data: FixtureDataModel
    ) -> List[ProtocolCLIDirFixtureCase]:
        """
        Convert fixture data to ProtocolCLIDirFixtureCase instances.

        Args:
            fixture_name: Name of the fixture.
            fixture_data: Loaded fixture data (FixtureDataModel).

        Returns:
            List of fixture cases extracted from the data.
        """
        cases = []
        data = (
            fixture_data.data
            if isinstance(fixture_data, FixtureDataModel)
            else fixture_data
        )
        if isinstance(data, dict):
            if "test_cases" in data:
                for i, test_case in enumerate(data["test_cases"]):
                    case_id = test_case.get("id", f"{fixture_name}_{i}")
                    case = self._create_fixture_case(case_id, test_case, fixture_name)
                    cases.append(case)
            else:
                case_id = data.get("id", fixture_name)
                case = self._create_fixture_case(case_id, data, fixture_name)
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
            A ProtocolCLIDirFixtureCase instance (CLIDirFixtureCase).
        """
        # Always set fixture_name on the case
        case_data = dict(case_data)
        case_data.setdefault("fixture_name", fixture_name)
        files = [FileEntryModel(**f) for f in case_data.get("files", [])]
        subdirs = (
            [
                SubdirEntryModel(
                    subdir=s["subdir"],
                    files=[FileEntryModel(**ff) for ff in s["files"]],
                )
                for s in case_data.get("subdirs", [])
            ]
            if "subdirs" in case_data
            else None
        )
        case = CLIDirFixtureCase(id=case_id, files=files, subdirs=subdirs)
        # Attach input/expected_output if present for test compatibility
        if "input" in case_data:
            setattr(case, "input", case_data["input"])
        if "expected_output" in case_data:
            setattr(case, "expected_output", case_data["expected_output"])
        # Explicitly set fixture_name attribute
        case.fixture_name = fixture_name
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
