#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# schema_version: 1.0.0
# name: common_validator_utils
# namespace: omninode.tools.common_validator_utils
# meta_type: model
# version: 0.1.0
# author: OmniNode Team
# owner: jonah@omninode.ai
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-05-03T22:59:57+00:00
# last_modified_at: 2025-05-03T22:59:57+00:00
# entrypoint: common_validator_utils.py
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validator_utils.py
containers.foundation.src.foundation.script.validate.validator_utils.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import List, Set


def get_files_staged_for_deletion() -> List[str]:
    """Get a list of files that are staged for deletion in git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            check=True,
        )
        deleted_files = []
        for line in result.stdout.splitlines():
            if line.strip().startswith("D"):
                parts = line.strip().split(maxsplit=1)
                if len(parts) > 1:
                    deleted_files.append(parts[1].strip())
        return deleted_files
    except subprocess.CalledProcessError:
        logging.getLogger(__name__).warning(
            "Warning: Failed to get files staged for deletion"
        )
        return []


def get_staged_python_files() -> List[Path]:
    """Get a list of staged Python files from git."""
    try:
        deleted_files = get_files_staged_for_deletion()
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        all_staged_py_files = [
            file.strip()
            for file in result.stdout.splitlines()
            if file.strip().endswith(".py")
        ]
        staged_files = []
        for file in all_staged_py_files:
            if file in deleted_files:
                continue
            elif not os.path.isfile(file):
                continue
            else:
                staged_files.append(Path(file))
        return staged_files
    except subprocess.CalledProcessError as e:
        logging.getLogger(__name__).error(f"Error getting staged files: {e}")
        return []


def get_staged_files() -> List[str]:
    """Get a list of staged Python files (used in logger extra validator)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "--", "*.py"],
        capture_output=True,
        text=True,
    )
    return [
        f for f in result.stdout.splitlines() if f.strip() and os.path.isfile(f.strip())
    ]


def get_changed_files() -> Set[str]:
    """Get the list of changed files from git (used in container yaml
    validator)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except Exception as e:
        logging.getLogger(__name__).error(f"Error getting changed files from git: {e}")
        return set()


def should_validate_file(metadata, target: Path) -> bool:
    """Return True if the file should be validated based on metadata file_extensions and exempt_names."""
    ext = target.suffix.lower()
    if hasattr(metadata, 'file_extensions'):
        if ext not in metadata.file_extensions:
            return False
    elif hasattr(metadata, 'get') and callable(metadata.get):
        # Support dict-like metadata
        if ext not in metadata.get('file_extensions', []):
            return False
    # Optionally check for exempt_names (for registry entries, not files)
    return True