# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.450134'
# description: Stamped by PythonHandler
# entrypoint: python://mixin_metadata_block
# hash: dffde2524d7c0f78c16a28c513badccd8746868b4ea73672d0d8b8eb4cc3cf92
# last_modified_at: '2025-05-29T14:14:00.624896+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: mixin_metadata_block.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_metadata_block
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 15dca7ec-5555-4e17-a348-f0cb38e9f274
# version: 1.0.0
# === /OmniNode:Metadata ===


import os
import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Tuple
from datetime import datetime, timezone

import yaml
import hashlib

if TYPE_CHECKING:
    pass

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.nodes.stamper_node.v1_0_0.helpers.hash_utils import compute_metadata_hash_for_new_blocks, compute_idempotency_hash
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.metadata.metadata_constants import (
    METADATA_VERSION,
    SCHEMA_VERSION,
    get_namespace_prefix,
)
from omnibase.model.model_node_metadata import Namespace, EntrypointBlock

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem

# Helper to load .onexversion once per process
_version_cache = None


def get_onex_versions() -> dict[str, Any]:
    global _version_cache
    if _version_cache is not None:
        if not isinstance(_version_cache, dict):
            raise OnexError(
                "_version_cache must be a dict", CoreErrorCode.INVALID_PARAMETER
            )
        return _version_cache
    # Try CWD, then walk up to repo root
    cwd = Path(os.getcwd())
    search_dirs: list[Path] = [cwd]
    # Only add as many parents as exist
    search_dirs += list(cwd.parents)
    # Add project root (if __file__ is in src/omnibase/handlers)
    search_dirs.append(Path(__file__).parent.parent.parent.parent)
    for d in search_dirs:
        candidate = d / ".onexversion"
        if candidate.exists():
            with open(candidate, "r") as f:
                data: dict[str, Any] = yaml.safe_load(f)
            for key in ("metadata_version", "protocol_version", "schema_version"):
                if key not in data:
                    raise OnexError(
                        f"Missing {key} in .onexversion at {candidate}",
                        CoreErrorCode.MISSING_REQUIRED_PARAMETER,
                    )
            if not isinstance(data, dict):
                raise OnexError(
                    ".onexversion must load as a dict", CoreErrorCode.INVALID_PARAMETER
                )
            # Patch: Convert entrypoint dict to EntrypointBlock if needed
            if "entrypoint" in data and isinstance(data["entrypoint"], dict):
                from omnibase.model.model_node_metadata import EntrypointBlock
                data["entrypoint"] = EntrypointBlock(**data["entrypoint"])
            _version_cache = data
            return data
    raise OnexError(
        ".onexversion file not found in CWD or any parent directory",
        CoreErrorCode.FILE_NOT_FOUND,
    )


