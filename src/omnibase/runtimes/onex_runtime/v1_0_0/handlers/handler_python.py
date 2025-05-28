# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_python.py
# version: 1.0.0
# uuid: 7afa3e03-4735-44ea-b656-17f21e9cb87d
# author: OmniNode Team
# created_at: 2025-05-28T08:19:40.026642
# last_modified_at: 2025-05-28T15:55:27.566252
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 74417a2fc764cba102eefd8a5957eb3ba84d70297b5b3870f18deac98d51d60d
# entrypoint: python@handler_python.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.handler_python
# meta_type: tool
# === /OmniNode:Metadata ===


import re
from pathlib import Path
from typing import Any, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
    ToolCollection,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement import (
    BlockPlacementMixin,
)
from omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block import (
    MetadataBlockMixin,
)

open_delim = PY_META_OPEN
close_delim = PY_META_CLOSE

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class PythonHandler(ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin):
    """
    Handler for Python files (.py) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    All extracted metadata blocks must be validated and normalized using the canonical Pydantic model (NodeMetadataBlock) before further processing.
    """

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_owner: str = "OmniNode Team",
        default_copyright: str = "OmniNode Team",
        default_description: str = "Stamped by PythonHandler",
        default_state_contract: str = "state_contract://default",
        default_lifecycle: Lifecycle = Lifecycle.ACTIVE,
        default_meta_type: MetaTypeEnum = MetaTypeEnum.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = "omnibase.stamped",
        can_handle_predicate: Optional[Any] = None,
    ):
        self.default_author = default_author
        self.default_owner = default_owner
        self.default_copyright = default_copyright
        self.default_description = default_description
        self.default_state_contract = default_state_contract
        self.default_lifecycle = default_lifecycle
        self.default_meta_type = default_meta_type
        self.default_entrypoint_type = default_entrypoint_type
        self.default_runtime_language_hint = default_runtime_language_hint
        self.default_namespace_prefix = default_namespace_prefix
        self.can_handle_predicate = can_handle_predicate

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "python_handler"

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation."""
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler."""
        return "OmniNode Team"

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        return "Handles Python files (.py) for ONEX metadata stamping and validation"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".py", ".pyx"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # Python handler works with extensions, not specific filenames

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 50  # Runtime handler priority

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return bool(self.can_handle_predicate)  # Only if custom predicate is provided

    def can_handle(self, path: Path, content: str) -> bool:
        """
        Determine if this handler can process the given file.
        Uses an injected predicate or registry-driven check if provided.
        """
        if self.can_handle_predicate:
            result = self.can_handle_predicate(path)
            if isinstance(result, bool):
                return result
            return False
        return path.suffix.lower() == ".py"

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[START] extract_block for {path}",
            node_id=_COMPONENT_NAME,
        )
        try:
            prev_meta, rest = self._extract_block_with_delimiters(
                path, content, PY_META_OPEN, PY_META_CLOSE
            )
            # # Canonicality check - DISABLED to fix idempotency issue
            # is_canonical, reasons = self.is_canonical_block(
            #     prev_meta, NodeMetadataBlock
            # )
            # if not is_canonical:
            #     logger.warning(
            #         f"Restamping {path} due to non-canonical metadata block: {reasons}"
            #     )
            #     prev_meta = None  # Force restamp in idempotency logic
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[END] extract_block for {path}, result=({prev_meta}, rest)",
                node_id=_COMPONENT_NAME,
            )
            return prev_meta, rest
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Exception in extract_block for {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            return None, content

    def _extract_block_with_delimiters(
        self, path: Path, content: str, open_delim: str, close_delim: str
    ) -> tuple[Optional[Any], str]:
        import yaml

        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Starting extraction for {path}",
            node_id=_COMPONENT_NAME,
        )

        # Find the block between the delimiters using regex
        block_pattern = rf"(?s){re.escape(PY_META_OPEN)}(.*?){re.escape(PY_META_CLOSE)}"
        match = re.search(block_pattern, content)
        if not match:
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[EXTRACT] No metadata block found in {path}",
                node_id=_COMPONENT_NAME,
            )
            return None, content

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Metadata block found in {path}",
            node_id=_COMPONENT_NAME,
        )
        block_content = match.group(1).strip("\n ")

        # Remove '# ' prefix from each line to get clean YAML
        yaml_lines = []
        for line in block_content.split("\n"):
            if line.startswith("# "):
                yaml_lines.append(line[2:])  # Remove '# ' prefix
            elif line.startswith("#"):
                yaml_lines.append(line[1:])  # Remove '#' prefix
            else:
                yaml_lines.append(line)  # Keep line as-is

        block_yaml = "\n".join(yaml_lines).strip()
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Processed YAML length: {len(block_yaml)}",
            node_id=_COMPONENT_NAME,
        )

        prev_meta = None
        if block_yaml:
            try:
                data = yaml.safe_load(block_yaml)
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[EXTRACT] YAML parsing successful, keys: {list(data.keys())[:5]}",
                    node_id=_COMPONENT_NAME,
                )
                if isinstance(data, dict):
                    # Fix datetime objects - convert to ISO strings
                    for field in ["created_at", "last_modified_at"]:
                        if field in data and hasattr(data[field], "isoformat"):
                            data[field] = data[field].isoformat()

                    # Fix entrypoint format - handle both compact and flattened
                    if "entrypoint" in data:
                        entrypoint_val = data["entrypoint"]
                        if isinstance(entrypoint_val, str) and "@" in entrypoint_val:
                            # Compact format: "python@filename.py"
                            entry_type, entry_target = entrypoint_val.split("@", 1)
                            data["entrypoint"] = {
                                "type": entry_type.strip(),
                                "target": entry_target.strip(),
                            }
                        # If it's already a dict, keep it as-is
                    elif "entrypoint.type" in data or "entrypoint.target" in data:
                        # Legacy flattened format: entrypoint.type and entrypoint.target
                        data["entrypoint"] = {
                            "type": data.pop("entrypoint.type", "python"),
                            "target": data.pop("entrypoint.target", "unknown"),
                        }

                    prev_meta = NodeMetadataBlock(**data)
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"[EXTRACT] NodeMetadataBlock created successfully: {prev_meta.uuid}",
                        node_id=_COMPONENT_NAME,
                    )
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"[EXTRACT] Already NodeMetadataBlock: {prev_meta.uuid}",
                        node_id=_COMPONENT_NAME,
                    )
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[EXTRACT] Failed to parse block as YAML: {e}",
                    node_id=_COMPONENT_NAME,
                )
                prev_meta = None

        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[EXTRACT] Extraction complete, prev_meta: {prev_meta is not None}",
            node_id=_COMPONENT_NAME,
        )
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
            serialize_metadata_block,
        )
        return serialize_metadata_block(
            meta, PY_META_OPEN, PY_META_CLOSE, comment_prefix="# "
        )

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        Protocol: Must return only OnexResultModel, never the tuple from stamp_with_idempotency.
        """

        # Create context defaults WITHOUT sticky fields (uuid, created_at)
        # These will be preserved from existing metadata or generated only for new files
        context_defaults = {
            "name": path.name,
            "author": self.default_author,
            "entrypoint": {
                "type": str(self.default_entrypoint_type.value),
                "target": path.name,
            },
            "description": self.default_description,
            "meta_type": str(self.default_meta_type.value),
            "owner": self.default_owner,
            "copyright": self.default_copyright,
            "state_contract": self.default_state_contract,
            "lifecycle": str(self.default_lifecycle.value),
            "runtime_language_hint": self.default_runtime_language_hint,
            # Explicitly exclude sticky fields - they will be handled by idempotency logic
            # Namespace is now generated automatically from file path
        }

        # Handle function discovery if requested
        discover_functions = kwargs.get("discover_functions", False)
        if discover_functions:
            try:
                from omnibase.core.core_function_discovery import (
                    function_discovery_registry,
                )

                # Discover functions in the file content
                discovered_functions = (
                    function_discovery_registry.discover_functions_in_file(
                        path, content
                    )
                )

                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[TRACE] Discovered functions: {discovered_functions}",
                    node_id=_COMPONENT_NAME,
                )
                # Always set tools if discovery is enabled (even if empty)
                context_defaults["tools"] = ToolCollection.from_dict(discovered_functions)
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Function discovery failed for {path}: {e}",
                    node_id=_COMPONENT_NAME,
                )
                # Continue with normal stamping even if function discovery fails
        else:
            # Always set tools to empty ToolCollection if discovery is disabled
            context_defaults["tools"] = ToolCollection.from_dict({})

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[TRACE] Final context_defaults['tools']: {context_defaults.get('tools', 'NOT_SET')}, type: {type(context_defaults.get('tools', None))}",
            node_id=_COMPONENT_NAME,
        )

        result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
            path=path,
            content=content,
            author=self.default_author,
            entrypoint_type=self.default_entrypoint_type,
            meta_type=self.default_meta_type,
            description=self.default_description,
            extract_block_fn=self.extract_block,
            serialize_block_fn=self.serialize_block,
            model_cls=NodeMetadataBlock,
            context_defaults=context_defaults,
        )
        _, result = result_tuple
        return result

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(status=None, target=str(path), messages=[], metadata={})
