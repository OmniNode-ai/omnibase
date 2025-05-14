#!/usr/bin/env python3

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_file_utils"
# namespace: "omninode.tools.common_file_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "common_file_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolFileUtils']
# base_class: ['ProtocolFileUtils']
# mock_safe: true
# === /OmniNode:Metadata ===




"""file_utils.py
containers.foundation.src.foundation.script.validate.common.file_utils.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import fnmatch
import os
from pathlib import Path
from typing import Optional, Set, Union
from foundation.protocol.protocol_file_utils import ProtocolFileUtils


def find_files(
    target: Union[str, Path],
    pattern: str = "*.py",
    ignore_patterns: Optional[list] = None,
    utility_registry: 'UtilityRegistry' = None,
) -> Set[Path]:
    """Find files matching pattern in target directory.

    Args:
        target: Directory to search
        pattern: File pattern to match (default: *.py)
        ignore_patterns: List of patterns to ignore
        utility_registry: Utility registry for additional functionality
    Returns:
        Set[Path]: Set of matching file paths
    """
    if ignore_patterns is None:
        ignore_patterns = []
    default_ignores = [
        "**/__pycache__/**",
        "**/venv/**",
        "**/.venv/**",
        "**/env/**",
        "**/*_env/**",
        "**/*_venv/**",
        "**/.env/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
    ]
    target_path = Path(target)
    matching_files = set()
    for root, _, files in os.walk(target_path):
        root_path = Path(root)
        should_ignore = any(
            fnmatch.fnmatch(str(root_path), ignore)
            for ignore in default_ignores + ignore_patterns
        )
        if should_ignore:
            continue
        for file in files:
            file_path = root_path / file
            if fnmatch.fnmatch(file, pattern):
                matching_files.add(file_path)
    return matching_files


class FileUtils(ProtocolFileUtils):
    def check_file_extension(self, path: Path, valid_exts: Set[str]) -> bool:
        """Return True if the file has a valid extension."""
        return path.suffix.lower() in {ext.lower() for ext in valid_exts}

    def file_exists(self, path: Path) -> bool:
        """Return True if the file exists and is a file."""
        return path.exists() and path.is_file()

    def read_file(self, path: Path) -> str:
        """Read and return the contents of the file as a string."""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()