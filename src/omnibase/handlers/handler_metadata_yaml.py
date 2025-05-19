# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: <to-be-generated>
# name: handler_metadata_yaml.py
# version: 1.0.0
# author: OmniNode Team
# created_at: <to-be-generated>
# last_modified_at: <to-be-generated>
# description: Handler for ONEX metadata YAML files (node.onex.yaml, etc).
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'handler_metadata_yaml.py'}
# namespace: onex.stamped.handler_metadata_yaml.py
# meta_type: tool
# === /OmniNode:Metadata ===

import logging
import re
import uuid
from pathlib import Path
from typing import Any, Optional

from omnibase.canonical.canonical_serialization import (
    CanonicalYAMLSerializer,
    extract_metadata_block_and_body,
    strip_block_delimiters_and_assert,
)
from omnibase.metadata.metadata_constants import (
    METADATA_VERSION,
    SCHEMA_VERSION,
    YAML_META_CLOSE,
    YAML_META_OPEN,
)
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message import LogLevelEnum, OnexMessageModel
from omnibase.model.model_onex_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.schema.loader import SchemaLoader

logger = logging.getLogger(__name__)


class MetadataYAMLHandler(ProtocolFileTypeHandler):
    """
    Minimal YAML handler: only extraction, serialization, and validation.
    All protocol logic is in the engine.
    """

    # Canonical block placement policy (can be customized per handler/file type)
    block_placement_policy = BlockPlacementPolicy(
        allow_shebang=True,
        max_blank_lines_before_block=1,
        allow_license_header=True,
        license_header_pattern=None,
        normalize_blank_lines=True,
        enforce_block_at_top=True,
        placement_policy_version="1.0.0",
    )

    def __init__(
        self,
        default_author: str = "OmniNode Team",
        default_owner: str = "OmniNode Team",
        default_copyright: str = "OmniNode Team",
        default_description: str = "Stamped by MetadataYAMLHandler",
        default_state_contract: str = "state_contract://default",
        default_lifecycle: Lifecycle = Lifecycle.ACTIVE,
        default_meta_type: MetaType = MetaType.TOOL,
        default_entrypoint_type: EntrypointType = EntrypointType.PYTHON,
        default_runtime_language_hint: str = "python>=3.11",
        default_namespace_prefix: str = "onex.stamped",
        can_handle_predicate: Optional[Any] = None,
        schema_loader: Optional[SchemaLoader] = None,
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
        self.schema_loader = schema_loader

    def can_handle(self, path: Path, content: str) -> bool:
        if self.can_handle_predicate:
            return bool(self.can_handle_predicate(path))
        return path.suffix.lower() == ".yaml"

    def extract_block(self, path: Path, content: str) -> tuple[Optional[str], str]:
        """
        Extract the metadata block (as a string) and the rest of the file.
        """
        block, rest = extract_metadata_block_and_body(
            content, YAML_META_OPEN, YAML_META_CLOSE
        )
        logger.debug(f"extract_block: raw block=\n{block}")
        block_yaml = None
        if block:
            block_lines = []
            for line in block.splitlines():
                if line.lstrip().startswith("# "):
                    prefix_index = line.find("# ")
                    block_lines.append(line[:prefix_index] + line[prefix_index + 2 :])
                else:
                    block_lines.append(line)
            # Use shared utility to strip delimiters and assert
            delimiters = {
                YAML_META_OPEN.replace("# ", ""),
                YAML_META_CLOSE.replace("# ", ""),
            }
            block_yaml = strip_block_delimiters_and_assert(
                block_lines, delimiters, context="YAMLHandler.extract_block"
            )
            logger.debug(
                f"extract_block: block_yaml after prefix/delimiter strip=\n{block_yaml}"
            )
        logger.debug(f"extract_block: rest=\n{rest}")
        return block_yaml, rest

    def serialize_block(self, meta: NodeMetadataBlock) -> str:
        """
        Serialize the metadata model as a canonical YAML block, wrapped in delimiters.
        """
        serializer = CanonicalYAMLSerializer()
        block_body = serializer.canonicalize_metadata_block(meta, comment_prefix="# ")
        logger.debug(f"serialize_block: block_body=\n{block_body}")
        return f"{YAML_META_OPEN}\n{block_body}\n{YAML_META_CLOSE}"

    def construct_new_metadata_block(self, path: Path, now: str) -> NodeMetadataBlock:
        """
        Construct a new NodeMetadataBlock with defaults for an unstamped file.
        NOTE: version="1.0.0" is a placeholder. This must be replaced with a real versioning mechanism before production.
        UUID is generated for protocol compliance and uniqueness.
        """
        return NodeMetadataBlock(
            metadata_version=METADATA_VERSION,
            protocol_version=SCHEMA_VERSION,
            owner=self.default_owner,
            copyright=self.default_copyright,
            schema_version=SCHEMA_VERSION,
            name=path.stem,
            # TODO: versioning policy needed; '1.0.0' is a stub for now
            version="1.0.0",
            uuid=str(uuid.uuid4()),
            author=self.default_author,
            created_at=now,
            last_modified_at=now,
            description=self.default_description,
            state_contract=self.default_state_contract,
            lifecycle=self.default_lifecycle,
            hash="0" * 64,
            entrypoint=EntrypointBlock(
                type=self.default_entrypoint_type, target=path.name
            ),
            runtime_language_hint=self.default_runtime_language_hint,
            namespace=f"{self.default_namespace_prefix}.{path.stem}",
            meta_type=self.default_meta_type,
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Validate the YAML content against the ONEX node schema.
        """
        logger.debug(f"validate: content=\n{content}")
        try:
            meta_block_str, _ = self.extract_block(path, content)
            logger.debug(f"validate: meta_block_str=\n{meta_block_str}")
            if meta_block_str:
                meta = NodeMetadataBlock.from_file_or_content(
                    meta_block_str, already_extracted_block=meta_block_str
                )
                logger.debug(f"validate: loaded meta=\n{meta}")
            else:
                meta = None
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=None,
                messages=[],
                metadata={"note": "Validation passed"},
            )
        except Exception as e:
            logger.error(f"validate: Exception: {e}")

            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=None,
                messages=[
                    OnexMessageModel(
                        summary=f"Validation failed: {e}", level=LogLevelEnum.ERROR
                    )
                ],
                metadata={"note": "Validation failed", "error": str(e)},
            )

    def normalize_block_placement(self, content: str) -> str:
        """
        Normalize the placement of the metadata block according to block_placement_policy.
        - Preserves shebang if present.
        - Collapses all blank lines above the block to at most one.
        - Removes leading spaces/tabs before the block delimiter.
        - Ensures block is at the canonical position (top of file after shebang).
        """
        policy = self.block_placement_policy
        lines = content.splitlines(keepends=True)
        shebang = None
        start = 0
        # 1. Detect and preserve shebang
        if policy.allow_shebang and lines and lines[0].startswith("#!"):
            shebang = lines[0]
            start = 1
        # 2. Find the block delimiter
        open_delim = "# === OmniNode:Metadata ==="
        close_delim = "# === /OmniNode:Metadata ==="
        block_start = None
        block_end = None
        for i, line in enumerate(lines[start:], start):
            if line.lstrip().startswith(open_delim):
                block_start = i
                break
        if block_start is not None:
            for j in range(block_start, len(lines)):
                if lines[j].lstrip().startswith(close_delim):
                    block_end = j
                    break
        # 3. If block found, move it to canonical position
        if block_start is not None and block_end is not None:
            block_lines = lines[block_start : block_end + 1]
            after_block = lines[block_end + 1 :]
            # Remove leading spaces/tabs from block lines
            block_lines = [re.sub(r"^[ \t]+", "", line) for line in block_lines]
            # Collapse blank lines between shebang and block to at most one
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append("\n")  # At most one blank line
            normalized.extend(block_lines)
            # Remove leading blank lines after block
            after_block = list(after_block)
            while after_block and after_block[0].strip() == "":
                after_block.pop(0)
            normalized.extend(after_block)
            return "".join(normalized)
        else:
            # No block found, just normalize leading whitespace
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append("\n")
            normalized.extend(lines[start:])
            return "".join(normalized)
