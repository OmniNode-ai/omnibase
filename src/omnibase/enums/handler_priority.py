from enum import Enum

class HandlerPriorityEnum(int, Enum):
    """
    Canonical priority levels for file type handlers in ONEX/OmniBase.
    Used for registry, plugin, and protocol compliance.
    """
    CORE = 100
    RUNTIME = 50
    NODE_LOCAL = 10
    PLUGIN = 0
    CUSTOM = 25 