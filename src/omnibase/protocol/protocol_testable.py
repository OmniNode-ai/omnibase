# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_testable.py
# version: 1.0.0
# uuid: 0562818d-653d-4c07-84ec-4f12e6c11b47
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167762
# last_modified_at: 2025-05-21T16:42:46.093434
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: bafe4cd2e35750f0363a08d3338834fe2104f5601e2c9e235ca3f1047743f8a2
# entrypoint: python@protocol_testable.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_testable
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ProtocolTestable: Base protocol for all testable ONEX components.
This is a marker protocol for testable objects (registries, CLIs, tools, etc.).
Extend this for specific testable interfaces as needed.
"""

from typing import Protocol


class ProtocolTestable(Protocol):
    """
    Marker protocol for testable ONEX components.
    Extend for specific testable interfaces.
    """

    pass
