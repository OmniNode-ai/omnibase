from enum import Enum

class NodeKafkaArgEnum(str, Enum):
    """
    Node-specific CLI argument flags for the kafka node.
    Extend this enum with all valid kafka node-specific arguments.
    """
    KAFKA_CONFIG = "--kafka-config"
    EVENT_BUS = "--event-bus"
    # Add more as needed 