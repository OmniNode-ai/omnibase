# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "util_file_output_writer"
# namespace: "omninode.tools.util_file_output_writer"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:30+00:00"
# last_modified_at: "2025-05-05T13:00:30+00:00"
# entrypoint: "util_file_output_writer.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['FileOutputWriterProtocol', 'Protocol']
# base_class: ['FileOutputWriterProtocol', 'Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Any, Optional, TextIO
from pathlib import Path
from datetime import datetime
import yaml
import sys
import json

class FileOutputWriterProtocol(Protocol):
    def write_tree_files(
        self,
        root: Path,
        node: Any,
        write: bool = False,
        as_yaml: bool = False,
        flat: bool = False,
        with_metadata: bool = False,
        verbose: bool = False,
        output_dir: Optional[Path] = None,
        rel_path: Optional[Path] = None,
        tree_format_utils: Any = None,
        hash_utils: Any = None,
        logger: Any = None,
        is_top_level: bool = True,
    ) -> None:
        ...

class UtilFileOutputWriter(FileOutputWriterProtocol):
    @staticmethod
    def write_tree_files(
        root: Path,
        node: Any,
        write: bool = False,
        as_yaml: bool = False,
        flat: bool = False,
        with_metadata: bool = False,
        verbose: bool = False,
        output_dir: Optional[Path] = None,
        rel_path: Optional[Path] = None,
        tree_format_utils: Any = None,
        hash_utils: Any = None,
        logger: Any = None,
        is_top_level: bool = True,
    ) -> None:
        if node.type != "directory":
            return
        rel_path = rel_path or Path("")
        out_base = (output_dir / rel_path) if output_dir else (root / rel_path)
        out_base.mkdir(parents=True, exist_ok=True)
        tree_text = tree_format_utils.tree_to_text(node)
        tree_hash = hash_utils.compute_hash(tree_text)
        timestamp = datetime.utcnow().isoformat()
        metadata = {
            "hash": tree_hash,
            "timestamp": timestamp,
            "file_count": node.metadata["file_count"] if node.metadata else None,
            "dir_count": node.metadata["dir_count"] if node.metadata else None
        }
        tree_file = out_base / ".tree"
        if write:
            with tree_file.open("w") as f:
                yaml.dump(node.model_dump(include={"name", "type", "children", "size", "mtime", "metadata"}), f)
            written = [str(tree_file)]
            if verbose and logger:
                logger.info(f"Wrote {', '.join(filter(None, written))}")
        else:
            if is_top_level:
                # Print the tree structure and metadata header to stdout
                print(f"# StructIndex Metadata\n# hash: {tree_hash}\n# timestamp: {timestamp}\n# file_count: {metadata['file_count']}\n# dir_count: {metadata['dir_count']}\n", file=sys.stdout)
                print(tree_text, file=sys.stdout)
            if tree_file.exists():
                with tree_file.open("r") as f:
                    try:
                        first_lines = [next(f) for _ in range(5)]
                    except StopIteration:
                        first_lines = []
                hash_line = next((line for line in first_lines if line.startswith("# hash:")), None)
                existing_hash = hash_line.split(":", 1)[1].strip() if hash_line else None
                if existing_hash == tree_hash:
                    if verbose and logger:
                        logger.info(f"{tree_file} is up-to-date.")
                else:
                    if logger:
                        logger.warning(f"{tree_file} is stale or missing metadata.")
            else:
                if logger:
                    logger.warning(f"{tree_file} does not exist.")
        if getattr(node, 'children', None):
            for child in node.children:
                if getattr(child, 'type', None) == "directory":
                    UtilFileOutputWriter.write_tree_files(
                        root,
                        child,
                        write,
                        as_yaml,
                        flat,
                        with_metadata,
                        verbose,
                        output_dir,
                        rel_path / child.name,
                        tree_format_utils,
                        hash_utils,
                        logger,
                        is_top_level=False,
                    )

    def write_output(self, path: str, content: Any) -> None:
        # TODO: Implement file writing logic
        raise NotImplementedError()

class OutputWriter:
    """
    DI-compliant utility for writing output to stdout (or any stream).
    All CLI and tool output must use this, never print().
    """
    def __init__(self, stream: TextIO = sys.stdout) -> None:
        self.stream = stream

    def write_output(self, data: str) -> None:
        """Write a string to the output stream (default: sys.stdout)."""
        self.stream.write(data)
        self.stream.flush()

    def write_json(self, obj: Any, *, indent: int = 2) -> None:
        """Serialize obj as JSON and write to the output stream."""
        json.dump(obj, self.stream, indent=indent)
        self.stream.write("\n")
        self.stream.flush() 