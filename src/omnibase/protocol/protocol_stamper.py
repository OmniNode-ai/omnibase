
# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_stamper"
# namespace: "omninode.tools.protocol_stamper"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "protocol_stamper.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Metadata ===





from typing import Protocol
from pathlib import Path

class ProtocolStamper(Protocol):
    """
    Protocol for metadata stamping tools. All stampers must implement this interface for DI and orchestration.
    """
    def stamp_file(
        self,
        path: Path,
        template: str = "minimal",
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs,
    ) -> bool:
        """
        Stamp the file with a metadata block, replacing any existing block.
        :return: True if file was written, False if dry run.
        """
        ... 