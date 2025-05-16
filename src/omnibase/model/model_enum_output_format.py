from enum import Enum


class OutputFormatEnum(str, Enum):
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"
