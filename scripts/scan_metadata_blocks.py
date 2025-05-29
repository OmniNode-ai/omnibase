# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-29T05:49:49.012423'
# description: Stamped by PythonHandler
# entrypoint: python://scan_metadata_blocks.py
# hash: 3c7a2b2f9a60ead62fbd61b426c2ca62369b4e81e2ee5d8c3c8f0a8106f26dfc
# last_modified_at: '2025-05-29T13:43:06.625581+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: scan_metadata_blocks.py
# namespace:
#   value: py://omnibase.scan_metadata_blocks_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: d16264a9-fcb1-4f27-aad6-0990a70a03d3
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
import os
import re
import sys
import yaml
from pathlib import Path

# Canonical version values (update as needed)
CANONICAL_METADATA_VERSION = "0.1.0"
CANONICAL_PROTOCOL_VERSION = "1.1.0"
CANONICAL_SCHEMA_VERSION = "1.1.0"
PROTOCOL_REQUIRED_FIELDS = {"tools"}

META_OPEN = "=== OmniNode:Metadata ==="
META_CLOSE = "=== /OmniNode:Metadata ==="

VIOLATIONS = []


def find_metadata_blocks(text):
    pattern = re.compile(
        rf"^#? ?{re.escape(META_OPEN)}.*?^#? ?{re.escape(META_CLOSE)}",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.findall(text)


def parse_metadata_block(block):
    # Remove comment prefixes
    lines = [re.sub(r"^# ?", "", l) for l in block.splitlines()]
    # Remove delimiters
    lines = [l for l in lines if l.strip() not in (META_OPEN, META_CLOSE)]
    yaml_str = "\n".join(lines)
    try:
        return yaml.safe_load(yaml_str)
    except Exception as e:
        return None


def scan_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    blocks = find_metadata_blocks(text)
    for block in blocks:
        meta = parse_metadata_block(block)
        if not meta:
            VIOLATIONS.append((str(path), None, None, None, "YAML parse error"))
            continue
        # Check for empty/null/empty-string fields
        for k, v in meta.items():
            if (
                (v == "" or v is None or v == {} or v == [])
                and k not in PROTOCOL_REQUIRED_FIELDS
            ):
                VIOLATIONS.append((str(path), k, v, type(v).__name__, "Empty/null/empty-string field"))
        # Check version fields
        if meta.get("metadata_version") != CANONICAL_METADATA_VERSION:
            VIOLATIONS.append((str(path), "metadata_version", meta.get("metadata_version"), type(meta.get("metadata_version")), f"Non-canonical metadata_version (expected {CANONICAL_METADATA_VERSION})"))
        if meta.get("protocol_version") != CANONICAL_PROTOCOL_VERSION:
            VIOLATIONS.append((str(path), "protocol_version", meta.get("protocol_version"), type(meta.get("protocol_version")), f"Non-canonical protocol_version (expected {CANONICAL_PROTOCOL_VERSION})"))
        if meta.get("schema_version") != CANONICAL_SCHEMA_VERSION:
            VIOLATIONS.append((str(path), "schema_version", meta.get("schema_version"), type(meta.get("schema_version")), f"Non-canonical schema_version (expected {CANONICAL_SCHEMA_VERSION})"))


def main():
    root = Path(".")
    for ext in [".py", ".md", ".yaml", ".yml", ".json"]:
        for path in root.rglob(f"*{ext}"):
            scan_file(path)
    print("\n=== Metadata Block Protocol Violations ===")
    if not VIOLATIONS:
        print("No violations found. All metadata blocks are protocol-compliant.")
        return 0
    for v in VIOLATIONS:
        print(f"File: {v[0]} | Field: {v[1]} | Value: {v[2]!r} | Type: {v[3]} | Issue: {v[4]}")
    print(f"\nTotal violations: {len(VIOLATIONS)}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
