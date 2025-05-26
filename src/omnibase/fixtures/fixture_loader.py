# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: fixture_loader.py
# version: 1.0.0
# uuid: 5f9516d2-02c5-4cda-be6b-ff4d50bf5391
# author: OmniNode Team
# created_at: 2025-05-25T13:15:06.406337
# last_modified_at: 2025-05-25T17:18:14.232923
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: af1b6c3abb79d48b67aaf3237ffef0cea65e772332673d3ac0e4086b4a05344d
# entrypoint: python@fixture_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.fixture_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Concrete implementation of fixture loader for ONEX system.

This module provides a concrete implementation of the FixtureLoaderProtocol
that can discover and load fixtures from both central and node-local directories.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.protocol.protocol_fixture_loader import ProtocolFixtureLoader


class CentralizedFixtureLoader(ProtocolFixtureLoader):
    """
    Centralized fixture loader that supports both central and node-local fixtures.

    This loader can discover and load fixtures from:
    - Central fixtures: tests/fixtures/
    - Central data: tests/data/
    - Node-local fixtures: src/omnibase/nodes/*/v1_0_0/node_tests/fixtures/
    """

    def __init__(
        self,
        central_fixtures_dir: Optional[Path] = None,
        central_data_dir: Optional[Path] = None,
        include_node_local: bool = True,
    ):
        """
        Initialize the fixture loader.

        Args:
            central_fixtures_dir: Path to central fixtures directory.
            central_data_dir: Path to central data directory.
            include_node_local: Whether to include node-local fixtures.
        """
        self.central_fixtures_dir = central_fixtures_dir or Path("tests/fixtures")
        self.central_data_dir = central_data_dir or Path("tests/data")
        self.include_node_local = include_node_local
        self._fixture_cache: Dict[str, Path] = {}
        self._discover_all_fixtures()

    def _discover_all_fixtures(self) -> None:
        """Discover all available fixtures and cache their paths."""
        self._fixture_cache.clear()

        # Discover central fixtures
        self._discover_fixtures_in_directory(self.central_fixtures_dir, "central")
        self._discover_fixtures_in_directory(self.central_data_dir, "central_data")

        # Discover node-local fixtures if enabled
        if self.include_node_local:
            self._discover_node_local_fixtures()

    def _discover_fixtures_in_directory(self, directory: Path, prefix: str) -> None:
        """
        Discover fixtures in a specific directory.

        Args:
            directory: Directory to search for fixtures.
            prefix: Prefix to add to fixture names for namespacing.
        """
        if not directory.exists():
            return

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".yaml", ".yml", ".json"]:
                # Create a namespaced fixture name
                relative_path = file_path.relative_to(directory)
                fixture_name = f"{prefix}:{relative_path.as_posix()}"
                self._fixture_cache[fixture_name] = file_path

    def _discover_node_local_fixtures(self) -> None:
        """Discover node-local fixtures."""
        nodes_dir = Path("src/omnibase/nodes")
        if not nodes_dir.exists():
            return

        for node_dir in nodes_dir.iterdir():
            if not node_dir.is_dir():
                continue

            # Look for versioned node directories
            for version_dir in node_dir.iterdir():
                if not version_dir.is_dir() or not version_dir.name.startswith("v"):
                    continue

                fixtures_dir = version_dir / "node_tests" / "fixtures"
                if fixtures_dir.exists():
                    self._discover_fixtures_in_directory(
                        fixtures_dir, f"node:{node_dir.name}"
                    )

    def discover_fixtures(self) -> List[str]:
        """
        Return a list of available fixture names.

        Returns:
            List of fixture names that can be loaded by this loader.
        """
        return list(self._fixture_cache.keys())

    def load_fixture(self, name: str) -> Any:
        """
        Load and return the fixture by name.

        Args:
            name: The name of the fixture to load.

        Returns:
            The loaded fixture object.

        Raises:
            OnexError: If the fixture is not found or cannot be loaded.
        """
        if name not in self._fixture_cache:
            raise OnexError(f"Fixture '{name}' not found", CoreErrorCode.FILE_NOT_FOUND)

        file_path = self._fixture_cache[name]

        try:
            if file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    return json.load(f)
            elif file_path.suffix in [".yaml", ".yml"]:
                with open(file_path, "r") as f:
                    return yaml.safe_load(f)
            else:
                raise OnexError(
                    f"Unsupported fixture format: {file_path.suffix}",
                    CoreErrorCode.INVALID_PARAMETER,
                )
        except Exception as e:
            raise OnexError(
                f"Failed to load fixture '{name}': {e}", CoreErrorCode.OPERATION_FAILED
            ) from e

    def get_fixture_path(self, name: str) -> Path:
        """
        Get the file path for a fixture.

        Args:
            name: The name of the fixture.

        Returns:
            Path to the fixture file.

        Raises:
            OnexError: If the fixture is not found.
        """
        if name not in self._fixture_cache:
            raise OnexError(f"Fixture '{name}' not found", CoreErrorCode.FILE_NOT_FOUND)
        return self._fixture_cache[name]

    def filter_fixtures(self, pattern: str) -> List[str]:
        """
        Filter fixtures by name pattern.

        Args:
            pattern: Pattern to match against fixture names.

        Returns:
            List of fixture names matching the pattern.
        """
        import fnmatch

        return [
            name
            for name in self._fixture_cache.keys()
            if fnmatch.fnmatch(name, pattern)
        ]
