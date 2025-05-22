# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: handler_python.py
# version: 1.0.0
# uuid: '785ba7a2-4ba6-4439-9da5-2c63f05bf615'
# author: OmniNode Team
# created_at: '2025-05-22T14:05:25.006018'
# last_modified_at: '2025-05-22T18:05:26.868494'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: handler_python.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.handler_python
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
from omnibase.runtime.mixins.block_placement_mixin import BlockPlacementMixin
from omnibase.runtime.mixins.metadata_block_mixin import MetadataBlockMixin
from omnibase.runtime.protocol.protocol_file_type_handler import ProtocolFileTypeHandler

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
            # Canonicality check
            is_canonical, reasons = self.is_canonical_block(
                prev_meta, NodeMetadataBlock
            )
            if not is_canonical:
                logger.warning(
                    f"Restamping {path} due to non-canonical metadata block: {reasons}"
                )
                prev_meta = None  # Force restamp in idempotency logic
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

        # Find the block between the delimiters
        block_pattern = rf"(?s){re.escape(PY_META_OPEN)}(.*?){re.escape(PY_META_CLOSE)}"
        match = re.search(block_pattern, content)
        if not match:
            return None, content
        block_content = match.group(1).strip("\n ")

        # Remove '# ' prefix from each line to get clean YAML
        yaml_lines = []
        for line in block_content.split("\n"):
            if line.startswith("# "):
                yaml_lines.append(line[2:])  # Remove '# ' prefix
            elif line.startswith("#"):
                yaml_lines.append(line[1:])  # Remove '#' prefix
            else:
                yaml_lines.append(line)  # Keep line as-is (for backwards compatibility)

        block_yaml = "\n".join(yaml_lines).strip()

        prev_meta = None
        try:
            data = yaml.safe_load(block_yaml)
            if isinstance(data, dict):
                prev_meta = NodeMetadataBlock(**data)
            elif isinstance(data, NodeMetadataBlock):
                prev_meta = data
        except Exception:
            prev_meta = None
        # Remove the block from the content
        rest = re.sub(block_pattern + r"\n?", "", content, count=1)
        return prev_meta, rest

    def serialize_block(self, meta: object) -> str:
        """
        Serialize a complete NodeMetadataBlock model as a YAML block with Python comment delimiters.
        Expects a complete, validated NodeMetadataBlock model instance.
        All Enums are converted to strings. The block is round-trip parseable.
        Each line of YAML is prefixed with '# ' to make it a valid Python comment.
        """
        from enum import Enum

        import yaml

        from omnibase.metadata.metadata_constants import PY_META_CLOSE, PY_META_OPEN
        from omnibase.model.model_node_metadata import NodeMetadataBlock

        def enum_to_str(obj: Any) -> Any:
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: enum_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [enum_to_str(v) for v in obj]
            else:
                return obj

        # Expect a complete NodeMetadataBlock model
        if not isinstance(meta, NodeMetadataBlock):
            raise ValueError(
                f"serialize_block expects NodeMetadataBlock, got {type(meta)}"
            )

        meta_dict = enum_to_str(meta.model_dump())

        # Custom YAML representer to force quoting of UUID and other string fields
        class QuotedStringDumper(yaml.SafeDumper):
            pass

        def quoted_string_representer(dumper, data):
            # Force quoting for UUID-like strings and other fields that need it
            if isinstance(data, str) and (
                # UUID pattern
                len(data) == 36
                and data.count("-") == 4
                and all(c.isalnum() or c == "-" for c in data)
            ):
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        QuotedStringDumper.add_representer(str, quoted_string_representer)

        yaml_block = yaml.dump(
            meta_dict,
            sort_keys=False,
            default_flow_style=False,
            Dumper=QuotedStringDumper,
        ).strip()

        # Add '# ' prefix to each line of YAML to make it a valid Python comment
        commented_yaml = "\n".join(f"# {line}" for line in yaml_block.split("\n"))

        return f"{PY_META_OPEN}\n{commented_yaml}\n{PY_META_CLOSE}\n"

    def normalize_rest(self, rest: str) -> str:
        return rest.strip()

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Use the centralized idempotency logic from MetadataBlockMixin for stamping.
        All protocol details are sourced from metadata_constants.
        Protocol: Must return only OnexResultModel, never the tuple from stamp_with_idempotency.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock

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
