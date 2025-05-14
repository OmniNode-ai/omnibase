# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "struct_index"
# namespace: "omninode.tools.struct_index"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:01+00:00"
# last_modified_at: "2025-05-05T12:44:01+00:00"
# entrypoint: "struct_index.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import os
import sys
import argparse
import fnmatch
import yaml
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import logging

from foundation.model.model_struct_index import TreeNode
from foundation.util.util_tree_format_utils import UtilTreeFormatUtils
from foundation.util.util_file_output_writer import UtilFileOutputWriter
from foundation.util.util_hash_utils import UtilHashUtils

DEFAULT_IGNORES = [
    ".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".venv", "venv", ".DS_Store", ".cache", ".tox", ".coverage", ".idea", ".vscode", ".egg-info", "dist", "build", "node_modules"
]

class StructIndex:
    def __init__(self, logger: logging.Logger, config: Optional[Dict[str, Any]] = None, dir_iter=None,
                 tree_format_utils=None, file_output_writer=None, hash_utils=None):
        self.logger = logger
        self.config = config or {}
        self.dir_iter = dir_iter or (lambda p: sorted(p.iterdir()))
        self.tree_format_utils = tree_format_utils or UtilTreeFormatUtils
        self.file_output_writer = file_output_writer or UtilFileOutputWriter
        self.hash_utils = hash_utils or UtilHashUtils

    def load_treeignore(self, directory: Path) -> Set[str]:
        ignore_patterns = set(DEFAULT_IGNORES)
        treeignore = directory / ".treeignore"
        if treeignore.exists():
            with treeignore.open("r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    ignore_patterns.add(line)
        return ignore_patterns

    def should_ignore(self, path: Path, ignore_patterns: Set[str], verbose: bool = False) -> bool:
        ignored = False
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(path), pattern):
                ignored = True
                if verbose:
                    self.logger.info(f"IGNORING: {path.name} (pattern: {pattern})")
                break
        if not ignored and verbose:
            self.logger.info(f"NOT IGNORING: {path.name}; patterns: {ignore_patterns}")
        return ignored

    def build_tree(self, directory: Path, max_depth: int = -1, include: Optional[str] = None, exclude: Optional[str] = None, follow_symlinks: bool = False, flat: bool = False, with_metadata: bool = False, verbose: bool = False, depth: int = 0, visited=None) -> TreeNode:
        if visited is None:
            visited = set()
        ignore_patterns = self.load_treeignore(directory)
        children = []
        file_count = 0
        dir_count = 0
        try:
            entries = self.dir_iter(directory)
        except Exception as e:
            if verbose:
                self.logger.warning(f"Failed to list {directory}: {e}")
            entries = []
        for entry in entries:
            if self.should_ignore(entry, ignore_patterns, verbose=verbose):
                if verbose:
                    self.logger.info(f"Ignored: {entry}")
                continue
            if entry.is_symlink() and not follow_symlinks:
                if verbose:
                    self.logger.info(f"Symlink skipped: {entry}")
                continue
            if entry.is_dir():
                inode = None
                try:
                    inode = (entry.stat().st_ino, entry.stat().st_dev)
                except Exception:
                    pass
                abs_path = str(entry.resolve())
                key = inode if inode else abs_path
                if follow_symlinks and key in visited:
                    if verbose:
                        self.logger.warning(f"Symlink loop detected, skipping {entry}")
                    continue
                if follow_symlinks:
                    visited.add(key)
                if max_depth != -1 and depth >= max_depth:
                    continue
                subtree = self.build_tree(entry, max_depth, include, exclude, follow_symlinks, flat, with_metadata, verbose, depth + 1, visited)
                if subtree:
                    children.append(subtree)
                    dir_count += 1
            elif entry.is_file():
                if include and not fnmatch.fnmatch(entry.name, include):
                    continue
                if exclude and fnmatch.fnmatch(entry.name, exclude):
                    continue
                stat = entry.stat() if with_metadata else None
                node = TreeNode(
                    name=entry.name,
                    type="file",
                    size=stat.st_size if stat else None,
                    mtime=stat.st_mtime if stat else None,
                    children=None
                )
                if verbose:
                    self.logger.info(f"Counting file: {entry.name}")
                children.append(node)
                file_count += 1
        node = TreeNode(
            name=directory.name,
            type="directory",
            children=children,
            metadata={
                "file_count": file_count,
                "dir_count": dir_count
            } if with_metadata else None
        )
        return node

    def write_tree_files(self, root: Path, node: TreeNode, write: bool = False, as_yaml: bool = False, flat: bool = False, with_metadata: bool = False, verbose: bool = False, output_dir: Optional[Path] = None, rel_path: Optional[Path] = None):
        self.file_output_writer.write_tree_files(
            root,
            node,
            write=write,
            as_yaml=as_yaml,
            flat=flat,
            with_metadata=with_metadata,
            verbose=verbose,
            output_dir=output_dir,
            rel_path=rel_path,
            tree_format_utils=self.tree_format_utils,
            hash_utils=self.hash_utils,
            logger=self.logger,
            is_top_level=True,
        ) 