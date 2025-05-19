# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: f713ae0a-b757-4800-95de-e6760a954f39
# name: stamper_engine.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:38:49.825566
# last_modified_at: 2025-05-19T16:38:49.825581
# description: Stamped Python file: stamper_engine.py
# state_contract: none
# lifecycle: active
# hash: f9f592d6bfab1f06f7834e0dcafd0c671ef266c4c623e9f60cfde87088db473f
# entrypoint: {'type': 'python', 'target': 'stamper_engine.py'}
# namespace: onex.stamped.stamper_engine.py
# meta_type: tool
# === /OmniNode:Metadata ===

import datetime
import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import List, Optional

import yaml

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
from omnibase.model.model_enum_log_level import LogLevelEnum
from omnibase.model.model_enum_metadata import MetaTypeEnum
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_ignore import OnexIgnoreModel
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.in_memory_file_io import InMemoryFileIO

logger = logging.getLogger(__name__)


class StamperEngine(ProtocolStamperEngine):
    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        schema_loader: ProtocolSchemaLoader,
        directory_traverser: Optional[DirectoryTraverser] = None,
        file_io: Optional[ProtocolFileIO] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
    ) -> None:
        self.schema_loader = schema_loader
        self.directory_traverser = directory_traverser or DirectoryTraverser()
        self.file_io = file_io or InMemoryFileIO()
        self.handler_registry = handler_registry or FileTypeHandlerRegistry()

    def _json_default(self, obj: object) -> str:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs: object,
    ) -> OnexResultModel:
        try:
            # Special handling for ignore files
            ignore_filenames = {".onexignore", ".stamperignore", ".gitignore"}
            if path.name in ignore_filenames:
                # Stamp with special ignore_config metadata block
                import uuid

                metadata_block = {
                    "metadata_version": "0.1.0",
                    "schema_version": "1.1.0",
                    "uuid": str(uuid.uuid4()),
                    "name": path.name,
                    "version": "1.0.0",
                    "author": author,
                    "created_at": datetime.datetime.now().isoformat(),
                    "last_modified_at": datetime.datetime.now().isoformat(),
                    "description": f"Ignore file stamped for provenance: {path.name}",
                    "state_contract": "none",
                    "lifecycle": "active",
                    "hash": "0" * 64,
                    "entrypoint": {"type": "cli", "target": path.name},
                    "namespace": f"onex.ignore.{path.name}",
                    "meta_type": MetaTypeEnum.IGNORE_CONFIG.value,
                }
                # Write the metadata block to the file (prepend as YAML block)
                block_yaml = (
                    f"{YAML_META_OPEN}\n"
                    + yaml.safe_dump(metadata_block, sort_keys=False)
                    + f"{YAML_META_CLOSE}\n"
                )
                if isinstance(self.file_io, InMemoryFileIO):
                    orig_content = self.file_io.files.get(str(path), None)
                    if orig_content is None:
                        orig_content = ""
                else:
                    orig_content = ""
                new_content = block_yaml + orig_content
                # Ensure file ends with exactly one newline
                new_content = new_content.rstrip("\n") + "\n"
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return OnexResultModel(
                    status=OnexStatus.success,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"Stamped ignore file {path.name} with ignore_config metadata block.",
                            level=LogLevelEnum.INFO,
                            details=None,
                            file=str(path),
                            line=None,
                            code=None,
                            context=None,
                            timestamp=datetime.datetime.now(),
                            type=None,
                        )
                    ],
                    metadata={
                        "meta_type": MetaTypeEnum.IGNORE_CONFIG.value,
                        "stamped_at": datetime.datetime.now().isoformat(),
                        "author": author,
                    },
                )
            # Use handler-based stamping for all other files
            handler = self.handler_registry.get_handler(path)
            if handler is None:
                return OnexResultModel(
                    status=OnexStatus.warning,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"No handler registered for file type: {path.suffix}",
                            level=LogLevelEnum.WARNING,
                            file=str(path),
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=datetime.datetime.now(),
                            type=None,
                        )
                    ],
                    metadata={"note": "Skipped: no handler registered"},
                )
            # Read file content
            if isinstance(self.file_io, InMemoryFileIO):
                orig_content = self.file_io.files.get(str(path), None)
                if orig_content is None:
                    orig_content = ""
            else:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        orig_content = f.read()
                except Exception:
                    orig_content = ""
            # --- Hybrid idempotency logic start ---
            # 1. Get file mtime
            try:
                mtime = os.path.getmtime(path)
                mtime_iso = datetime.datetime.fromtimestamp(mtime).isoformat()
            except Exception:
                mtime = None
                mtime_iso = None
            # 2. Extract last_modified_at and hash from metadata block (if present)
            meta_block_match = re.search(
                r"(?s)^# === OmniNode:Metadata ===.*?# === /OmniNode:Metadata ===",
                orig_content,
            )
            last_modified_at = None
            prev_hash = None
            if meta_block_match:
                meta_block = meta_block_match.group(0)
                # Try to extract last_modified_at and hash
                last_modified_at_match = re.search(
                    r"last_modified_at: ([^\n]+)", meta_block
                )
                hash_match = re.search(r"hash: ([^\n]+)", meta_block)
                if last_modified_at_match:
                    last_modified_at = last_modified_at_match.group(1).strip()
                if hash_match:
                    prev_hash = hash_match.group(1).strip()
            # 3. If mtime matches last_modified_at, skip further processing
            if mtime_iso and last_modified_at and mtime_iso == last_modified_at:
                return OnexResultModel(
                    status=OnexStatus.success,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"File unchanged (mtime matches metadata): {path.name}",
                            level=LogLevelEnum.INFO,
                            file=str(path),
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=datetime.datetime.now(),
                            type=None,
                        )
                    ],
                    metadata={"note": "Skipped: mtime matches metadata"},
                )
            # 4. Otherwise, call handler.stamp and check hash
            result = handler.stamp(path, orig_content)
            if not isinstance(result, OnexResultModel):
                result = OnexResultModel.model_validate(result)
            elif type(result) is not OnexResultModel:
                result = OnexResultModel.model_validate(result.model_dump())
            stamped_content = (
                result.metadata.get("content") if result.metadata else None
            )
            # 5. Extract new hash from stamped_content's metadata block
            new_hash = None
            if stamped_content:
                new_meta_block_match = re.search(
                    r"(?s)^# === OmniNode:Metadata ===.*?# === /OmniNode:Metadata ===",
                    stamped_content,
                )
                if new_meta_block_match:
                    new_meta_block = new_meta_block_match.group(0)
                    new_hash_match = re.search(r"hash: ([^\n]+)", new_meta_block)
                    if new_hash_match:
                        new_hash = new_hash_match.group(1).strip()
            # 6. Only write if hash differs
            if new_hash and prev_hash and new_hash == prev_hash:
                return OnexResultModel(
                    status=OnexStatus.success,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"File unchanged (hash matches): {path.name}",
                            level=LogLevelEnum.INFO,
                            file=str(path),
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=datetime.datetime.now(),
                            type=None,
                        )
                    ],
                    metadata={"note": "Skipped: hash matches metadata"},
                )
            # 7. Only write if content differs
            if stamped_content is not None and stamped_content != orig_content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(stamped_content)
            return result
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary=f"Error stamping file: {str(e)}",
                        level=LogLevelEnum.ERROR,
                        file=str(path),
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=datetime.datetime.now(),
                        type=None,
                    )
                ],
            )

    def _compute_trace_hash(self, filepath: Path) -> str:
        try:
            suffix = filepath.suffix.lower()
            if suffix in [".yaml", ".yml"]:
                data = self.file_io.read_yaml(filepath)
            else:
                data = self.file_io.read_json(filepath)
            content = json.dumps(data, sort_keys=True, default=self._json_default)
            sha256 = hashlib.sha256(content.encode("utf-8"))
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing trace hash for {filepath}: {str(e)}")
            return f"error-{str(e)}"

    def process_directory(
        self,
        directory: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        recursive: bool = True,
        dry_run: bool = False,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
        author: str = "OmniNode Team",
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
    ) -> OnexResultModel:
        def stamp_processor(file_path: Path) -> OnexResultModel:
            return self.stamp_file(
                file_path,
                template=template,
                overwrite=overwrite,
                repair=repair,
                force_overwrite=force_overwrite,
                author=author,
            )

        logger.debug(f"process_directory: exclude_patterns={exclude_patterns}")
        # Use registry-driven include patterns if not provided
        if include_patterns is None:
            exts = list(self.handler_registry.handled_extensions())
            include_patterns = [f"**/*{ext}" for ext in exts]
        result = self.directory_traverser.process_directory(
            directory=directory,
            processor=stamp_processor,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            recursive=recursive,
            ignore_file=ignore_file,
            dry_run=dry_run,
            max_file_size=self.MAX_FILE_SIZE,
        )
        logger.debug(
            f"process_directory: result.metadata={getattr(result, 'metadata', None)}"
        )
        # Use result.metadata for all counts and reporting
        meta = getattr(result, "metadata", {}) or {}
        processed_count = meta.get("processed")
        failed_count = meta.get("failed")
        skipped_count = meta.get("skipped")
        total_size_bytes = meta.get("size_bytes")
        skipped_files = meta.get("skipped_files", [])
        skipped_file_reasons = meta.get("skipped_file_reasons", {})
        # If no files processed, preserve original messages (for test compatibility)
        if processed_count == 0:
            messages = result.messages
        else:
            messages = [
                OnexMessageModel(
                    summary=f"Processed {processed_count} files, "
                    f"{failed_count} failed, "
                    f"{skipped_count} skipped",
                    level=(
                        LogLevelEnum.INFO
                        if result.status == OnexStatus.success
                        else (
                            LogLevelEnum.WARNING
                            if result.status == OnexStatus.warning
                            else LogLevelEnum.ERROR
                        )
                    ),
                    file=str(directory),
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=datetime.datetime.now(),
                    type=None,
                )
            ]
        return OnexResultModel(
            status=result.status,
            target=str(directory),
            messages=messages,
            metadata={
                "processed": processed_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "size_bytes": total_size_bytes,
                "skipped_files": skipped_files,
                "skipped_file_reasons": skipped_file_reasons,
            },
        )

    def load_ignore_patterns(self, ignore_file: Optional[Path] = None) -> list[str]:
        """Load ignore patterns from a file using the directory traverser."""
        return self.directory_traverser.load_ignore_patterns(ignore_file)

    def should_ignore(self, path: Path, patterns: list[str]) -> bool:
        """Check if a file should be ignored using the directory traverser."""
        return self.directory_traverser.should_ignore(path, patterns)

    def load_onexignore(self, directory: Path) -> List[str]:
        """
        Load .onexignore YAML from the given directory (or parent dirs),
        return the combined ignore patterns for 'stamper' and 'all'.
        Fallback to .stamperignore (line-based) if .onexignore is missing.
        """
        onexignore_path = directory / ".onexignore"
        if onexignore_path.exists():
            with onexignore_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            model = OnexIgnoreModel.model_validate(data)
            patterns = []
            if model.all:
                patterns.extend(model.all.patterns)
            if model.stamper:
                patterns.extend(model.stamper.patterns)
            logger.debug(
                f"Loaded .onexignore patterns from {onexignore_path}: {patterns}"
            )
            return patterns
        # Fallback: .stamperignore (if present)
        stamperignore_path = directory / ".stamperignore"
        if stamperignore_path.exists():
            with stamperignore_path.open("r", encoding="utf-8") as f:
                lines = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
            logger.debug(
                f"Loaded .stamperignore patterns from {stamperignore_path}: {lines}"
            )
            return lines
        logger.debug(f"No .onexignore or .stamperignore found in {directory}")
        return []
