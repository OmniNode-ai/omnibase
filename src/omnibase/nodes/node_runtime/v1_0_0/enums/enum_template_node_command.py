from enum import Enum

class TemplateNodeCommandEnum(str, Enum):
    """
    Canonical CLI command names for the template node.
    Extend this enum with all valid template node commands.
    """
    RUN = "run"
    GENERATE = "generate"
    # Add more as needed 