from enum import Enum

class NodeKafkaCommandEnum(str, Enum):
    """
    Canonical CLI command names for the kafka node.
    Extend this enum with all valid kafka node commands.
    """
    RUN = "run"
    BOOTSTRAP = "bootstrap"
    SEND = "send"
    # Add more as needed 