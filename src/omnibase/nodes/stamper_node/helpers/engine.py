# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: engine.py
# version: 1.0.0
# uuid: '5ac9d2e6-1f56-4bd1-b8b3-1296f435ca40'
# author: OmniNode Team
# created_at: '2025-05-22T12:17:04.393270'
# last_modified_at: '2025-05-22T18:05:26.840326'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.engine
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
import logging
from pathlib import Path
from typing import List, Optional

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.model.model_enum_log_level import LogLevelEnum
from omnibase.model.model_enum_template_type import TemplateTypeEnum
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


class StamperEngine(ProtocolStamperEngine):
    """
    Canonical implementation of the ONEX stamping engine for metadata block insertion and idempotency.
    All file I/O, handler registry, and stamping logic is encapsulated here.
    """

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
        if handler_registry is None:
            handler_registry = FileTypeHandlerRegistry()
            handler_registry.register_all_handlers()
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
        """
        Stamp a single file with ONEX metadata, using the appropriate handler.
        Handles idempotency, error reporting, and file I/O.
        """
        try:
            logger.debug(
                f"[START] stamp_file for path={path}, template={template}, overwrite={overwrite}, repair={repair}, force_overwrite={force_overwrite}, author={author}"
            )
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
                orig_content = self._read_file(path)
                result = handler.stamp(path, orig_content)
                stamped_content = (
                    result.metadata.get("content") if result.metadata else None
                )
                if stamped_content is not None and stamped_content != orig_content:
                    self._write_file(path, stamped_content)
                return result
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
            orig_content = self._read_file(path)
            result = handler.stamp(path, orig_content)
            stamped_content = (
                result.metadata.get("content") if result.metadata else None
            )
            if stamped_content is not None and stamped_content != orig_content:
                self._write_file(path, stamped_content)
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
                metadata={"note": "Exception occurred during stamping"},
            )

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
        """
        Stamp all eligible files in a directory, respecting ignore patterns and options.
        Aggregates results and returns a summary OnexResultModel.
        """
        results = []
        patterns = self.load_ignore_patterns(ignore_file)

        def stamp_processor(file_path: Path) -> OnexResultModel:
            if self.should_ignore(file_path, patterns):
                logger.info(f"Ignoring file {file_path} due to ignore patterns")
                return OnexResultModel(
                    status=OnexStatus.SKIPPED,
                    target=str(file_path),
                    messages=[
                        OnexMessageModel(
                            summary="File ignored by pattern",
                            level=LogLevelEnum.INFO,
                            file=str(file_path),
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=datetime.datetime.now(),
                            type=None,
                        )
                    ],
                    metadata={"note": "Ignored by pattern"},
                )
            return self.stamp_file(
                file_path, template, overwrite, repair, force_overwrite, author
            )

        self.directory_traverser.traverse(
            directory,
            stamp_processor,
            recursive=recursive,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
        # Aggregate results (for now, just collect status)
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(directory),
            messages=[
                OnexMessageModel(
                    summary="Directory stamping complete",
                    level=LogLevelEnum.INFO,
                    file=str(directory),
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=datetime.datetime.now(),
                    type=None,
                )
            ],
            metadata={"files_processed": len(results)},
        )

    def load_ignore_patterns(self, ignore_file: Optional[Path] = None) -> list[str]:
        # TODO: Implement loading of ignore patterns from .onexignore or .stamperignore
        return []

    def should_ignore(self, path: Path, patterns: list[str]) -> bool:
        # TODO: Implement pattern matching logic
        return False

    def _read_file(self, path: Path) -> str:
        if isinstance(self.file_io, InMemoryFileIO):
            return self.file_io.files.get(str(path), "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}", exc_info=True)
            return ""

    def _write_file(self, path: Path, content: str) -> None:
        if isinstance(self.file_io, InMemoryFileIO):
            self.file_io.files[str(path)] = content
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}", exc_info=True)
