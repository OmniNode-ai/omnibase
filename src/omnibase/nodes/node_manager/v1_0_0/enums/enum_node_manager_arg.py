from enum import Enum

class NodeManagerArgEnum(str, Enum):
    """
    Node-specific CLI argument flags for node_manager.
    Extend this enum with all valid node_manager-specific arguments.
    """
    GENERATE_ARTIFACT = "--generate-artifact"
    CUSTOM_CONFIG = "--custom-config"
    # Add more as needed 