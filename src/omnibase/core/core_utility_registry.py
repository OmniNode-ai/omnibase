# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "utility_registry"
# namespace: "omninode.tools.utility_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "utility_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===



"""
UtilityRegistry implements BaseRegistry for DI/registry-compliant utility injection.
"""
from foundation.util.util_chunk_metrics import UtilChunkMetrics
from foundation.registry.base_registry import BaseRegistry
from foundation.util.util_header import UtilHeader

# Remove global singleton instance and registration logic
# All instantiation and registration must be handled via DI/bootstrap 

# DI-compliant registry for utility classes
UTILITY_REGISTRY = BaseRegistry()
UTILITY_REGISTRY.register('header', UtilHeader())

def get_util(name: str):
    """DI-compliant accessor for registered utilities."""
    return UTILITY_REGISTRY.get(name) 