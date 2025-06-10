from enum import Enum

class TestKafkaCloneNodeArgEnum(str, Enum):
    """
    Node-specific CLI argument flags for the test_kafka_clone node.
    Extend this enum with all valid test_kafka_clone node-specific arguments.
    """
    EXAMPLE_ARG = "--example-arg"
    TEST_KAFKA_CLONE_ONLY = "--test_kafka_clone-only"
    # Add more as needed 