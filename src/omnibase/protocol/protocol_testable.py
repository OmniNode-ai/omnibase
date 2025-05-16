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
