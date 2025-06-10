from enum import Enum

class NodeManagerCommandEnum(str, Enum):
    """
    Canonical CLI command names for node_manager node.
    Extend this enum with all valid node_manager commands.
    """
    GENERATE = "generate"
    VALIDATE = "validate"
    INTROSPECT = "introspect"
    # Add more as needed 