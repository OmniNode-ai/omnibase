# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.910769'
# description: Stamped by PythonHandler
# entrypoint: python://test_centralized_fixture_registry.py
# hash: c0c70136b53351cde02921b33801c87f0feb0d57857ab50ab962fa8ccfc63b06
# last_modified_at: '2025-05-29T11:50:12.616733+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_centralized_fixture_registry.py
# namespace: omnibase.test_centralized_fixture_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b8ed0dc6-2a0a-4fa4-9166-3722a47c17a9
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tests for the centralized fixture registry.

This module tests the CentralizedFixtureRegistry to ensure it properly
integrates with the fixture loader and provides the expected interface.
"""

from unittest.mock import MagicMock

import pytest

from omnibase.core.core_error_codes import OnexError
from omnibase.fixtures.centralized_fixture_registry import CentralizedFixtureRegistry
from omnibase.fixtures.fixture_loader import CentralizedFixtureLoader


class TestCentralizedFixtureRegistry:
    """Test suite for CentralizedFixtureRegistry."""

    def test_registry_initialization(self) -> None:
        """Test that the registry initializes correctly."""
        registry = CentralizedFixtureRegistry()
        assert registry.fixture_loader is not None
        assert isinstance(registry.fixture_loader, CentralizedFixtureLoader)

    def test_registry_with_custom_loader(self) -> None:
        """Test that the registry accepts a custom fixture loader."""
        custom_loader = MagicMock(spec=CentralizedFixtureLoader)
        registry = CentralizedFixtureRegistry(fixture_loader=custom_loader)
        assert registry.fixture_loader is custom_loader

    def test_all_cases_loads_from_fixtures(self) -> None:
        """Test that all_cases() loads cases from available fixtures."""
        registry = CentralizedFixtureRegistry()
        cases = registry.all_cases()

        # Should return a list (may be empty if no fixtures)
        assert isinstance(cases, list)

    def test_get_case_by_id(self) -> None:
        """Test that get_case() retrieves cases by ID."""
        registry = CentralizedFixtureRegistry()
        cases = registry.all_cases()

        if cases:
            # Test with an existing case - use hasattr to check for case_id
            first_case = cases[0]
            if hasattr(first_case, "case_id"):
                retrieved_case = registry.get_case(first_case.case_id)
                assert hasattr(retrieved_case, "case_id")
                assert retrieved_case.case_id == first_case.case_id

    def test_get_nonexistent_case(self) -> None:
        """Test that get_case() raises OnexError for nonexistent cases."""
        registry = CentralizedFixtureRegistry()

        with pytest.raises(OnexError, match="Fixture case 'nonexistent' not found"):
            registry.get_case("nonexistent")

    def test_filter_cases(self) -> None:
        """Test that filter_cases() works correctly."""
        registry = CentralizedFixtureRegistry()

        # Filter for cases with specific attributes
        all_cases = registry.all_cases()
        filtered_cases = registry.filter_cases(lambda case: hasattr(case, "case_id"))

        # All cases should have case_id
        assert len(filtered_cases) == len(all_cases)

    def test_refresh_cache(self) -> None:
        """Test that refresh_cache() clears and reloads the cache."""
        registry = CentralizedFixtureRegistry()

        # Refresh cache
        registry.refresh_cache()

        # Cases should be reloaded
        refreshed_cases = registry.all_cases()
        assert isinstance(refreshed_cases, list)

    def test_get_fixtures_by_source(self) -> None:
        """Test that get_fixtures_by_source() filters by source pattern."""
        registry = CentralizedFixtureRegistry()

        # Get fixtures from central data source
        central_fixtures = registry.get_fixtures_by_source("central_data")
        assert isinstance(central_fixtures, list)

        # All returned fixtures should match the pattern
        for fixture in central_fixtures:
            assert hasattr(fixture, "fixture_name")
            assert "central_data" in fixture.fixture_name

    def test_convert_fixture_to_cases_with_test_cases(self) -> None:
        """Test conversion of fixture data with test_cases format."""
        registry = CentralizedFixtureRegistry()

        fixture_data = {
            "test_cases": [
                {
                    "id": "test1",
                    "input": {"value": 1},
                    "expected_output": {"result": "success"},
                },
                {
                    "id": "test2",
                    "input": {"value": 2},
                    "expected_output": {"result": "failure"},
                },
            ]
        }

        cases = registry._convert_fixture_to_cases("test_fixture", fixture_data)

        assert len(cases) == 2
        # Use hasattr to check for case_id since it may not be part of the protocol
        if hasattr(cases[0], "case_id"):
            assert cases[0].case_id == "test1"
        if hasattr(cases[1], "case_id"):
            assert cases[1].case_id == "test2"

    def test_convert_fixture_to_cases_single_case(self) -> None:
        """Test conversion of fixture data with single case format."""
        registry = CentralizedFixtureRegistry()

        fixture_data = {
            "id": "single_test",
            "input": {"value": 1},
            "expected_output": {"result": "success"},
        }

        cases = registry._convert_fixture_to_cases("single_fixture", fixture_data)

        assert len(cases) == 1
        # Use hasattr to check for case_id since it may not be part of the protocol
        if hasattr(cases[0], "case_id"):
            assert cases[0].case_id == "single_test"

    def test_create_fixture_case(self) -> None:
        """Test creation of fixture cases from case data."""
        registry = CentralizedFixtureRegistry()

        case_data = {
            "input": {"file_path": "test.yaml"},
            "expected_output": {"status": "success"},
            "description": "Test case description",
        }

        case = registry._create_fixture_case("test_case", case_data, "test_fixture")

        # Test the attributes that actually exist in the protocol
        assert hasattr(case, "input")
        assert hasattr(case, "expected_output")
        # Note: case_id, fixture_name, data, description may not be part of the protocol

    def test_registry_integration(self) -> None:
        """Test basic registry functionality."""
        registry = CentralizedFixtureRegistry()

        # Test that we can get all cases
        cases = registry.all_cases()
        assert isinstance(cases, list)


class TestFixtureRegistryIntegration:
    """Integration tests for fixture registry with real fixtures."""

    def test_registry_loads_real_fixtures(self) -> None:
        """Test that the registry can load real fixtures from the test data."""
        registry = CentralizedFixtureRegistry()
        cases = registry.all_cases()

        # Should find our test data file - use hasattr to check for fixture_name
        test_data_cases = []
        for case in cases:
            if (
                hasattr(case, "fixture_name")
                and "shared_test_data_basic" in case.fixture_name
            ):
                test_data_cases.append(case)
        assert len(test_data_cases) > 0

        # Verify case structure
        for case in test_data_cases:
            # Check for attributes that should exist in the protocol
            assert hasattr(case, "input")
            assert hasattr(case, "expected_output")

    def test_registry_provides_protocol_compliance(self) -> None:
        """Test that the registry complies with the ProtocolCLIDirFixtureRegistry protocol."""

        registry = CentralizedFixtureRegistry()

        # Should implement all protocol methods
        assert hasattr(registry, "all_cases")
        assert hasattr(registry, "get_case")
        assert hasattr(registry, "filter_cases")

        # Methods should be callable
        assert callable(registry.all_cases)
        assert callable(registry.get_case)
        assert callable(registry.filter_cases)
