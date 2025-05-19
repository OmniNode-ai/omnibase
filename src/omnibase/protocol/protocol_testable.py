# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 6d180091-fff7-481a-a163-11e5e06155f9
# name: protocol_testable.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:02.429353
# last_modified_at: 2025-05-19T16:20:02.429359
# description: Stamped Python file: protocol_testable.py
# state_contract: none
# lifecycle: active
# hash: ba58d3d6b322e0ffd68bdb366331879470792a712e8cb443735dc5d3685373b5
# entrypoint: {'type': 'python', 'target': 'protocol_testable.py'}
# namespace: onex.stamped.protocol_testable.py
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
