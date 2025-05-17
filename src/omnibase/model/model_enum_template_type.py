from enum import Enum


class TemplateTypeEnum(str, Enum):
    """
    Canonical template types for metadata stamping and registry.
    """

    MINIMAL = "minimal"
    EXTENDED = "extended"
    YAML = "yaml"
    MARKDOWN = "markdown"
