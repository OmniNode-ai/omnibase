# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# schema_version: 1.0.0
# name: __init__
# namespace: omninode.tools.__init__
# meta_type: model
# version: 0.1.0
# author: OmniNode Team
# owner: jonah@omninode.ai
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-05-02T18:46:08+00:00
# last_modified_at: 2025-05-02T18:46:08+00:00
# entrypoint: __init__.py
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from .metadata_stamper import *
from .metadata_block_utils import *

# Alias for standards-compliant import
metadata_stamper = __import__(
    "foundation.script.metadata.metadata_stamper", fromlist=["metadata_stamper"]
)