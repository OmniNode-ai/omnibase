"""
Canonical Metadata Block Normalizer for ONEX (Stamper Node)
- Extracts, normalizes, and emits metadata blocks for any filetype.
- Filetype-aware: emits correct delimiters, omits YAML markers for non-YAML files.
- Canonicalizes all fields, omits empty/None, enforces protocol invariants.
- Exposes: normalize_metadata_block(content: str, filetype: str, meta: Optional[NodeMetadataBlock] = None) -> str
- Uses NodeMetadataBlock and canonical serializer for all logic.
- This is the canonical normalizer for all stamping operations in the stamper node.
"""
from typing import Optional
import re
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.metadata.metadata_constants import MD_META_OPEN, MD_META_CLOSE
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer

# Filetype to delimiter mapping
DELIMITERS = {
    "markdown": (MD_META_OPEN, MD_META_CLOSE),
    "md": (MD_META_OPEN, MD_META_CLOSE),
    "python": ("# === OmniNode:Metadata ===", "# === /OmniNode:Metadata ==="),
    "py": ("# === OmniNode:Metadata ===", "# === /OmniNode:Metadata ==="),
    "yaml": ("---", "..."),
    "yml": ("---", "..."),
}

def normalize_metadata_block(content: str, filetype: str, meta: Optional[NodeMetadataBlock] = None) -> str:
    """
    Normalize and emit a protocol-compliant metadata block for the given filetype.
    - Removes any existing block (legacy or malformed).
    - Emits a fresh, canonical block with correct delimiters and field formatting.
    - If meta is not provided, attempts to extract and parse from content.
    """
    # 1. Remove any existing block (legacy or malformed)
    open_delim, close_delim = DELIMITERS.get(filetype, (MD_META_OPEN, MD_META_CLOSE))
    block_pattern = rf"{re.escape(open_delim)}[\s\S]+?{re.escape(close_delim)}\n*"
    content_no_block = re.sub(block_pattern, "", content, flags=re.MULTILINE)
    # 2. If meta not provided, try to extract and parse
    if meta is None:
        block_match = re.search(rf"{re.escape(open_delim)}\n(.*?)(?:\n)?{re.escape(close_delim)}", content, re.DOTALL)
        if block_match:
            import yaml
            try:
                meta_dict = yaml.safe_load(block_match.group(1))
                meta = NodeMetadataBlock.model_validate(meta_dict)
            except Exception:
                meta = None
    if meta is None:
        raise ValueError("No valid metadata block found or provided.")
    # 3. Canonicalize and emit block
    serializer = CanonicalYAMLSerializer()
    yaml_block = serializer.canonicalize_metadata_block(meta, comment_prefix="" if filetype in ("yaml", "yml") else None)
    # Remove YAML document markers for non-YAML files
    if filetype not in ("yaml", "yml"):
        yaml_block = re.sub(r"^(---|\.\.\.)\s*\n?", "", yaml_block, flags=re.MULTILINE)
        yaml_block = re.sub(r"\n(---|\.\.\.)\s*$", "", yaml_block, flags=re.MULTILINE)
    # For YAML, ensure only a single '...' at the end of the block
    if filetype in ("yaml", "yml"):
        yaml_block = yaml_block.rstrip()
        if yaml_block.endswith("..."):
            block = f"{open_delim}\n{yaml_block}\n"
        else:
            block = f"{open_delim}\n{yaml_block}\n{close_delim}"
    else:
        block = f"{open_delim}\n{yaml_block}\n{close_delim}"
    # Normalize spacing: exactly one blank line after the block if content follows
    rest = content_no_block.lstrip("\n")
    if rest:
        stamped = block + "\n" + rest
    else:
        stamped = block + "\n"
    return stamped

# Stub for test coverage (to be expanded)
def test_normalize_metadata_block_stub():
    """Stub test for normalizer (expand with real cases)."""
    pass 