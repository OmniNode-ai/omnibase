# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 45cac6ab-dcdb-4666-877d-ed9110b3b347
# name: handler_metadata_yaml.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:38:44.936768
# last_modified_at: 2025-05-19T16:38:44.936769
# description: Stamped Python file: handler_metadata_yaml.py
# state_contract: none
# lifecycle: active
# hash: 335e6ea18bb448e732dfd3c494a03b5df15e4ae5d8a3687d23df1cae88e43948
# entrypoint: {'type': 'python', 'target': 'handler_metadata_yaml.py'}
# namespace: onex.stamped.handler_metadata_yaml.py
# meta_type: tool
# === /OmniNode:Metadata ===

import datetime
import logging
import re
import uuid
from pathlib import Path
from typing import Any, Optional, Tuple

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
from omnibase.model.model_onex_message_result import OnexResultModel
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

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
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

    def serialize_block(self, meta: Any) -> str:
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
        open_delim = YAML_META_OPEN
        close_delim = YAML_META_CLOSE
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

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Insert or update the canonical metadata block as a YAML comment block at the top of the file.
        Ensures idempotency and correct block placement.
        Idempotency policy: For already-stamped files, uuid and created_at are always preserved. Only last_modified_at and hash are updated if content changes. For new files, uuid and created_at are generated.
        Returns OnexResultModel with new content and status.
        """
        logger.info(f"Stamping file: {path}")
        messages: list[OnexMessageModel] = []
        try:
            block_yaml, rest_raw = self.extract_block(path, content)
            rest_lines = rest_raw.splitlines()
            rest_lines = [line.rstrip() for line in rest_lines]
            normalized_rest = "\n".join(rest_lines)
            if normalized_rest != "":
                normalized_rest += "\n"
            prev_meta = None
            prev_hash = None
            prev_last_modified = None
            prev_uuid = None
            prev_created_at = None
            try:
                prev_meta = NodeMetadataBlock.from_file_or_content(content)
                prev_hash = prev_meta.hash
                prev_last_modified = prev_meta.last_modified_at
                prev_uuid = prev_meta.uuid
                prev_created_at = prev_meta.created_at
            except Exception:
                pass
            logger.info(
                f"Previous metadata: hash={prev_hash}, last_modified_at={prev_last_modified}, uuid={prev_uuid}, created_at={prev_created_at}"
            )
            hash_for_compare = None
            if prev_last_modified is not None and prev_meta is not None:
                meta_for_hash = prev_meta.model_copy(
                    update={
                        "hash": "0" * 64,
                        "last_modified_at": prev_last_modified,
                        "uuid": prev_uuid,
                        "created_at": prev_created_at,
                    }
                )
                block_for_hash_yaml = self.serialize_block(meta_for_hash)
                block_lines = block_for_hash_yaml.splitlines()
                if block_lines and block_lines[0] == YAML_META_OPEN:
                    block_lines = block_lines[1:]
                if block_lines and block_lines[-1] == YAML_META_CLOSE:
                    block_lines = block_lines[:-1]
                block_body = "\n".join(block_lines)
                block_for_compare = f"{YAML_META_OPEN}\n{block_body}\n{YAML_META_CLOSE}"
                if normalized_rest:
                    full_content = f"{block_for_compare}\n\n{normalized_rest.rstrip()}"
                else:
                    full_content = block_for_compare
                import hashlib

                hash_for_compare = hashlib.sha256(
                    full_content.encode("utf-8")
                ).hexdigest()
            logger.info(f"Computed hash for compare: {hash_for_compare}")
            is_dirty = True
            if prev_hash is not None and hash_for_compare == prev_hash:
                is_dirty = False
            logger.info(f"Dirty check: is_dirty={is_dirty}")
            if not is_dirty and prev_meta is not None:
                logger.info("File is clean; reusing previous metadata block.")
                meta_for_output = prev_meta.model_copy(
                    update={
                        "hash": prev_hash,
                        "last_modified_at": prev_last_modified,
                        "uuid": prev_uuid,
                        "created_at": prev_created_at,
                    }
                )
                block_yaml = self.serialize_block(meta_for_output)
                block_lines = block_yaml.splitlines()
                if block_lines and block_lines[0] == YAML_META_OPEN:
                    block_lines = block_lines[1:]
                if block_lines and block_lines[-1] == YAML_META_CLOSE:
                    block_lines = block_lines[:-1]
                block_body = "\n".join(block_lines)
                block = f"{YAML_META_OPEN}\n{block_body}\n{YAML_META_CLOSE}"
                if normalized_rest:
                    stamped = f"{block}\n\n{normalized_rest}"
                else:
                    stamped = block
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    target=str(path),
                    messages=messages,
                    metadata={
                        "note": "Stamped YAML file (unchanged)",
                        "hash": prev_hash,
                        "content": stamped,
                    },
                    diff=None,
                    auto_fix_applied=True,
                    fixed_files=[str(path)],
                )
            logger.info("File is dirty; generating new metadata block.")
            now = datetime.datetime.utcnow().isoformat()
            try:
                meta_model = (
                    prev_meta.model_copy(
                        update={
                            "last_modified_at": now,
                            "uuid": prev_uuid,
                            "created_at": prev_created_at,
                        }
                    )
                    if prev_meta
                    else self.construct_new_metadata_block(path, now)
                )
            except Exception as e:
                logger.info(f"Exception during metadata block creation: {e}")
                messages.append(
                    OnexMessageModel(
                        summary=f"Metadata block creation failed: {e}",
                        level=LogLevelEnum.ERROR,
                    )
                )
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    target=str(path),
                    messages=messages,
                    metadata={
                        "note": "Metadata block creation failed",
                        "error": str(e),
                    },
                    auto_fix_applied=False,
                    failed_files=[str(path)],
                )
            hash_val = meta_model.compute_canonical_hash(
                normalized_rest, comment_prefix="# ", last_modified_at_override=now
            )
            meta_model.hash = hash_val
            try:
                block_yaml = self.serialize_block(meta_model)
            except Exception as ser_exc:
                messages.append(
                    OnexMessageModel(
                        summary=f"YAML serialization failed: {ser_exc}",
                        level=LogLevelEnum.ERROR,
                    )
                )
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    target=str(path),
                    messages=messages,
                    metadata={
                        "note": "YAML serialization failed",
                        "error": str(ser_exc),
                    },
                    auto_fix_applied=False,
                    failed_files=[str(path)],
                )
            block_lines = block_yaml.splitlines()
            if block_lines and block_lines[0] == YAML_META_OPEN:
                block_lines = block_lines[1:]
            if block_lines and block_lines[-1] == YAML_META_CLOSE:
                block_lines = block_lines[:-1]
            block_body = "\n".join(block_lines)
            block = f"{YAML_META_OPEN}\n{block_body}\n{YAML_META_CLOSE}"
            if normalized_rest:
                stamped = f"{block}\n\n{normalized_rest}"
            else:
                stamped = block
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=str(path),
                messages=messages,
                metadata={
                    "note": "Stamped YAML file",
                    "hash": hash_val,
                    "content": stamped,
                },
                diff=None,
                auto_fix_applied=True,
                fixed_files=[str(path)],
            )
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            messages.append(
                OnexMessageModel(
                    summary=f"Stamping failed: {e}", level=LogLevelEnum.ERROR
                )
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=messages,
                metadata={"note": "Stamping failed", "error": str(e), "traceback": tb},
                auto_fix_applied=False,
                failed_files=[str(path)],
            )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        return None
