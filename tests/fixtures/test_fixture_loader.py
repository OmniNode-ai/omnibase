# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_fixture_loader.py
# version: 1.0.0
# uuid: 5a07098d-1d18-45dd-8688-8bcf1e8d6e06
# author: OmniNode Team
# created_at: 2025-05-25T13:15:47.708286
# last_modified_at: 2025-05-25T17:35:42.327902
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 468abbbf5e24be4f0395ecfc207e1944217cc4867ba2a07ce71cc93c7ba59114
# entrypoint: python@test_fixture_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_fixture_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for the centralized fixture loader.

This module tests the CentralizedFixtureLoader implementation to ensure
it can properly discover and load fixtures from both central and node-local
directories.
"""

from pathlib import Path

import pytest

from omnibase.core.error_codes import OnexError
from omnibase.fixtures.fixture_loader import CentralizedFixtureLoader


class TestCentralizedFixtureLoader:
    """Test suite for CentralizedFixtureLoader."""

    def test_fixture_loader_initialization(self) -> None:
        """Test that fixture loader initializes correctly."""
        loader = CentralizedFixtureLoader()
        assert loader.central_fixtures_dir == Path("tests/fixtures")
        assert loader.central_data_dir == Path("tests/data")
        assert loader.include_node_local is True

    def test_discover_fixtures(self) -> None:
        """Test that fixture discovery works correctly."""
        loader = CentralizedFixtureLoader()
        fixtures = loader.discover_fixtures()

        # Should find at least our test data file
        assert isinstance(fixtures, list)
        # Look for our test data file
        test_data_fixtures = [f for f in fixtures if "shared_test_data_basic.yaml" in f]
        assert len(test_data_fixtures) > 0

    def test_load_fixture(self) -> None:
        """Test that fixture loading works correctly."""
        loader = CentralizedFixtureLoader()
        fixtures = loader.discover_fixtures()

        # Find our test data file
        test_data_fixtures = [f for f in fixtures if "shared_test_data_basic.yaml" in f]
        if test_data_fixtures:
            fixture_name = test_data_fixtures[0]
            data = loader.load_fixture(fixture_name)

            # Verify the loaded data structure
            assert isinstance(data, dict)
            assert "test_cases" in data
            assert "metadata" in data
            assert len(data["test_cases"]) == 2

    def test_load_nonexistent_fixture(self) -> None:
        """Test that loading a nonexistent fixture raises OnexError."""
        loader = CentralizedFixtureLoader()

        with pytest.raises(OnexError, match="Fixture 'nonexistent' not found"):
            loader.load_fixture("nonexistent")

    def test_get_fixture_path(self) -> None:
        """Test that getting fixture path works correctly."""
        loader = CentralizedFixtureLoader()
        fixtures = loader.discover_fixtures()

        # Find our test data file
        test_data_fixtures = [f for f in fixtures if "shared_test_data_basic.yaml" in f]
        if test_data_fixtures:
            fixture_name = test_data_fixtures[0]
            path = loader.get_fixture_path(fixture_name)

            assert isinstance(path, Path)
            assert path.exists()
            assert path.name == "shared_test_data_basic.yaml"

    def test_filter_fixtures(self) -> None:
        """Test that fixture filtering works correctly."""
        loader = CentralizedFixtureLoader()

        # Filter for YAML files
        yaml_fixtures = loader.filter_fixtures("*yaml*")
        assert isinstance(yaml_fixtures, list)

        # All results should contain 'yaml'
        for fixture in yaml_fixtures:
            assert "yaml" in fixture.lower()

    def test_node_local_fixture_discovery(self) -> None:
        """Test that node-local fixtures are discovered when enabled."""
        loader = CentralizedFixtureLoader(include_node_local=True)
        fixtures = loader.discover_fixtures()

        # Should find node-local fixtures if they exist
        node_fixtures = [f for f in fixtures if f.startswith("node:")]
        # We know stamper_node has fixtures
        stamper_fixtures = [f for f in node_fixtures if "stamper_node" in f]
        assert len(stamper_fixtures) > 0

    def test_node_local_fixture_exclusion(self) -> None:
        """Test that node-local fixtures are excluded when disabled."""
        loader = CentralizedFixtureLoader(include_node_local=False)
        fixtures = loader.discover_fixtures()

        # Should not find any node-local fixtures
        node_fixtures = [f for f in fixtures if f.startswith("node:")]
        assert len(node_fixtures) == 0
