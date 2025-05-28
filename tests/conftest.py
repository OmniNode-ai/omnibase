# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: conftest.py
# version: 1.0.0
# uuid: e409b785-6ab7-49af-bcf9-b4acd826c0fd
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.848418
# last_modified_at: 2025-05-28T17:20:05.290765
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 38a07aaf70d99ad909f3ef02a4dbb1264363f650ab07729846371037de1320a5
# entrypoint: python@conftest.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.conftest
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test Configuration for Centralized Tests

This conftest.py file imports and re-exports fixtures from the main
src/omnibase/conftest.py to make them available to tests in the centralized
tests/ directory.

This follows the ONEX testing standards defined in docs/testing.md.
"""

# Re-export specific fixtures that are commonly used
# Import all fixtures from the main conftest.py
from omnibase.conftest import *  # noqa: F403, F401
from omnibase.conftest import registry, registry_loader_context  # noqa: F401
