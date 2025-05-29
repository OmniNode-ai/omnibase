# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.883679'
# description: Stamped by PythonHandler
# entrypoint: python://model_block_placement_policy.py
# hash: 2e8f380f9d87dcd3ba6dee17f69cca077b98699cfd493d4b4ff6f7258fc1a48f
# last_modified_at: '2025-05-29T11:50:10.919607+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_block_placement_policy.py
# namespace: omnibase.model_block_placement_policy
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 3cc55211-330d-4b36-a981-a7d958d08261
# version: 1.0.0
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
