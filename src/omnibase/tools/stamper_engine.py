import datetime
import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional

import yaml

from omnibase.core.core_registry import FileTypeRegistry
from omnibase.model.model_enum_file_status import FileStatusEnum
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
from omnibase.utils.utils_node_metadata_extractor import load_node_metadata_from_dict

logger = logging.getLogger(__name__)


class StamperEngine(ProtocolStamperEngine):
    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        schema_loader: ProtocolSchemaLoader,
        directory_traverser: Optional[DirectoryTraverser] = None,
        file_io: Optional[ProtocolFileIO] = None,
        file_type_registry: Optional[FileTypeRegistry] = None,
    ) -> None:
        self.schema_loader = schema_loader
        self.directory_traverser = directory_traverser or DirectoryTraverser()
        self.file_io = file_io or InMemoryFileIO()
        self.file_type_registry = file_type_registry or FileTypeRegistry()

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
            # Detect ignore files by name
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
                    "# === OmniNode:Metadata ===\n"
                    + yaml.safe_dump(metadata_block, sort_keys=False)
                    + "# === /OmniNode:Metadata ===\n"
                )
                if isinstance(self.file_io, InMemoryFileIO):
                    orig_content = self.file_io.files.get(str(path), None)
                    if orig_content is None:
                        orig_content = ""
                else:
                    orig_content = ""
                new_content = block_yaml + orig_content
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
                            file=None,
                            line=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                    metadata={
                        "meta_type": MetaTypeEnum.IGNORE_CONFIG.value,
                        "stamped_at": datetime.datetime.now().isoformat(),
                        "author": author,
                    },
                )
            if not self.file_io.exists(path):
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"File does not exist: {path}",
                            level=LogLevelEnum.ERROR,
                            file=None,
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                )
            is_empty = False
            is_invalid = False
            validation_error = None
            data = None
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
            ext = str(path.suffix).lower()
            if ext in [".yaml", ".yml"]:
                try:
                    data = self.file_io.read_yaml(path)
                    logger.debug(f"[stamp_file] YAML parsed data: {repr(data)}")
                    if data is None:
                        if (
                            is_empty
                            or orig_content is None
                            or (
                                isinstance(orig_content, str)
                                and orig_content.strip() == ""
                            )
                        ):
                            logger.debug(
                                "[stamp_file] Detected empty YAML file; returning warning."
                            )
                            is_empty = True
                        else:
                            logger.debug(
                                "[stamp_file] Detected malformed YAML; returning error."
                            )
                            return OnexResultModel(
                                status=OnexStatus.error,
                                target=str(path),
                                messages=[
                                    OnexMessageModel(
                                        summary="Malformed YAML: could not parse content",
                                        level=LogLevelEnum.ERROR,
                                        file=None,
                                        line=None,
                                        details=None,
                                        code=None,
                                        context=None,
                                        timestamp=None,
                                        type=None,
                                    )
                                ],
                            )
                    elif not isinstance(data, (dict, list)):
                        logger.debug(
                            "[stamp_file] YAML is not a mapping or sequence; returning error."
                        )
                        return OnexResultModel(
                            status=OnexStatus.error,
                            target=str(path),
                            messages=[
                                OnexMessageModel(
                                    summary="Malformed YAML: not a mapping or sequence",
                                    level=LogLevelEnum.ERROR,
                                    file=None,
                                    line=None,
                                    details=None,
                                    code=None,
                                    context=None,
                                    timestamp=None,
                                    type=None,
                                )
                            ],
                        )
                    elif isinstance(data, (dict, list)) and not data:
                        logger.debug(
                            "[stamp_file] YAML is empty dict/list; returning warning."
                        )
                        is_empty = True
                except Exception as e:
                    logger.debug(f"[stamp_file] Exception in YAML parse: {e}")
                    return OnexResultModel(
                        status=OnexStatus.error,
                        target=str(path),
                        messages=[
                            OnexMessageModel(
                                summary=f"Error stamping file: {e}",
                                level=LogLevelEnum.ERROR,
                                file=None,
                                line=None,
                                details=None,
                                code=None,
                                context=None,
                                timestamp=None,
                                type=None,
                            )
                        ],
                    )
            elif ext == ".json":
                try:
                    data = self.file_io.read_json(path)
                    logger.debug(f"[stamp_file] JSON parsed data: {repr(data)}")
                    if data is None:
                        if (
                            is_empty
                            or orig_content is None
                            or (
                                isinstance(orig_content, str)
                                and orig_content.strip() == ""
                            )
                        ):
                            logger.debug(
                                "[stamp_file] Detected empty JSON file; returning warning."
                            )
                            is_empty = True
                        else:
                            logger.debug(
                                "[stamp_file] Detected malformed JSON; returning error."
                            )
                            return OnexResultModel(
                                status=OnexStatus.error,
                                target=str(path),
                                messages=[
                                    OnexMessageModel(
                                        summary="Malformed JSON: could not parse content",
                                        level=LogLevelEnum.ERROR,
                                        file=None,
                                        line=None,
                                        details=None,
                                        code=None,
                                        context=None,
                                        timestamp=None,
                                        type=None,
                                    )
                                ],
                            )
                    elif not isinstance(data, (dict, list)):
                        logger.debug(
                            "[stamp_file] JSON is not a mapping or sequence; returning error."
                        )
                        return OnexResultModel(
                            status=OnexStatus.error,
                            target=str(path),
                            messages=[
                                OnexMessageModel(
                                    summary="Malformed JSON: not a mapping or sequence",
                                    level=LogLevelEnum.ERROR,
                                    file=None,
                                    line=None,
                                    details=None,
                                    code=None,
                                    context=None,
                                    timestamp=None,
                                    type=None,
                                )
                            ],
                        )
                    elif isinstance(data, (dict, list)) and not data:
                        logger.debug(
                            "[stamp_file] JSON is empty dict/list; returning warning."
                        )
                        is_empty = True
                except Exception as e:
                    logger.debug(f"[stamp_file] Exception in JSON parse: {e}")
                    return OnexResultModel(
                        status=OnexStatus.error,
                        target=str(path),
                        messages=[
                            OnexMessageModel(
                                summary=f"Error stamping file: {e}",
                                level=LogLevelEnum.ERROR,
                                file=None,
                                line=None,
                                details=None,
                                code=None,
                                context=None,
                                timestamp=None,
                                type=None,
                            )
                        ],
                    )
            elif ext == ".py":
                # Stamp Python file by prepending metadata block as comments
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
                    "description": f"Stamped Python file: {path.name}",
                    "state_contract": "none",
                    "lifecycle": "active",
                    "hash": "0" * 64,
                    "entrypoint": {"type": "python", "target": path.name},
                    "namespace": f"onex.stamped.{path.name}",
                    "meta_type": MetaTypeEnum.TOOL.value,
                }
                block_lines = ["# === OmniNode:Metadata ==="]
                for k, v in metadata_block.items():
                    block_lines.append(f"# {k}: {v}")
                block_lines.append("# === /OmniNode:Metadata ===\n")
                new_content = "\n".join(block_lines) + orig_content
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return OnexResultModel(
                    status=OnexStatus.success,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"Stamped Python file {path.name} with metadata block.",
                            level=LogLevelEnum.INFO,
                            details=None,
                            file=None,
                            line=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                    metadata={
                        "meta_type": MetaTypeEnum.TOOL.value,
                        "stamped_at": datetime.datetime.now().isoformat(),
                        "author": author,
                    },
                )
            elif ext == ".md":
                # Stamp Markdown file by prepending metadata block as HTML comment
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
                    "description": f"Stamped Markdown file: {path.name}",
                    "state_contract": "none",
                    "lifecycle": "active",
                    "hash": "0" * 64,
                    "entrypoint": {"type": "markdown", "target": path.name},
                    "namespace": f"onex.stamped.{path.name}",
                    "meta_type": MetaTypeEnum.TOOL.value,
                }
                block_lines = ["<!-- === OmniNode:Metadata ==="]
                for k, v in metadata_block.items():
                    block_lines.append(f"{k}: {v}")
                block_lines.append("=== /OmniNode:Metadata === -->\n")
                new_content = "\n".join(block_lines) + orig_content
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return OnexResultModel(
                    status=OnexStatus.success,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"Stamped Markdown file {path.name} with metadata block.",
                            level=LogLevelEnum.INFO,
                            details=None,
                            file=None,
                            line=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                    metadata={
                        "meta_type": MetaTypeEnum.TOOL.value,
                        "stamped_at": datetime.datetime.now().isoformat(),
                        "author": author,
                    },
                )
            else:
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"Unsupported file type: {path.suffix}",
                            level=LogLevelEnum.ERROR,
                            file=None,
                            line=None,
                            details=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                )
            if not is_empty and isinstance(data, dict):
                try:
                    load_node_metadata_from_dict(data)
                except Exception as e:
                    logger.debug(f"[stamp_file] Semantic validation failed: {e}")
                    is_invalid = True
                    validation_error = str(e)
            trace_hash = self._compute_trace_hash(path)
            if is_empty:
                statuses = [FileStatusEnum.empty, FileStatusEnum.unvalidated]
                return OnexResultModel(
                    status=OnexStatus.warning,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"File is empty; stamped with empty status. Trace hash: {trace_hash}",
                            level=LogLevelEnum.WARNING,
                            details=f"Trace hash: {trace_hash}",
                            file=None,
                            line=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                    metadata={
                        "trace_hash": trace_hash,
                        "template": template.value,
                        "stamped_at": datetime.datetime.now().isoformat(),
                        "author": author,
                        "statuses": [s.value for s in statuses],
                    },
                )
            if is_invalid:
                statuses = [FileStatusEnum.incomplete, FileStatusEnum.unvalidated]
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary=f"Semantic validation failed: {validation_error}",
                            level=LogLevelEnum.ERROR,
                            details=f"Trace hash: {trace_hash}",
                            file=None,
                            line=None,
                            code=None,
                            context=None,
                            timestamp=None,
                            type=None,
                        )
                    ],
                    metadata={
                        "trace_hash": trace_hash,
                        "template": template.value,
                        "stamped_at": datetime.datetime.now().isoformat(),
                        "author": author,
                        "statuses": [s.value for s in statuses],
                    },
                )
            statuses = [FileStatusEnum.unvalidated]
            return OnexResultModel(
                status=OnexStatus.success,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary=f"Simulated stamping for M0: {path}",
                        level=LogLevelEnum.INFO,
                        details=f"Trace hash: {trace_hash}",
                        file=None,
                        line=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
                metadata={
                    "trace_hash": trace_hash,
                    "template": template.value,
                    "stamped_at": datetime.datetime.now().isoformat(),
                    "author": author,
                    "statuses": [s.value for s in statuses],
                },
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary=f"Error stamping file: {str(e)}",
                        level=LogLevelEnum.ERROR,
                        file=None,
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
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
            exts = self.file_type_registry.get_all_extensions()
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
        return result

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
