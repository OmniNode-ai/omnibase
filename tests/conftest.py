# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.848418'
# description: Stamped by PythonHandler
# entrypoint: python://conftest.py
# hash: a5fef4f650ef9dc2cd98496ace55409dbdbf8c7e15c2b9ca5c7c697e96701bdc
# last_modified_at: '2025-05-29T13:51:23.017621+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: conftest.py
# namespace: py://omnibase.tests.conftest_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e409b785-6ab7-49af-bcf9-b4acd826c0fd
# version: 1.0.0
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