class MetadataBlockMixin:
    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def extract_preserved_fields(
        self, prev_meta: Any
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        if prev_meta is None:
            return None, None, None
        return prev_meta.uuid, prev_meta.created_at, prev_meta.hash

    def handle_result(
        self,
        status: str,
        path: Path,
        messages: list[str],
        metadata: dict[str, Any],
        diff: Optional[str] = None,
        auto_fix_applied: bool = False,
        fixed_files: Optional[list[str]] = None,
        failed_files: Optional[list[str]] = None,
    ) -> "OnexResultModel":
        from omnibase.model.model_onex_message_result import OnexResultModel

        return OnexResultModel(
            status=status,
            target=str(path),
            messages=messages,
            metadata=metadata,
            diff=diff,
            auto_fix_applied=auto_fix_applied,
            fixed_files=fixed_files or [],
            failed_files=failed_files or [],
        )

    def update_metadata_block(
        self,
        prev_block: Optional[Any],
        updates: dict[str, Any],
        path: Path,
        model_cls: Optional[type] = None,
        context_defaults: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Canonical update function for metadata blocks.
        - Preserves sticky fields (created_at, uuid) from prev_block if present.
        - Applies updates from the updates dict.
        - Uses model's create_with_defaults for protocol-compliant construction.
        - Returns a new canonicalized model.
        """
        if model_cls is None:
            from omnibase.model.model_node_metadata import NodeMetadataBlock

            model_cls = NodeMetadataBlock

        # Extract values from previous block if it exists
        prev_data = prev_block.model_dump() if prev_block else {}

        # Start with context_defaults if provided
        base_data = context_defaults.copy() if context_defaults else {}

        # Apply previous data on top of context defaults
        base_data.update(prev_data)

        # Preserve sticky fields from previous block
        sticky_fields = ["created_at", "uuid"]
        for field in sticky_fields:
            if prev_block is not None and hasattr(prev_block, field):
                updates[field] = getattr(prev_block, field)
            elif field in prev_data:
                updates.setdefault(field, prev_data[field])

        # Always set name and path-based fields
        updates.setdefault("name", path.name)
        updates.setdefault("namespace", self._generate_namespace_from_path(path))

        # Handle entrypoint field specially
        entrypoint = updates.get("entrypoint", {})
        # PATCH: Use entrypoint_type and entrypoint_target from updates/context_defaults if provided
        entrypoint_type = updates.get("entrypoint_type") or base_data.get("entrypoint_type")
        if not entrypoint_type:
            ext = path.suffix.lower().lstrip(".")
            from omnibase.model.model_node_metadata import Namespace
            entrypoint_type = Namespace.CANONICAL_SCHEME_MAP.get(ext, ext or "python")
        entrypoint_target = updates.get("entrypoint_target") or base_data.get("entrypoint_target")
        if not entrypoint_target:
            entrypoint_target = path.stem
        emit_log_event("DEBUG", f"[UPDATE_METADATA_BLOCK] entrypoint_type={entrypoint_type}, entrypoint_target={entrypoint_target}", node_id=_COMPONENT_NAME)

        # Use the model's canonical constructor
        # Filter out None values to avoid validation errors
        # Combine base_data (context_defaults + prev_data) with updates
        final_data = {**base_data, **updates}
        
        # Don't filter out sticky fields (uuid, created_at) or other important fields
        # Only filter out None values and fields that are handled separately
        filtered_data = {
            k: v
            for k, v in final_data.items()
            if v is not None and k not in ["name", "author", "namespace", "entrypoint"]
        }

        # Remove hash from updates/context_defaults to avoid non-canonical assignment
        updates.pop("hash", None)
        if context_defaults:
            context_defaults.pop("hash", None)
        result = model_cls.create_with_defaults(  # type: ignore[attr-defined]
            name=updates.get("name", path.name),
            author=updates.get("author", "unknown"),
            namespace=updates.get("namespace", self._generate_namespace_from_path(path)),
            entrypoint_type=entrypoint_type,
            entrypoint_target=entrypoint_target,
            file_path=path,
            **filtered_data,
        )
        # Always set hash to placeholder here; real hash will be set after block construction
        result.hash = "0" * 64
        return result

    def _normalize_filename_for_namespace(self, filename: str) -> str:
        """
        Normalize a filename for use in namespace generation.
        Removes leading dots, replaces dashes with underscores, and ensures valid characters.
        """
        import re

        # Remove leading dots
        normalized = filename.lstrip(".")
        # Replace dashes and other invalid chars with underscores
        normalized = re.sub(r"[^a-zA-Z0-9_]", "_", normalized)
        # Remove consecutive underscores
        normalized = re.sub(r"_+", "_", normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip("_")
        # Ensure not empty
        if not normalized:
            normalized = "file"
        return normalized

    def _generate_namespace_from_path(self, path: Path) -> Namespace:
        """
        Generate a proper namespace based on the file's actual location in the project structure.
        Returns a Namespace object.
        """
        return Namespace.from_path(path)

    def stamp_with_idempotency(
        self,
        *,
        path: Path,
        content: str,
        author: str,
        entrypoint_type: str,
        meta_type: Optional[str] = None,
        description: Optional[str] = None,
        extract_block_fn: Any = None,
        serialize_block_fn: Any = None,
        normalize_rest_fn: Any = None,
        model_cls: Any = None,
        context_defaults: Optional[dict[str, Any]] = None,
    ) -> Tuple[str, OnexResultModel]:
        emit_log_event("DEBUG", f"[IDEMPOTENCY] Enter stamp_with_idempotency for {path}", node_id=_COMPONENT_NAME)
        try:
            try:
                prev_meta, rest = extract_block_fn(path, content)
                emit_log_event("DEBUG", f"[STAMP] original content: {repr(content)}", node_id=_COMPONENT_NAME)
                emit_log_event("DEBUG", f"[STAMP] extracted rest: {repr(rest)}", node_id=_COMPONENT_NAME)
                if not rest.strip():
                    raise RuntimeError(f"[TEST DEBUG] Extracted rest is empty after extract_block_fn in test_spacing_after_block. Original content: {repr(content)}")
                emit_log_event("DEBUG", f"[IDEMPOTENCY] extract_block_fn returned for {path}", node_id=_COMPONENT_NAME)
            except Exception as e:
                emit_log_event("ERROR", f"[IDEMPOTENCY] extract_block_fn exception for {path}: {e}", node_id=_COMPONENT_NAME)
                prev_meta, rest = None, content
            canonicalizer = (
                model_cls.get_canonicalizer() if model_cls else (lambda x: x)
            )
            # Apply normalize_rest_fn if provided, otherwise use canonicalizer
            if normalize_rest_fn:
                normalized_rest = normalize_rest_fn(rest)
            else:
                normalized_rest = canonicalizer(rest)
            volatile_fields = (
                list(model_cls.get_volatile_fields())
                if model_cls
                else ["hash", "last_modified_at"]
            )
            
            # Normalize filename for namespace
            normalized_stem = self._normalize_filename_for_namespace(path.stem)

            # Prepare updates
            updates = {
                "author": author,
                # Always canonicalize entrypoint before passing to model
                # PROTOCOL: Always use path.name (full filename) for entrypoint_target
                "entrypoint": EntrypointBlock(type=entrypoint_type, target=path.name),
                "namespace": self._generate_namespace_from_path(path),
                "meta_type": meta_type,
                "description": description,
            }
            emit_log_event("DEBUG", f"[STAMP_WITH_IDEMPOTENCY] entrypoint_target={path.name}", node_id=_COMPONENT_NAME)
            if prev_meta is None:
                # New block: set all required fields and compute hash
                updates["created_at"] = self.get_file_creation_date(path) or datetime.now(timezone.utc).isoformat()
                updates["last_modified_at"] = datetime.now(timezone.utc).isoformat()
                # Construct block with placeholder hash
                new_block = self.update_metadata_block(
                    prev_meta, updates, path, model_cls, context_defaults
                )
                # Compute canonical hash
                new_computed_hash = compute_metadata_hash_for_new_blocks(
                    metadata_dict=new_block.model_dump(),
                    body=normalized_rest,
                    volatile_fields=volatile_fields,
                    metadata_serializer=serialize_block_fn,
                    body_canonicalizer=canonicalizer,
                )
                new_block.hash = new_computed_hash
                final_block = new_block
            else:
                # Existing block: check idempotency
                computed_hash = compute_idempotency_hash(
                    metadata_model=prev_meta,
                    body=normalized_rest,
                    volatile_fields=volatile_fields,
                    metadata_serializer=serialize_block_fn,
                    body_canonicalizer=canonicalizer,
                )
                is_placeholder_hash = prev_meta.hash == "0" * 64
                stored_hash = prev_meta.hash
                content_changed = stored_hash != computed_hash
                
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"[IDEMPOTENCY] stored_hash={stored_hash[:16]}..., computed_hash={computed_hash[:16]}..., content_changed={content_changed}, is_placeholder={is_placeholder_hash}",
                    node_id=_COMPONENT_NAME,
                )
                
                if not content_changed and not is_placeholder_hash:
                    # Content hasn't changed - return existing block unchanged for perfect idempotency
                    block_str = serialize_block_fn(prev_meta)
                    if normalized_rest:
                        rest_stripped = normalized_rest.lstrip("\n")
                        new_content = (
                            f"{block_str}\n\n{rest_stripped}"
                            if rest_stripped
                            else f"{block_str}\n"
                        )
                    else:
                        new_content = block_str + "\n"
                    new_content = new_content.rstrip() + "\n"
                    
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"[END] stamp_with_idempotency for {path} (idempotent)",
                        node_id=_COMPONENT_NAME,
                    )
                    print(f"[DEBUG] new_content: {repr(new_content)}")
                    return new_content, self.handle_result(
                        status="success",
                        path=path,
                        messages=[],
                        metadata={
                            "note": "Stamped (idempotent)",
                            "hash": prev_meta.hash,
                            "content": new_content,
                        },
                    )
                else:
                    # Content changed OR placeholder hash: update last_modified_at and hash
                    updates["last_modified_at"] = datetime.now(timezone.utc).isoformat()
                    # Construct block with placeholder hash
                    updated_block = self.update_metadata_block(
                        prev_meta, updates, path, model_cls, context_defaults
                    )
                    # Compute canonical hash
                    updated_hash = compute_idempotency_hash(
                        metadata_model=updated_block,
                        body=normalized_rest,
                        volatile_fields=volatile_fields,
                        metadata_serializer=serialize_block_fn,
                        body_canonicalizer=canonicalizer,
                    )
                    updated_block.hash = updated_hash
                    final_block = updated_block
            emit_log_event("DEBUG", f"[IDEMPOTENCY] About to serialize final_block for {path}", node_id=_COMPONENT_NAME)
            block_str = serialize_block_fn(final_block)
            emit_log_event("DEBUG", f"[IDEMPOTENCY] Serialized block for {path}", node_id=_COMPONENT_NAME)
            if normalized_rest:
                print(f"[DEBUG] normalized_rest: {repr(normalized_rest)}")
                rest_stripped = normalized_rest.lstrip("\n")
                print(f"[DEBUG] rest_stripped: {repr(rest_stripped)}")
                block_str = block_str.rstrip()
                # Ensure exactly one blank line after the block, then code
                code_body = rest_stripped.lstrip()
                if code_body:
                    new_content = f"{block_str}\n\n{code_body}"
                else:
                    new_content = f"{block_str}\n\n"
            else:
                new_content = block_str + "\n\n"
            new_content = new_content.rstrip() + "\n"
            print(f"[DEBUG] new_content: {repr(new_content)}")
            emit_log_event("DEBUG", f"[IDEMPOTENCY] Exit stamp_with_idempotency for {path}", node_id=_COMPONENT_NAME)
            return new_content, self.handle_result(
                status="success",
                path=path,
                messages=[],
                metadata={
                    "note": "Stamped (idempotent or updated)",
                    "hash": final_block.hash,
                    "content": new_content,
                },
            )
        except Exception as e:
            emit_log_event("ERROR", f"[IDEMPOTENCY] Exception in stamp_with_idempotency for {path}: {e}", node_id=_COMPONENT_NAME)
            from omnibase.model.model_onex_message_result import OnexStatus, OnexMessageModel
            return content, self.handle_result(
                status=OnexStatus.ERROR,
                path=path,
                messages=[OnexMessageModel(summary=f"Error stamping file: {str(e)}")],
                metadata={
                    "note": f"Error: {str(e)}",
                    "content": content,
                },
            )

    @staticmethod
    def is_canonical_block(block: Any, model_cls: type) -> tuple[bool, list[str]]:
        """
        Check if a block is canonical (matches the model_cls schema exactly).
        Returns (True, []) if canonical, else (False, [reasons]).
        Raises TypeError if model_cls is not a Pydantic model class.
        """
        if block is None:
            return False, ["Block is None"]
        if not hasattr(model_cls, "model_fields"):
            raise OnexError(
                f"model_cls {model_cls} does not have model_fields; must be a Pydantic model class.",
                CoreErrorCode.INVALID_PARAMETER,
            )
        reasons = []
        # Get canonical field names and types
        canonical_fields = model_cls.model_fields
        block_dict = block.model_dump() if hasattr(block, "model_dump") else dict(block)
        # Check for extra fields
        extra_fields = set(block_dict.keys()) - set(canonical_fields.keys())
        if extra_fields:
            reasons.append(f"Extra fields: {sorted(extra_fields)}")
        # Check for missing fields
        missing_fields = set(canonical_fields.keys()) - set(block_dict.keys())
        if missing_fields:
            reasons.append(f"Missing fields: {sorted(missing_fields)}")
        # Check for wrong types, coercing dicts to models if needed
        for k, v in block_dict.items():
            if k in canonical_fields:
                expected_type = canonical_fields[k].annotation
                # If expected type is a Pydantic model and value is a dict, coerce
                try:
                    from pydantic import BaseModel

                    if (
                        isinstance(expected_type, type)
                        and issubclass(expected_type, BaseModel)
                        and isinstance(v, dict)
                    ):
                        v = expected_type(**v)
                except Exception:
                    pass
                # Accept None for optional fields
                if v is not None and not MetadataBlockMixin._is_instance_of_type(
                    v, expected_type
                ):
                    reasons.append(
                        f"Field '{k}' has wrong type: {type(v).__name__} (expected {expected_type})"
                    )
        return (len(reasons) == 0), reasons

    @staticmethod
    def _is_instance_of_type(value: Any, typ: Any) -> bool:
        # Handle Optional[...] and Union types
        import typing

        origin = getattr(typ, "__origin__", None)
        if origin is typing.Union:
            return any(
                MetadataBlockMixin._is_instance_of_type(value, t) for t in typ.__args__
            )
        # Handle parameterized generics (List, Dict, etc.)
        if origin is not None:
            # For List[...] and similar, check only the outer type
            if origin in (list, tuple, set):
                return isinstance(value, origin)
            if origin is dict:
                return isinstance(value, dict)
            # Fallback: do not pass parameterized generic to isinstance
            return False
        # Accept enums as their value type
        import enum

        if isinstance(typ, type) and issubclass(typ, enum.Enum):
            return isinstance(value, typ) or isinstance(value, str)
        # Accept Path for str fields
        if typ is str and isinstance(value, Path):
            return True
        return isinstance(value, typ)

    @staticmethod
    def get_file_creation_date(path: Path) -> Optional[str]:
        """
        Return the file creation date as an ISO8601 string, or None if not available.
        Uses st_birthtime on macOS, st_ctime as a fallback on other systems.
        """
        import os

        try:
            stat = os.stat(path)
            if sys.platform == "darwin" and hasattr(stat, "st_birthtime"):
                # macOS
                ts = stat.st_birthtime
            else:
                # Linux/other: st_ctime is not always creation time, but best available
                ts = stat.st_ctime
            return datetime.fromtimestamp(ts).isoformat()
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Error getting file creation date for {path}: {e}",
                node_id=_COMPONENT_NAME,
            )
            return None
