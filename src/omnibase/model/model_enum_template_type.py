from enum import Enum


class TemplateTypeEnum(str, Enum):
    """
    Canonical template types for metadata stamping and registry.
    """

    MINIMAL: str = "minimal"
    EXTENDED: str = "extended"
    YAML: str = "yaml"
    MARKDOWN: str = "markdown"
