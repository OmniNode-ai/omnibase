# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_block_placement_policy.py
# version: 1.0.0
# uuid: b1ceeb93-98c1-43ee-b40e-65c7940cae3a
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164773
# last_modified_at: 2025-05-21T16:42:46.078889
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: fae749217b8a95616e49de1a64ff9c0599d4da119d22fb3341a3520bd52acaba
# entrypoint: {'type': 'python', 'target': 'model_block_placement_policy.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_block_placement_policy
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
