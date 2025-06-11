from enum import Enum

class NodeKafkaCommandEnum(str, Enum):
    """
    Canonical CLI command names for the kafka node.
    Extend this enum with all valid kafka node commands.
    """
    RUN = "run"
    BOOTSTRAP = "bootstrap"
    SEND = "send"
    CLEANUP = "cleanup"
    LIST_GROUPS = "list-groups"
    DELETE_GROUP = "delete-group"
    LIST_TOPICS = "list-topics"
    DELETE_TOPIC = "delete-topic"
    HEALTH_CHECK = "health-check"
    # Add more as needed 