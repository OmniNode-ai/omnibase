# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: metadata_block_mixin.py
# version: 1.0.0
# uuid: aae52b31-0b70-48f0-8824-c2734a2c9ed8
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164159
# last_modified_at: 2025-05-21T16:42:46.083460
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 26791fe59b4b1c8795dd061ea7d1dbbf48564baf6c4195439e2425c169a47181
# entrypoint: {'type': 'python', 'target': 'metadata_block_mixin.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.metadata_block_mixin
# meta_type: tool
# === /OmniNode:Metadata ===

import logging
import os
import uuid
from pathlib import Path
from typing import Any, Optional, Tuple

import yaml

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.utils.metadata_utils import canonicalize_for_hash, compute_canonical_hash

# Helper to load .onexversion once per process
_version_cache = None


def get_onex_versions() -> dict[Any, Any]:
    global _version_cache
    if _version_cache is not None:
        if not isinstance(_version_cache, dict):
            raise TypeError("_version_cache must be a dict")
        return _version_cache
    # Try CWD, then walk up to repo root
    cwd = Path(os.getcwd())
    search_dirs = [cwd]
    # Only add as many parents as exist
    search_dirs += list(cwd.parents)
    # Add project root (if __file__ is in src/omnibase/handlers)
    search_dirs.append(Path(__file__).parent.parent.parent.parent)
    for d in search_dirs:
        candidate = d / ".onexversion"
        if candidate.exists():
            with open(candidate, "r") as f:
                data = yaml.safe_load(f)
            for key in ("metadata_version", "protocol_version", "schema_version"):
                if key not in data:
                    raise ValueError(f"Missing {key} in .onexversion at {candidate}")
            if not isinstance(data, dict):
                raise TypeError(".onexversion must load as a dict")
            _version_cache = data
            return data
    raise FileNotFoundError(
        ".onexversion file not found in CWD or any parent directory"
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
        messages: list,
        metadata: dict,
        diff: Optional[str] = None,
        auto_fix_applied: bool = False,
        fixed_files: Optional[list] = None,
        failed_files: Optional[list] = None,
    ) -> OnexResultModel:
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
        prev_block: Optional[NodeMetadataBlock],
        updates: dict,
        path: Path,
        model_cls: type[NodeMetadataBlock] = NodeMetadataBlock,
    ) -> NodeMetadataBlock:
        """
        Canonical update function for metadata blocks.
        - Preserves sticky fields (created_at, uuid) from prev_block if present.
        - Applies updates from the updates dict.
        - Returns a new canonicalized model.
        """
        # Sticky fields
        sticky_fields = ["created_at", "uuid"]
        base = prev_block.model_dump() if prev_block else {}
        for field in sticky_fields:
            if prev_block and field in base:
                updates.setdefault(field, base[field])
        # Always set name and path-based fields
        updates.setdefault("name", path.name)
        updates.setdefault("namespace", f"onex.stamped.{path.stem}")
        # Merge and construct
        merged = {**base, **updates}
        if model_cls is None and prev_block is not None:
            model_cls = type(prev_block)
        elif model_cls is None:
            model_cls = NodeMetadataBlock
        return model_cls(**merged)

    def stamp_with_idempotency(
        self,
        *,
        path: Path,
        content: str,
        author: str,
        entrypoint_type: str,
        namespace_prefix: str,
        meta_type: Optional[str] = None,
        description: Optional[str] = None,
        extract_block_fn: Any = None,
        serialize_block_fn: Any = None,
        normalize_rest_fn: Any = None,
        model_cls: Any = None,
    ) -> Tuple[str, OnexResultModel]:
        logger = logging.getLogger("omnibase.handlers.metadata_block_mixin")
        logger.debug(f"[START] stamp_with_idempotency for {path}")
        try:
            try:
                prev_meta, rest = extract_block_fn(path, content)
            except Exception:
                prev_meta, rest = None, content
            canonicalizer = (
                model_cls.get_canonicalizer() if model_cls else (lambda x: x)
            )
            normalized_rest = canonicalizer(rest)
            volatile_fields = (
                list(model_cls.get_volatile_fields())
                if model_cls
                else ["hash", "last_modified_at"]
            )
            import datetime

            now = datetime.datetime.utcnow().isoformat()
            # Compute hash for idempotency
            prev_block_dict = prev_meta.model_dump() if prev_meta else {}
            prev_full_content_for_hash = canonicalize_for_hash(
                prev_block_dict,
                normalized_rest,
                volatile_fields=volatile_fields,
                metadata_serializer=serialize_block_fn,
                body_canonicalizer=canonicalizer,
            )
            prev_computed_hash = compute_canonical_hash(prev_full_content_for_hash)
            # Prepare updates
            updates = {
                "author": author,
                "entrypoint": {"type": entrypoint_type, "target": path.name},
                "namespace": f"{namespace_prefix}.{path.stem}",
                "meta_type": meta_type,
                "description": description,
            }
            if prev_meta is None:
                # New block: set all required fields
                updates["created_at"] = self.get_file_creation_date(path) or now
                updates["last_modified_at"] = now
            else:
                # Existing block: check idempotency
                new_block = self.update_metadata_block(
                    prev_meta, updates, path, model_cls
                )
                new_block_dict = new_block.model_dump()
                new_full_content_for_hash = canonicalize_for_hash(
                    new_block_dict,
                    normalized_rest,
                    volatile_fields=volatile_fields,
                    metadata_serializer=serialize_block_fn,
                    body_canonicalizer=canonicalizer,
                )
                new_computed_hash = compute_canonical_hash(new_full_content_for_hash)
                if prev_computed_hash == new_computed_hash:
                    # Idempotent: preserve last_modified_at and hash
                    updates["last_modified_at"] = prev_meta.last_modified_at
                    updates["hash"] = prev_meta.hash
                else:
                    # Content changed: update last_modified_at and hash
                    updates["last_modified_at"] = now
                    updates["hash"] = new_computed_hash
            # Final block construction
            final_block = self.update_metadata_block(
                prev_meta, updates, path, model_cls
            )
            block_str = serialize_block_fn(final_block)
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
            logger.debug(f"[END] stamp_with_idempotency for {path}")
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
            logger.error(
                f"Exception in stamp_with_idempotency for {path}: {e}", exc_info=True
            )
            raise

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
            raise TypeError(
                f"model_cls {model_cls} does not have model_fields; must be a Pydantic model class."
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
        # Check for wrong types
        for k, v in block_dict.items():
            if k in canonical_fields:
                expected_type = canonical_fields[k].annotation
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
        Uses st_birthtime on macOS, st_ctime on Linux/other.
        """
        import os

        try:
            stat = os.stat(path)
            if hasattr(stat, "st_birthtime"):
                # macOS
                ts = stat.st_birthtime
            else:
                # Linux/other: st_ctime is not always creation time, but best available
                ts = stat.st_ctime
            import datetime

            return datetime.datetime.fromtimestamp(ts).isoformat()
        except Exception:
            return None
