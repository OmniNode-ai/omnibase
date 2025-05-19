# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: <to-be-generated>
# name: handler_python.py
# version: 1.0.0
# author: OmniNode Team
# created_at: <to-be-generated>
# last_modified_at: <to-be-generated>
# description: Handler for Python files (.py) for ONEX stamping.
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'handler_python.py'}
# namespace: onex.stamped.handler_python.py
# meta_type: tool
# === /OmniNode:Metadata ===

import ast
import datetime
import re
from pathlib import Path
from typing import Any, Optional

from omnibase.metadata.metadata_constants import (
    METADATA_VERSION,
    PY_META_CLOSE,
    PY_META_OPEN,
    SCHEMA_VERSION,
)
from omnibase.model.enum_onex_status import OnexStatus
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


class PythonHandler(ProtocolFileTypeHandler):
    """
    Handler for Python files (.py) for ONEX stamping.
    All metadata field defaults are injected/configurable or sourced from canonical constants.
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

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """
        Insert or update the canonical metadata block as a Python comment block at the top of the file.
        Ensures idempotency and correct block placement.
        Returns OnexResultModel with new content and status.
        """
        messages: list[OnexMessageModel] = []
        try:
            # Remove all existing metadata blocks (idempotency) from the entire file
            meta_block_pattern = re.compile(
                rf"{PY_META_OPEN}([\s\S]+?){PY_META_CLOSE}\n*", re.MULTILINE
            )
            rest_raw = meta_block_pattern.sub("", content or "")
            # Normalize non-metadata content to unify normalization logic with compute_hash
            rest_lines = rest_raw.splitlines()
            # Remove trailing whitespace from each line to normalize
            rest_lines = [line.rstrip() for line in rest_lines]
            normalized_rest = "\n".join(rest_lines)
            # Add trailing newline if original content had non-empty body after normalization
            if normalized_rest != "":
                normalized_rest += "\n"

            # Try to parse previous metadata block
            prev_meta = None
            prev_hash = None
            prev_last_modified = None
            try:
                prev_meta = NodeMetadataBlock.from_file_or_content(content)
                prev_hash = prev_meta.hash
                prev_last_modified = prev_meta.last_modified_at
            except Exception:
                pass

            # Compute canonical hash for current content using previous last_modified_at
            hash_for_compare = None
            if prev_last_modified is not None and prev_meta is not None:
                # Use previous last_modified_at and hash=placeholder for hash computation
                meta_for_hash = prev_meta.model_copy(
                    update={"hash": "0" * 64, "last_modified_at": prev_last_modified}
                )
                block_for_hash_yaml = meta_for_hash.to_canonical_yaml_block(
                    comment_prefix="# ", enum_as_value=True
                )
                block_lines = block_for_hash_yaml.splitlines()
                if block_lines and block_lines[0] == PY_META_OPEN:
                    block_lines = block_lines[1:]
                if block_lines and block_lines[-1] == PY_META_CLOSE:
                    block_lines = block_lines[:-1]
                block_body = "\n".join(block_lines)
                block_for_compare = f"{PY_META_OPEN}\n{block_body}\n{PY_META_CLOSE}"
                if normalized_rest:
                    full_content = f"{block_for_compare}\n\n{normalized_rest.rstrip()}"
                else:
                    full_content = block_for_compare
                import hashlib

                hash_for_compare = hashlib.sha256(
                    full_content.encode("utf-8")
                ).hexdigest()

            # Dirty check: compare previous hash with current computed hash
            is_dirty = True
            if prev_hash is not None and hash_for_compare == prev_hash:
                is_dirty = False

            # If not dirty, reuse previous metadata block exactly as is (idempotency)
            if not is_dirty and prev_meta is not None:
                # Set both last_modified_at and hash fields to previous values for true idempotency
                meta_for_output = prev_meta.model_copy(
                    update={"hash": prev_hash, "last_modified_at": prev_last_modified}
                )
                block_yaml = meta_for_output.to_canonical_yaml_block(
                    comment_prefix="# ", enum_as_value=True
                )
                block_lines = block_yaml.splitlines()
                if block_lines and block_lines[0] == PY_META_OPEN:
                    block_lines = block_lines[1:]
                if block_lines and block_lines[-1] == PY_META_CLOSE:
                    block_lines = block_lines[:-1]
                block_body = "\n".join(block_lines)
                block = f"{PY_META_OPEN}\n{block_body}\n{PY_META_CLOSE}"
                # Reuse the exact normalized_rest with preserved spacing and newlines
                if normalized_rest:
                    stamped = f"{block}\n\n{normalized_rest}"
                else:
                    stamped = block
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    target=str(path),
                    messages=messages,
                    metadata={
                        "note": "Stamped Python file (unchanged)",
                        "hash": prev_hash,
                        "content": stamped,
                    },
                    diff=None,
                    auto_fix_applied=True,
                    fixed_files=[str(path)],
                )

            # Otherwise, update last_modified_at and hash (dirty file)
            now = datetime.datetime.utcnow().isoformat()
            try:
                meta_model = (
                    prev_meta.model_copy(update={"last_modified_at": now})
                    if prev_meta
                    else NodeMetadataBlock(
                        metadata_version=METADATA_VERSION,
                        protocol_version=SCHEMA_VERSION,
                        owner=self.default_owner,
                        copyright=self.default_copyright,
                        schema_version=SCHEMA_VERSION,
                        name=path.stem,
                        version="1.0.0",
                        uuid="00000000-0000-0000-0000-000000000000",
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
                )
            except Exception as e:
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
            # Compute canonical hash with updated last_modified_at
            hash_val = meta_model.compute_canonical_hash(
                normalized_rest, comment_prefix="# ", last_modified_at_override=now
            )
            meta_model.hash = hash_val
            # Serialize block as Python comment block, ensuring all Enums are .value
            try:
                block_yaml = meta_model.to_canonical_yaml_block(
                    comment_prefix="# ", enum_as_value=True
                )
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
            if block_lines and block_lines[0] == PY_META_OPEN:
                block_lines = block_lines[1:]
            if block_lines and block_lines[-1] == PY_META_CLOSE:
                block_lines = block_lines[:-1]
            block_body = "\n".join(block_lines)
            block = f"{PY_META_OPEN}\n{block_body}\n{PY_META_CLOSE}"
            # Use normalized_rest with preserved spacing and newlines
            if normalized_rest:
                stamped = f"{block}\n\n{normalized_rest}"
            else:
                stamped = block
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                target=str(path),
                messages=messages,
                metadata={
                    "note": "Stamped Python file",
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

    def _validate_syntax_and_block(
        self, path: Path, content: str, phase: str
    ) -> Optional[OnexResultModel]:
        """
        Helper to validate Python syntax and metadata block presence.
        """
        try:
            ast.parse(content)
            if PY_META_OPEN in content and PY_META_CLOSE in content:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS,
                    target=str(path),
                    messages=[],
                    metadata={
                        "note": f"{phase}-stamp validation passed (syntax and block present)"
                    },
                )
            else:
                return OnexResultModel(
                    status=OnexStatus.WARNING,
                    target=str(path),
                    messages=[
                        OnexMessageModel(
                            summary="Metadata block not present",
                            level=LogLevelEnum.WARNING,
                        )
                    ],
                    metadata={
                        "note": f"{phase}-stamp: block not present, but syntax valid"
                    },
                )
        except Exception as e:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary=f"{phase}-stamp validation failed: {e}",
                        level=LogLevelEnum.ERROR,
                    )
                ],
                metadata={"note": f"{phase}-stamp validation failed", "error": str(e)},
            )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> OnexResultModel | None:
        """
        Validate the Python file for syntax and block presence before stamping.
        """
        return self._validate_syntax_and_block(path, content, phase="Pre")

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> OnexResultModel | None:
        """
        Validate the Python file for syntax and block presence after stamping.
        """
        return self._validate_syntax_and_block(path, content, phase="Post")

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        """
        Compute the canonical hash for the Python file content using NodeMetadataBlock logic.
        The normalization (whitespace, newlines) matches exactly what is used in stamp.
        Returns the hash as a string, or None if computation fails.
        """
        try:
            meta_block_pattern = re.compile(
                rf"^{PY_META_OPEN}([\s\S]+?){PY_META_CLOSE}\n*", re.MULTILINE
            )
            meta_match = meta_block_pattern.match(content or "")
            if meta_match:
                rest_raw = content[meta_match.end() :]
            else:
                rest_raw = content or ""
            # Normalize non-metadata content as in stamp
            rest_lines = rest_raw.splitlines()
            rest_lines = [line.rstrip() for line in rest_lines]
            normalized_rest = "\n".join(rest_lines)
            if normalized_rest != "":
                normalized_rest += "\n"
            meta = NodeMetadataBlock.from_file_or_content(content)
            # Pass the exact last_modified_at from the parsed metadata to ensure test and handler symmetry and true idempotency
            return meta.compute_canonical_hash(
                normalized_rest,
                comment_prefix="# ",
                last_modified_at_override=meta.last_modified_at,
            )
        except Exception:
            return None
