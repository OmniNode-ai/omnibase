# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: conftest.py
# version: 1.0.0
# uuid: 8d3cea83-536d-4afd-9483-ff8c3800e019
# author: OmniNode Team
# created_at: 2025-05-27T12:46:03.651209
# last_modified_at: 2025-05-27T16:48:17.268185
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8a9af5a23f9d31c2a7cf1003897ffac91ce2b53acea7259f15d04c84b1e48c9f
# entrypoint: python@conftest.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.conftest
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
