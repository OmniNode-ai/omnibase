# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: b4e3dda6-119c-4f45-a015-1f5ae1b2ee43
# name: model_block_placement_policy.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:05.852937
# last_modified_at: 2025-05-19T16:20:05.852938
# description: Stamped Python file: model_block_placement_policy.py
# state_contract: none
# lifecycle: active
# hash: 878801b0bf5da757fdb242977ffac66900f61f23beac5542d7a7ba150ea793fe
# entrypoint: {'type': 'python', 'target': 'model_block_placement_policy.py'}
# namespace: onex.stamped.model_block_placement_policy.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Optional

from pydantic import BaseModel, Field


class BlockPlacementPolicy(BaseModel):
    """
    Canonical policy for placement and normalization of ONEX metadata blocks in files.
    This model is the single source of truth for all block placement rules.
    """

    allow_shebang: bool = Field(
        True, description="Allow a shebang (#!...) at the very top of the file."
    )
    max_blank_lines_before_block: int = Field(
        1,
        description="Maximum blank lines allowed before the metadata block (after shebang, if present).",
    )
    allow_license_header: bool = Field(
        False, description="Allow a license header above the metadata block."
    )
    license_header_pattern: Optional[str] = Field(
        None, description="Regex pattern for allowed license header lines."
    )
    normalize_blank_lines: bool = Field(
        True, description="Normalize all blank lines above the block to at most one."
    )
    enforce_block_at_top: bool = Field(
        True,
        description="Enforce that the metadata block is at the top (after shebang/license header, if allowed).",
    )
    placement_policy_version: str = Field(
        "1.0.0", description="Version of the placement policy."
    )
