from enum import Enum

class TestKafkaCloneNodeCommandEnum(str, Enum):
    """
    Canonical CLI command names for the test_kafka_clone node.
    Extend this enum with all valid test_kafka_clone node commands.
    """
    RUN = "run"
    GENERATE = "generate"
    # Add more as needed 