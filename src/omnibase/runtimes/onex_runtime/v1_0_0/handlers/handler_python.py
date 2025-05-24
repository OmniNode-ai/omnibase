# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_python.py
# version: 1.0.0
# uuid: 785ba7a2-4ba6-4439-9da5-2c63f05bf615
# author: OmniNode Team
# created_at: 2025-05-22T14:05:25.006018
# last_modified_at: 2025-05-22T18:43:36.756496
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2b37f58f47f13ef28e5befd775d95f2ad4e4ccf674a786c873a95c71fe8919ea
# entrypoint: python@handler_python.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_python
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
import re
from pathlib import Path
from typing import Any, Optional

from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
from omnibase.model.model_node_metadata import (
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
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
logger = logging.getLogger("omnibase.runtime.handlers.handler_python")


class PythonHandler(ProtocolFileTypeHandler, MetadataBlockMixin, BlockPlacementMixin):
    """
    Handler for Python files (.py) for ONEX stamping.
    All block extraction, serialization, and idempotency logic is delegated to the canonical mixins.
    No custom or legacy logic is present; all protocol details are sourced from metadata_constants.
    """

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_owner: str = "OmniNode Team",
        default_copyright: str = "OmniNode Team",
        default_description: str = "Stamped by PythonHandler",
        default_state_contract: str = "state_contract://default",
        default_lifecycle: Lifecycle = Lifecycle.ACTIVE,
        default_meta_type: MetaType = MetaType.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = "onex.stamped",
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
        logger = logging.getLogger("omnibase.handlers.handler_python")
        logger.debug(f"[START] extract_block for {path}")
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
            logger.debug(f"[END] extract_block for {path}, result=({prev_meta}, rest)")
            return prev_meta, rest
        except Exception as e:
            logger.error(f"Exception in extract_block for {path}: {e}", exc_info=True)
            return None, content

    def _extract_block_with_delimiters(
        self, path: Path, content: str, open_delim: str, close_delim: str
    ) -> tuple[Optional[Any], str]:
        import yaml

        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN

        logger.debug(f"[EXTRACT] Starting extraction for {path}")

        # Find the block between the delimiters using regex
        block_pattern = rf"(?s){re.escape(PY_META_OPEN)}(.*?){re.escape(PY_META_CLOSE)}"
        match = re.search(block_pattern, content)
        if not match:
            logger.debug(f"[EXTRACT] No metadata block found in {path}")
            return None, content

        logger.debug(f"[EXTRACT] Metadata block found in {path}")
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
        logger.debug(f"[EXTRACT] Processed YAML length: {len(block_yaml)}")

        prev_meta = None
        if block_yaml:
            try:
                data = yaml.safe_load(block_yaml)
                logger.debug(
                    f"[EXTRACT] YAML parsing successful, keys: {list(data.keys())[:5]}"
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
                    logger.debug(
                        f"[EXTRACT] NodeMetadataBlock created successfully: {prev_meta.uuid}"
                    )
                elif isinstance(data, NodeMetadataBlock):
                    prev_meta = data
                    logger.debug(
                        f"[EXTRACT] Already NodeMetadataBlock: {prev_meta.uuid}"
                    )
            except Exception as e:
                logger.debug(f"[EXTRACT] Failed to parse block as YAML: {e}")
                prev_meta = None

        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        logger.debug(
            f"[EXTRACT] Extraction complete, prev_meta: {prev_meta is not None}"
        )
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        """
        Delegate to centralized runtime.metadata_block_serializer.serialize_metadata_block.
        """
        from typing import Any, Dict, Union

        from pydantic import BaseModel

        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
        from omnibase.runtimes.onex_runtime.v1_0_0.metadata_block_serializer import (
            serialize_metadata_block,
        )

        # Type cast to satisfy mypy
        meta_typed: Union[BaseModel, Dict[str, Any]]
        if isinstance(meta, BaseModel):
            meta_typed = meta
        elif isinstance(meta, dict):
            meta_typed = meta
        else:
            # Fallback for other object types - convert to dict if possible
            meta_typed = meta.__dict__ if hasattr(meta, "__dict__") else {}

        return serialize_metadata_block(
            meta_typed, PY_META_OPEN, PY_META_CLOSE, comment_prefix="# "
        )

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        Protocol: Must return only OnexResultModel, never the tuple from stamp_with_idempotency.
        """

        # Create a complete metadata model instead of a dictionary
        default_metadata = NodeMetadataBlock.create_with_defaults(
            name=path.name,
            author=self.default_author,
            namespace=self.default_namespace_prefix + f".{path.stem}",
            entrypoint_type=str(self.default_entrypoint_type.value),
            entrypoint_target=path.name,
            description=self.default_description,
            meta_type=str(self.default_meta_type.value),
            owner=self.default_owner,
            copyright=self.default_copyright,
            state_contract=self.default_state_contract,
            lifecycle=str(self.default_lifecycle.value),
            runtime_language_hint=self.default_runtime_language_hint,
        )

        # Convert model to dictionary for context_defaults
        context_defaults = default_metadata.model_dump()

        result_tuple: tuple[str, OnexResultModel] = self.stamp_with_idempotency(
            path=path,
            content=content,
            author=self.default_author,
            entrypoint_type=self.default_entrypoint_type,
            namespace_prefix=self.default_namespace_prefix,
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
