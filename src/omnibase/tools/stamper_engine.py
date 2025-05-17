from pathlib import Path
from typing import Optional, List
from omnibase.protocol.protocol_stamper_engine import ProtocolStamperEngine
from omnibase.model.model_enum_template_type import TemplateTypeEnum
from omnibase.model.model_onex_message_result import OnexResultModel, OnexMessageModel, OnexStatus
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.utils.directory_traverser import DirectoryTraverser
from omnibase.utils.in_memory_file_io import InMemoryFileIO
from omnibase.model.model_enum_file_status import FileStatusEnum
from omnibase.utils.utils_node_metadata_extractor import load_node_metadata_from_dict
from datetime import datetime
import json
import hashlib
import logging
from omnibase.model.model_log_level_enum import LogLevelEnum

logger = logging.getLogger(__name__)

class StamperEngine(ProtocolStamperEngine):
    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        schema_loader: ProtocolSchemaLoader,
        directory_traverser: Optional[DirectoryTraverser] = None,
        file_io: Optional[ProtocolFileIO] = None,
    ):
        self.schema_loader = schema_loader
        self.directory_traverser = directory_traverser or DirectoryTraverser()
        self.file_io = file_io or InMemoryFileIO()

    def stamp_file(
        self,
        path: Path,
        template: TemplateTypeEnum = TemplateTypeEnum.MINIMAL,
        overwrite: bool = False,
        repair: bool = False,
        force_overwrite: bool = False,
        author: str = "OmniNode Team",
        **kwargs,
    ) -> OnexResultModel:
        try:
            if not self.file_io.exists(path):
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=str(path),
                    messages=[OnexMessageModel(summary=f"File does not exist: {path}", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                )
            is_empty = False
            is_invalid = False
            validation_error = None
            data = None
            orig_content = None
            if isinstance(self.file_io, InMemoryFileIO):
                orig_content = self.file_io.files.get(str(path), None)
            else:
                try:
                    if self.file_io.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            orig_content = f.read()
                        if orig_content is not None and isinstance(orig_content, str) and orig_content.strip() == "":
                            is_empty = True
                except Exception:
                    orig_content = None
            if str(path).endswith(".yaml"):
                try:
                    data = self.file_io.read_yaml(path)
                    logger.debug(f"[stamp_file] YAML parsed data: {repr(data)}")
                    if data is None:
                        if is_empty or orig_content is None or (isinstance(orig_content, str) and orig_content.strip() == ""):
                            logger.debug("[stamp_file] Detected empty YAML file; returning warning.")
                            is_empty = True
                        else:
                            logger.debug("[stamp_file] Detected malformed YAML; returning error.")
                            return OnexResultModel(
                                status=OnexStatus.error,
                                target=str(path),
                                messages=[OnexMessageModel(summary=f"Malformed YAML: could not parse content", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                            )
                    elif not isinstance(data, (dict, list)):
                        logger.debug("[stamp_file] YAML is not a mapping or sequence; returning error.")
                        return OnexResultModel(
                            status=OnexStatus.error,
                            target=str(path),
                            messages=[OnexMessageModel(summary=f"Malformed YAML: not a mapping or sequence", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                        )
                    elif isinstance(data, (dict, list)) and not data:
                        logger.debug("[stamp_file] YAML is empty dict/list; returning warning.")
                        is_empty = True
                except Exception as e:
                    logger.debug(f"[stamp_file] Exception in YAML parse: {e}")
                    return OnexResultModel(
                        status=OnexStatus.error,
                        target=str(path),
                        messages=[OnexMessageModel(summary=f"Error stamping file: {e}", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                    )
            elif str(path).endswith(".json"):
                try:
                    data = self.file_io.read_json(path)
                    logger.debug(f"[stamp_file] JSON parsed data: {repr(data)}")
                    if data is None:
                        if is_empty or orig_content is None or (isinstance(orig_content, str) and orig_content.strip() == ""):
                            logger.debug("[stamp_file] Detected empty JSON file; returning warning.")
                            is_empty = True
                        else:
                            logger.debug("[stamp_file] Detected malformed JSON; returning error.")
                            return OnexResultModel(
                                status=OnexStatus.error,
                                target=str(path),
                                messages=[OnexMessageModel(summary=f"Malformed JSON: could not parse content", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                            )
                    elif not isinstance(data, (dict, list)):
                        logger.debug("[stamp_file] JSON is not a mapping or sequence; returning error.")
                        return OnexResultModel(
                            status=OnexStatus.error,
                            target=str(path),
                            messages=[OnexMessageModel(summary=f"Malformed JSON: not a mapping or sequence", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                        )
                    elif isinstance(data, (dict, list)) and not data:
                        logger.debug("[stamp_file] JSON is empty dict/list; returning warning.")
                        is_empty = True
                except Exception as e:
                    logger.debug(f"[stamp_file] Exception in JSON parse: {e}")
                    return OnexResultModel(
                        status=OnexStatus.error,
                        target=str(path),
                        messages=[OnexMessageModel(summary=f"Error stamping file: {e}", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
                    )
            else:
                return OnexResultModel(
                    status=OnexStatus.error,
                    target=str(path),
                    messages=[OnexMessageModel(summary=f"Unsupported file type: {path.suffix}", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
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
                            file=None, line=None, code=None, context=None, timestamp=None, type=None
                        )
                    ],
                    metadata={
                        "trace_hash": trace_hash,
                        "template": template.value,
                        "stamped_at": datetime.now().isoformat(),
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
                            file=None, line=None, code=None, context=None, timestamp=None, type=None
                        )
                    ],
                    metadata={
                        "trace_hash": trace_hash,
                        "template": template.value,
                        "stamped_at": datetime.now().isoformat(),
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
                        file=None, line=None, code=None, context=None, timestamp=None, type=None
                    )
                ],
                metadata={
                    "trace_hash": trace_hash,
                    "template": template.value,
                    "stamped_at": datetime.now().isoformat(),
                    "author": author,
                    "statuses": [s.value for s in statuses],
                },
            )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(path),
                messages=[OnexMessageModel(summary=f"Error stamping file: {str(e)}", level=LogLevelEnum.ERROR, file=None, line=None, details=None, code=None, context=None, timestamp=None, type=None)],
            )

    def _compute_trace_hash(self, filepath: Path) -> str:
        try:
            suffix = filepath.suffix.lower()
            if suffix in [".yaml", ".yml"]:
                data = self.file_io.read_yaml(filepath)
            else:
                data = self.file_io.read_json(filepath)
            content = json.dumps(data, sort_keys=True)
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
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        ignore_file: Path = None,
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
        return self.directory_traverser.process_directory(
            directory=directory,
            processor=stamp_processor,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            recursive=recursive,
            ignore_file=ignore_file,
            dry_run=dry_run,
            max_file_size=self.MAX_FILE_SIZE,
        )

    def load_ignore_patterns(self, ignore_file=None):
        return self.directory_traverser.load_ignore_patterns(ignore_file)

    def should_ignore(self, path, patterns):
        return self.directory_traverser.should_ignore(path, patterns) 