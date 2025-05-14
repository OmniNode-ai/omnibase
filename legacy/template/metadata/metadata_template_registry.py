# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "metadata_template_registry"
# namespace: "omninode.tools.metadata_template_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "metadata_template_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolRegistryTemplate"]
# base_class: ["ProtocolRegistryTemplate"]
# mock_safe: true
# === /OmniNode:Metadata ===

"""
MetadataRegistryTemplate implements ProtocolRegistryTemplate for template registration and lookup.
"""
from foundation.protocol.protocol_template_registry import ProtocolRegistryTemplate
from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA, EXTENDED_METADATA
from typing import Dict, List, Optional
from foundation.model.model_enum_template_type import TemplateTypeEnum

# Fully-commented template for Python files
FULLY_COMMENTED_PY_TEMPLATE = """\
# === OmniNode:Metadata ===
# metadata_version: "{metadata_version}"
# schema_version: "{schema_version}"
# name: "{name}"
# namespace: "omninode.tools.{name}"
# meta_type: "{meta_type}"
# version: "{version}"
# author: "{author}"
# owner: "{owner}"
# copyright: "{copyright}"
# created_at: "{created_at}"
# last_modified_at: "{last_modified_at}"
# entrypoint: "{entrypoint}"
# protocols_supported:
#   - "{protocols_supported}"
# protocol_class:
#   - '{protocol_class}'
# base_class:
#   - '{base_class}'
# mock_safe: {mock_safe}
# === /OmniNode:Metadata ===
"""

# Un-commented YAML template for YAML/Markdown files (reuse MINIMAL_METADATA)
YAML_TEMPLATE = MINIMAL_METADATA

class MetadataRegistryTemplate(ProtocolRegistryTemplate):
    """
    In-memory registry for metadata templates. Maps template types (Enum) and file extensions to template strings.
    Implements ProtocolRegistryTemplate for registration and lookup.
    """
    def __init__(self) -> None:
        self._templates: Dict[TemplateTypeEnum, str] = {}
        self._ext_map: Dict[str, list[TemplateTypeEnum]] = {}
        self.register_templates()

    def register_template(self, type_enum: TemplateTypeEnum, template: str, extensions: List[str]) -> None:
        """Register a template by Enum type and associate it with file extensions."""
        self._templates[type_enum] = template
        for ext in extensions:
            ext = ext.lower()
            if ext not in self._ext_map:
                self._ext_map[ext] = []
            if type_enum not in self._ext_map[ext]:
                self._ext_map[ext].append(type_enum)

    def get_template_for_extension(self, ext: str, type_enum: Optional[TemplateTypeEnum] = None) -> Optional[str]:
        """Return the template string for a given file extension and optional template type."""
        enums = self._ext_map.get(ext.lower(), [])
        if type_enum:
            if type_enum in enums:
                return self._templates.get(type_enum)
            return None
        # Default: return MINIMAL if available, else first
        if TemplateTypeEnum.MINIMAL in enums:
            return self._templates.get(TemplateTypeEnum.MINIMAL)
        if enums:
            return self._templates.get(enums[0])
        return None

    def get_template(self, type_enum: TemplateTypeEnum) -> Optional[str]:
        """Return the template string for a given template Enum type."""
        return self._templates.get(type_enum)

    def list_templates(self) -> List[TemplateTypeEnum]:
        """Return a list of all registered template Enum types."""
        return list(self._templates.keys())

    def list(self) -> List[TemplateTypeEnum]:
        """Return a list of all registered template Enum types (protocol compliance)."""
        return self.list_templates()

    def register_templates(self) -> None:
        """Register canonical templates for python, yaml, and markdown using Enum types."""
        self.register_template(
            TemplateTypeEnum.EXTENDED,
            FULLY_COMMENTED_PY_TEMPLATE,
            [".py"]
        )
        self.register_template(
            TemplateTypeEnum.MINIMAL,
            FULLY_COMMENTED_PY_TEMPLATE,
            [".py"]
        )
        self.register_template(
            TemplateTypeEnum.YAML,
            YAML_TEMPLATE,
            [".yaml", ".yml"]
        )
        self.register_template(
            TemplateTypeEnum.MARKDOWN,
            YAML_TEMPLATE,
            [".md"]
        )

    def get(self, type_enum: TemplateTypeEnum) -> Optional[str]:
        """Protocol compliance: Return the template string for a given template Enum type."""
        return self.get_template(type_enum)
