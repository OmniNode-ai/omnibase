# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_fixture_loader.py
# version: 1.0.0
# uuid: 25f39f39-7b34-472f-8741-9b7a05cdd32f
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.191573
# last_modified_at: 2025-05-28T17:20:04.963158
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e73a203556e9c0d52f20bfe199b2c02bb4977acdb648099d1492f5a77a804599
# entrypoint: python@protocol_fixture_loader.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_fixture_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Protocol for fixture loading and discovery.

This module defines the minimal interface for fixture loaders that can
discover and load test fixtures from various sources (central, node-local).
"""

from typing import Any, List, Protocol


class ProtocolFixtureLoader(Protocol):
    """
    Protocol for fixture loading and discovery.

    This minimal interface supports fixture discovery and loading for both
    central and node-scoped fixture directories, enabling extensibility
    and plugin scenarios.
    """

    def discover_fixtures(self) -> List[str]:
        """
        Return a list of available fixture names.

        Returns:
            List of fixture names that can be loaded by this loader.
        """
        ...

    def load_fixture(self, name: str) -> Any:
        """
        Load and return the fixture by name.

        Args:
            name: The name of the fixture to load.

        Returns:
            The loaded fixture object.

        Raises:
            FileNotFoundError: If the fixture is not found.
            OnexError: If the fixture cannot be loaded or parsed.
        """
        ...
