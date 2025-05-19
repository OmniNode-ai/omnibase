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
