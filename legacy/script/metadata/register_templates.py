#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "register_templates"
# namespace: "omninode.tools.register_templates"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T10:56:45+00:00"
# last_modified_at: "2025-05-07T10:56:45+00:00"
# entrypoint: "register_templates.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Register metadata templates in the registry.
"""

from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA, EXTENDED_METADATA
from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.util.util_file_output_writer import OutputWriter
import structlog
from foundation.model.model_enum_template_type import TemplateTypeEnum

def register_templates(registry: MetadataRegistryTemplate, output_writer: OutputWriter):
    """Register all metadata templates."""
    # Register Python template (uses MINIMAL_METADATA with Python comment style)
    registry.register_template(
        TemplateTypeEnum.MINIMAL,
        MINIMAL_METADATA.replace("metadata_version:", "# metadata_version:"),
        [".py"]
    )

    # Register YAML template
    registry.register_template(
        TemplateTypeEnum.MINIMAL,
        MINIMAL_METADATA,
        [".yaml", ".yml"]
    )

    # Register Markdown template (uses YAML format)
    registry.register_template(
        TemplateTypeEnum.MINIMAL,
        MINIMAL_METADATA,
        [".md"]
    )

def main(logger: ProtocolLogger, output_writer: OutputWriter) -> None:
    """Register all templates."""
    registry = MetadataRegistryTemplate()
    register_templates(registry, output_writer)
    logger.info("Templates registered successfully.")

class TestLogger:
    def info(self, msg: str, *args, **kwargs) -> None:
        print(f"INFO: {msg}")
    def warning(self, msg: str, *args, **kwargs) -> None:
        print(f"WARNING: {msg}")
    def error(self, msg: str, *args, **kwargs) -> None:
        print(f"ERROR: {msg}")
    def debug(self, msg: str, *args, **kwargs) -> None:
        print(f"DEBUG: {msg}")

if __name__ == "__main__":
    logger = structlog.get_logger("register_templates")
    output_writer = OutputWriter()
    main(logger, output_writer) 