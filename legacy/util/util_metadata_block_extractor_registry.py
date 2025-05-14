# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "util_metadata_block_extractor_registry"
# namespace: "omninode.tools.util_metadata_block_extractor_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T22:11:58+00:00"
# last_modified_at: "2025-05-05T22:11:58+00:00"
# entrypoint: "util_metadata_block_extractor_registry.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '[]'
# base_class:
#   - '[]'
# mock_safe: true
# === /OmniNode:Metadata ===



from foundation.util.util_metadata_block_extractor import MetadataBlockExtractor
from foundation.const.metadata_tags import OMNINODE_METADATA_START, OMNINODE_METADATA_END

# Registry mapping language/file type to extractor
_METADATA_BLOCK_EXTRACTOR_REGISTRY = {
    'python': MetadataBlockExtractor(fr"^# {OMNINODE_METADATA_START}", fr"^# {OMNINODE_METADATA_END}", line_prefix="# "),
    'yaml': MetadataBlockExtractor(fr"^(#\s*)?{OMNINODE_METADATA_START}", fr"^(#\s*)?{OMNINODE_METADATA_END}"),
    'markdown': MetadataBlockExtractor(fr"^(#\s*)?{OMNINODE_METADATA_START}", fr"^(#\s*)?{OMNINODE_METADATA_END}"),
    'tree': MetadataBlockExtractor(fr"^(#\s*)?{OMNINODE_METADATA_START}", fr"^(#\s*)?{OMNINODE_METADATA_END}"),
}

def get_extractor(language: str):
    return _METADATA_BLOCK_EXTRACTOR_REGISTRY.get(language) 