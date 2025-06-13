from enum import Enum

class TemplateNodeArgEnum(str, Enum):
    """
    Node-specific CLI argument flags for the template node.
    Extend this enum with all valid template node-specific arguments.
    """
    EXAMPLE_ARG = "--example-arg"
    TEMPLATE_ONLY = "--template-only"
    # Add more as needed 