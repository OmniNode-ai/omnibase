# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.640260'
# description: Stamped by PythonHandler
# entrypoint: python://stamper_engine
# hash: 4ff3519c6b9fb2f239fe9e5d1ac8da5d38eccbb0dbcf0dc1d488c500224023ca
# last_modified_at: '2025-05-29T14:13:59.825400+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: stamper_engine.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.helpers.stamper_engine
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 62885027-34ec-4c0c-be75-83d4f192aef2
# version: 1.0.0
# === /OmniNode:Metadata ===


import datetime
import hashlib
import json
from pathlib import Path
from typing import List, Optional

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, TemplateTypeEnum, NodeMetadataField
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.nodes.parity_validator_node.v1_0_0.helpers.parity_node_metadata_loader import (
    get_node_name,
)
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io import InMemoryFileIO
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.core.core_function_discovery import function_discovery_registry

# Load node name from metadata to prevent drift
_NODE_DIRECTORY = Path(__file__).parent.parent  # stamper_node/v1_0_0/
_NODE_NAME = get_node_name(_NODE_DIRECTORY)

# Using structured logging via emit_log_event


def json_default(obj: object) -> str:  # type: ignore[no-untyped-def]
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise OnexError(
        f"Object of type {type(obj).__name__} is not JSON serializable",
        CoreErrorCode.INVALID_PARAMETER,
    )


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
        if handler_registry is None:
            handler_registry = FileTypeHandlerRegistry()
            handler_registry.register_all_handlers()  # Ensure all canonical handlers are registered for CLI/engine use
        self.handler_registry = handler_registry
        emit_log_event(
            LogLevelEnum.DEBUG,
            "StamperEngine initialized",
            context={
                "handled_extensions": self.handler_registry.handled_extensions(),
                "schema_loader": type(self.schema_loader).__name__,
                "file_io": type(self.file_io).__name__,
            },
            node_id=_NODE_NAME,
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
        emit_log_event(
            LogLevelEnum.INFO,
            "Stamping file",
            context={"file_path": str(path)},
            node_id=_NODE_NAME,
        )
        try:
            # Extract discover_functions from kwargs
            discover_functions = kwargs.get("discover_functions", False)
            emit_log_event(
                LogLevelEnum.DEBUG,
                "Starting stamp_file operation",
                context={
                    "path": str(path),
                    "template": (
                        template.value if hasattr(template, "value") else str(template)
                    ),
                    "overwrite": overwrite,
                    "repair": repair,
                    "force_overwrite": force_overwrite,
                    "author": author,
                    "discover_functions": discover_functions,
                },
                node_id=_NODE_NAME,
            )
            # Special handling for ignore files
            ignore_filenames = {".onexignore", ".gitignore"}
            if path.name in ignore_filenames:
                handler = self.handler_registry.get_handler(path)
                if handler is None:
                    emit_log_event(
                        LogLevelEnum.WARNING,
                        "No handler registered for ignore file",
                        context={"file_path": str(path), "file_name": path.name},
                        node_id=_NODE_NAME,
                    )
                    warning_level = LogLevelEnum.WARNING
                    return OnexResultModel(
                        status=OnexStatus.WARNING,
                        target=str(path),
                        messages=[
                            OnexMessageModel(
                                summary=f"No handler registered for ignore file type: {path.suffix}",
                                level=warning_level,
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
                orig_content = self.file_io.read_text(path)
                if orig_content is None:
                    orig_content = ""
                result = handler.stamp(path, orig_content, **kwargs)
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    "Stamp result for ignore file",
                    context={
                        "file_path": str(path),
                        "status": (
                            result.status.value
                            if hasattr(result.status, "value")
                            else str(result.status)
                        ),
                        "message_count": len(result.messages) if result.messages else 0,
                    },
                    node_id=_NODE_NAME,
                )
                stamped_content = (
                    result.metadata.get("content") if result.metadata else None
                )
                if stamped_content is not None and stamped_content != orig_content:
                    emit_log_event(
                        LogLevelEnum.INFO,
                        "Writing stamped content to file",
                        context={"file_path": str(path)},
                        node_id=_NODE_NAME,
                    )
                    self.file_io.write_text(path, stamped_content)
                # Inject default message if missing
                if not result.messages:
                    result.messages.append(
                        OnexMessageModel(
                            summary=f"File stamped successfully: {path}",
                            level=LogLevelEnum.INFO,
                            file=str(path),
                            timestamp=datetime.datetime.now(),
                        )
                    )
                return result
            # Use handler-based stamping for all other files
            handler = self.handler_registry.get_handler(path)
            if handler is None:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    "No handler registered for file",
                    context={"file_path": str(path), "file_suffix": path.suffix},
                    node_id=_NODE_NAME,
                )
                warning_level = LogLevelEnum.WARNING
                return OnexResultModel(
                    status=OnexStatus.WARNING,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"No handler registered for file type: {path.suffix}",
                            level=warning_level,
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
            orig_content = self.file_io.read_text(path)
            if orig_content is None:
                orig_content = ""

            # PATCH: Function discovery logic
            tools = None
            if discover_functions:
                discovered = function_discovery_registry.discover_functions_in_file(path, orig_content)
                emit_log_event(LogLevelEnum.DEBUG, f"Discovered functions: {discovered}", node_id=_NODE_NAME)
                if discovered:
                    from omnibase.model.model_node_metadata import ToolCollection
                    tools = ToolCollection({k: v for k, v in discovered.items()})
                    emit_log_event(LogLevelEnum.DEBUG, f"Tools object type: {type(tools)}; keys: {list(tools.root.keys())}", node_id=_NODE_NAME)
                else:
                    emit_log_event(LogLevelEnum.DEBUG, "No functions discovered for tools field", node_id=_NODE_NAME)

            # Delegate all stamping/idempotency to the handler, but inject tools if found
            handler_kwargs = dict(kwargs)
            if tools is not None:
                handler_kwargs[NodeMetadataField.TOOLS.value] = tools
            result = handler.stamp(path, orig_content, **handler_kwargs)
            emit_log_event(
                LogLevelEnum.DEBUG,
                "Stamp result for file",
                context={
                    "file_path": str(path),
                    "status": (
                        result.status.value
                        if hasattr(result.status, "value")
                        else str(result.status)
                    ),
                    "message_count": len(result.messages) if result.messages else 0,
                },
                node_id=_NODE_NAME,
            )
            stamped_content = (
                result.metadata.get("content") if result.metadata else None
            )
            # Only write if content differs
            if stamped_content is not None and stamped_content != orig_content:
                emit_log_event(
                    LogLevelEnum.INFO,
                    "Writing stamped content to file",
                    context={"file_path": str(path)},
                    node_id=_NODE_NAME,
                )
                self.file_io.write_text(path, stamped_content)
            # Inject default message if missing
            if not result.messages:
                result.messages.append(
                    OnexMessageModel(
                        summary=f"File stamped successfully: {path}",
                        level=LogLevelEnum.INFO,
                        file=str(path),
                        timestamp=datetime.datetime.now(),
                    )
                )
            return result
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                "Exception in stamp_file",
                context={
                    "file_path": str(path),
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                node_id=_NODE_NAME,
            )
            # Assign LogLevelEnum.ERROR to a variable to avoid scope issues
            error_level = LogLevelEnum.ERROR
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary=f"Error stamping file: {str(e)}",
                        level=error_level,
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
            emit_log_event(
                LogLevelEnum.ERROR,
                "Error computing trace hash",
                context={"file_path": str(filepath), "error": str(e)},
                node_id=_NODE_NAME,
            )
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

        emit_log_event(
            LogLevelEnum.DEBUG,
            "Processing directory",
            context={"exclude_patterns": exclude_patterns},
            node_id=_NODE_NAME,
        )
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
        emit_log_event(
            LogLevelEnum.DEBUG,
            "Directory processing result",
            context={"result_metadata": getattr(result, "metadata", None)},
            node_id=_NODE_NAME,
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
                    level=self._get_log_level_for_status(result.status),
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
        Load .onexignore patterns from the given directory and parent directories,
        return the combined ignore patterns for 'stamper' and 'all'.
        Delegates to DirectoryTraverser.load_ignore_patterns for parent directory traversal.
        """
        return self.directory_traverser.load_ignore_patterns(directory)

    def _get_log_level_for_status(self, status: OnexStatus) -> LogLevelEnum:
        """Helper method to map OnexStatus to LogLevelEnum."""
        if status == OnexStatus.SUCCESS:
            return LogLevelEnum.INFO
        elif status == OnexStatus.WARNING:
            return LogLevelEnum.WARNING
        else:
            return LogLevelEnum.ERROR
