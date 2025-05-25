# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_fixture_loader.py
# version: 1.0.0
# uuid: 22ef10fd-abc4-4af7-b37c-4d6b2dc6e92f
# author: OmniNode Team
# created_at: 2025-05-25T13:14:40.667588
# last_modified_at: 2025-05-25T17:18:14.229442
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: dd2004a3fbecec149a5ecc8fc4bec8cb09a1dac32b3fa8905f901a37be65d21f
# entrypoint: python@protocol_fixture_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_fixture_loader
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
            ValueError: If the fixture cannot be loaded or parsed.
        """
        ...
