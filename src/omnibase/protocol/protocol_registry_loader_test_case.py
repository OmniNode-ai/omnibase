# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_registry_loader_test_case.py
# version: 1.0.0
# uuid: 405b795b-e807-4a54-8a22-1f9a2f3eff1a
# author: OmniNode Team
# created_at: 2025-05-24T14:45:30.081979
# last_modified_at: 2025-05-24T18:52:54.045711
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 968ce13334ba5eff78ba0767777ba25f8aaf1727721de9cbd63a60292f5e0a82
# entrypoint: python@protocol_registry_loader_test_case.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_registry_loader_test_case
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Protocol interface for registry loader test cases.
"""

from typing import Protocol

from omnibase.model.enum_onex_status import OnexStatus


class ProtocolRegistryLoaderTestCase(Protocol):
    """Protocol for registry loader test cases."""

    id: str
    expected_status: OnexStatus
    description: str
