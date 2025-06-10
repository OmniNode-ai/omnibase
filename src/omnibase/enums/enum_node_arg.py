from enum import Enum

class NodeArgEnum(str, Enum):
    """
    Canonical CLI argument flags for ONEX nodes.
    """
    BOOTSTRAP = "--bootstrap"
    HEALTH_CHECK = "--health-check"
    INTROSPECT = "--introspect" 