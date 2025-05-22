# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: stamper_engine.py
# version: 1.0.0
# uuid: '381fc377-010c-4ba4-90e9-1039db602ad3'
# author: OmniNode Team
# created_at: '2025-05-22T14:05:21.446347'
# last_modified_at: '2025-05-22T18:05:26.860730'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: stamper_engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.stamper_engine
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
# === /OmniNode:Metadata ===


import datetime
import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional

import yaml

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.model.model_enum_log_level import LogLevelEnum
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_ignore import OnexIgnoreModel
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.runtime.protocol.protocol_file_io import ProtocolFileIO
from omnibase.runtime.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.in_memory_file_io import InMemoryFileIO

logger = logging.getLogger(__name__)


def json_default(obj: object) -> str:  # type: ignore[no-untyped-def]
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


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
        logger = logging.getLogger("omnibase.tools.stamper_engine")
        if handler_registry is None:
            handler_registry = FileTypeHandlerRegistry()
            handler_registry.register_all_handlers()  # Ensure all canonical handlers are registered for CLI/engine use
        self.handler_registry = handler_registry
        logger.debug(
            f"StamperEngine initialized with handled extensions: {self.handler_registry.handled_extensions()}"
        )

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
            logger.debug(
                f"[START] stamp_file for path={path}, template={template}, overwrite={overwrite}, repair={repair}, force_overwrite={force_overwrite}, author={author}"
            )
            # Special handling for ignore files
            ignore_filenames = {".onexignore", ".stamperignore", ".gitignore"}
            if path.name in ignore_filenames:
                handler = self.handler_registry.get_handler(path)
                if handler is None:
                    logger.warning(f"No handler registered for ignore file: {path}")
                    return OnexResultModel(
                        status=OnexStatus.WARNING,
                        target=str(path),
                        messages=[
                            OnexMessageModel(
                                summary=f"No handler registered for ignore file type: {path.suffix}",
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
                        metadata={
                            "note": "Skipped: no handler registered for ignore file"
                        },
                    )
                # Delegate stamping to the handler
                orig_content = ""
                if not isinstance(self.file_io, InMemoryFileIO):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            orig_content = f.read()
                        logger.debug(
                            f"Read file content for {path} (length={len(orig_content)})"
                        )
                    except Exception as e:
                        logger.error(f"Failed to read file {path}: {e}", exc_info=True)
                        orig_content = ""
                result = handler.stamp(path, orig_content)
                logger.debug(f"Stamp result for ignore file {path}: {result}")
                stamped_content = (
                    result.metadata.get("content") if result.metadata else None
                )
                if stamped_content is not None and stamped_content != orig_content:
                    logger.info(f"Writing stamped content to {path}")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(stamped_content)
                return result
            # Use handler-based stamping for all other files
            handler = self.handler_registry.get_handler(path)
            if handler is None:
                logger.warning(f"No handler registered for file: {path}")
                return OnexResultModel(
                    status=OnexStatus.WARNING,
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
                    logger.debug(
                        f"Read file content for {path} (length={len(orig_content)})"
                    )
                except Exception as e:
                    logger.error(f"Failed to read file {path}: {e}", exc_info=True)
                    orig_content = ""
            # Delegate all stamping/idempotency to the handler
            result = handler.stamp(path, orig_content)
            logger.debug(f"Stamp result for {path}: {result}")
            stamped_content = (
                result.metadata.get("content") if result.metadata else None
            )
            # Only write if content differs
            if stamped_content is not None and stamped_content != orig_content:
                logger.info(f"Writing stamped content to {path}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(stamped_content)
            return result
        except Exception as e:
            logger.error(f"Exception in stamp_file for {path}: {e}", exc_info=True)
            return OnexResultModel(
                status=OnexStatus.ERROR,
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
            content = json.dumps(data, sort_keys=True, default=json_default)
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
            include_patterns = []
            for ext in exts:
                include_patterns.append(f"*.{ext.lstrip('.')}")
                include_patterns.append(f"**/*{ext}")
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
                        if result.status == OnexStatus.SUCCESS
                        else (
                            LogLevelEnum.WARNING
                            if result.status == OnexStatus.WARNING
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
