from enum import Enum


class NodeNameEnum(str, Enum):
    """
    Canonical node names for ONEX protocol and testing.
    Use this Enum for all protocol-facing node name references.
    """

    STAMPER_NODE = "stamper_node"
    TREE_GENERATOR_NODE = "node_tree_generator"
    REGISTRY_LOADER_NODE = "registry_loader_node"
    SCHEMA_GENERATOR_NODE = "schema_generator_node"
    NODE_TEMPLATE = "node_template"
    NODE_KAFKA_EVENT_BUS = "node_kafka_event_bus"
    NODE_MANAGER = "node_manager"
