from enum import Enum

class NodeNameEnum(str, Enum):
    """
    Canonical node names for ONEX protocol and testing.
    Use this Enum for all protocol-facing node name references.
    """
    STAMPER_NODE = "stamper_node"
    TREE_GENERATOR_NODE = "tree_generator_node"
    REGISTRY_LOADER_NODE = "registry_loader_node"
    SCHEMA_GENERATOR_NODE = "schema_generator_node"
    TEMPLATE_NODE = "template_node" 