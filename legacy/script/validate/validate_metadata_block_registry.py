# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "validate_metadata_block_registry"
# namespace: "omninode.tools.validate_metadata_block_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T22:11:58+00:00"
# last_modified_at: "2025-05-05T22:11:58+00:00"
# entrypoint: "validate_metadata_block_registry.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '[]'
# base_class:
#   - '[]'
# mock_safe: true
# === /OmniNode:Metadata ===









"""
Registry for mapping file extensions to metadata block validator classes.
"""
from typing import Dict, Type
from foundation.script.validate.python.python_validate_metadata_block import PythonValidateMetadataBlock
from foundation.script.validate.yaml.yaml_validate_metadata_block import YamlValidateMetadataBlock
from foundation.script.validate.markdown.markdown_validate_metadata_block import MarkdownValidateMetadataBlock
from foundation.model.model_metadata import MetadataBlockModel

class MetadataValidateBlockRegistry:
    def __init__(self):
        self._registry: Dict[str, Type] = {}
        self.register('.py', PythonValidateMetadataBlock)
        self.register('.yaml', YamlValidateMetadataBlock)
        self.register('.yml', YamlValidateMetadataBlock)
        self.register('.md', MarkdownValidateMetadataBlock)
        self.register('.tree', YamlValidateMetadataBlock)

    def register(self, ext: str, validator_cls: Type):
        self._registry[ext] = validator_cls

    def get_validator(self, ext: str):
        return self._registry.get(ext)

    def list_extensions(self):
        return list(self._registry.keys())

# All instantiation and registration must be handled via DI/bootstrap 