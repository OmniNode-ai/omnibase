# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: test_stamp_idempotency.py
# version: 1.0.0
# uuid: 4fac5e1b-11f0-4a13-9822-b052fcb9a0e5
# author: OmniNode Team
# created_at: 2025-05-21T12:16:31.784926
# last_modified_at: 2025-05-21T16:42:46.083789
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f69885a2362b6663d2df68f9a7e09f4f7a22fb74706d2c1b962ac2bdc35fbdb4
# entrypoint: {'type': 'python', 'target': 'test_stamp_idempotency.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_stamp_idempotency
# meta_type: tool
# === /OmniNode:Metadata ===

import datetime
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Optional, Tuple

import yaml

from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
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

    def construct_new_metadata_block(
        self,
        *,
        path: Path,
        now: str,
        author: str,
        entrypoint_type: str,
        namespace_prefix: str,
        meta_type: Optional[str] = None,
        description: Optional[str] = None,
        uuid_val: Optional[str] = None,
        created_at_val: Optional[str] = None,
        last_modified_at_val: Optional[str] = None,
        hash_val: Optional[str] = None,
    ) -> NodeMetadataBlock:
        """
        Construct a new NodeMetadataBlock with context-dependent fields. All other fields use model defaults.
        Preserves uuid, created_at, last_modified_at, and hash if provided.
        """
        logger = logging.getLogger("omnibase.handlers.metadata_block_mixin")
        logger.debug(
            f"[START] construct_new_metadata_block for {path} with now={now}, author={author}, entrypoint_type={entrypoint_type}, namespace_prefix={namespace_prefix}, meta_type={meta_type}, description={description}, uuid_val={uuid_val}, created_at_val={created_at_val}, last_modified_at_val={last_modified_at_val}, hash_val={hash_val}"
        )
        try:
            versions = get_onex_versions()
            # Ensure entrypoint_type is EntrypointType
            if isinstance(entrypoint_type, str):
                entrypoint_type = EntrypointType(entrypoint_type)
            # Ensure meta_type is MetaType
            if meta_type is not None and isinstance(meta_type, str):
                meta_type = MetaType(meta_type)
            # Ensure lifecycle is Lifecycle
            lifecycle_val = Lifecycle.ACTIVE
            # last_modified_at and hash must never be None
            last_modified = last_modified_at_val or now
            hash_val_final = hash_val or "0" * 64
            block = NodeMetadataBlock(
                metadata_version=versions["metadata_version"],
                protocol_version=versions["protocol_version"],
                schema_version=versions["schema_version"],
                name=path.name,
                uuid=uuid_val or self.generate_uuid(),
                author=author,
                created_at=created_at_val or now,
                last_modified_at=last_modified,
                hash=hash_val_final,
                entrypoint=EntrypointBlock(type=entrypoint_type, target=path.name),
                namespace=f"{namespace_prefix}.{path.stem}",
                meta_type=meta_type if meta_type is not None else MetaType.TOOL,
                lifecycle=lifecycle_val,
            )
            if description is not None:
                block.description = description
            logger.debug(
                f"[END] construct_new_metadata_block for {path}, block={block}"
            )
            return block
        except Exception as e:
            logger.error(
                f"Exception in construct_new_metadata_block for {path}: {e}",
                exc_info=True,
            )
            raise

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

    def stamp_with_idempotency(
        self,
        *,
        path: Path,
        content: str,
        now: str,
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
        """
        Centralized idempotency logic for stamping. Returns a tuple: (new_content, OnexResultModel).
        WARNING: Handlers MUST unpack and return only the OnexResultModel from their stamp method.
        If a handler returns the tuple directly, this will break the protocol and cause downstream errors.
        """
        logger = logging.getLogger("omnibase.handlers.metadata_block_mixin")
        logger.debug(f"[START] stamp_with_idempotency for {path}")
        try:
            print(f"[DEBUG] stamp_with_idempotency called with now={now}")
            # mypy: ignore[assignment]
            # The following variables are assigned but not used; comment them out to fix mypy errors
            # messages = ...
            # prev_last_modified = ...
            try:
                prev_meta, rest = extract_block_fn(path, content)
            except Exception:
                prev_meta, rest = None, content
            prev_uuid, prev_created_at, prev_hash = self.extract_preserved_fields(
                prev_meta
            )
            # Always strictly preserve created_at: prev_meta > file creation date > now (only if truly new)
            created_at_val = prev_created_at
            if not created_at_val:
                created_at_val = self.get_file_creation_date(path)
            # Only use now if both previous block and file creation date are unavailable
            if not created_at_val:
                created_at_val = now
            # Always try to preserve uuid if present (sticky field)
            uuid_val = prev_uuid
            # Use canonicalizer from model
            canonicalizer = (
                model_cls.get_canonicalizer() if model_cls else (lambda x: x)
            )
            normalized_rest = canonicalizer(rest)
            # Get volatile fields from model
            volatile_fields = (
                list(model_cls.get_volatile_fields())
                if model_cls
                else ["hash", "last_modified_at"]
            )
            # If no previous metadata block, skip idempotency check and construct new block
            if prev_meta is None:
                new_block = self.build_metadata_block(
                    path=path,
                    now=now,
                    author=author,
                    entrypoint_type=entrypoint_type,
                    namespace_prefix=namespace_prefix,
                    meta_type=meta_type,
                    description=description,
                    uuid_val=uuid_val,  # Only None if no previous block
                    created_at_val=created_at_val,
                    last_modified_at_val=now,
                )
                if new_block is not None and isinstance(new_block, dict):
                    new_block = model_cls(**new_block)
                new_block_dict = new_block.model_dump()
                new_full_content_for_hash = canonicalize_for_hash(
                    new_block_dict,
                    normalized_rest,
                    volatile_fields=volatile_fields,
                    metadata_serializer=serialize_block_fn,
                    body_canonicalizer=canonicalizer,
                )
                computed_hash = compute_canonical_hash(new_full_content_for_hash)
                new_block.hash = computed_hash
                new_block.last_modified_at = now
                block_str = serialize_block_fn(new_block)
                # Normalize: exactly one blank line between block and next content
                if normalized_rest:
                    # Remove all leading blank lines from rest
                    rest_stripped = normalized_rest.lstrip("\n")
                    new_content = (
                        f"{block_str}\n\n{rest_stripped}"
                        if rest_stripped
                        else f"{block_str}\n"
                    )
                else:
                    new_content = block_str + "\n"
                new_content = new_content.rstrip() + "\n"
                logger.debug(
                    f"[END] stamp_with_idempotency for {path} (no previous block)"
                )
                return new_content, self.handle_result(
                    status="success",
                    path=path,
                    messages=[],
                    metadata={
                        "note": "Stamped new block (no previous metadata)",
                        "hash": computed_hash,
                        "content": new_content,
                    },
                )
            # --- Robust restamping: always remove old block, preserve sticky fields, write new canonical block ---
            # Extract sticky fields from previous block if present
            preserved_uuid = prev_uuid if prev_uuid else None
            preserved_created_at = (
                prev_created_at
                if prev_created_at
                else self.get_file_creation_date(path) or now
            )
            # Always remove the old block and restamp
            new_block = self.build_metadata_block(
                path=path,
                now=now,
                author=author,
                entrypoint_type=entrypoint_type,
                namespace_prefix=namespace_prefix,
                meta_type=meta_type,
                description=description,
                uuid_val=preserved_uuid,
                created_at_val=preserved_created_at,
                last_modified_at_val=now,
            )
            if new_block is not None and isinstance(new_block, dict):
                new_block = model_cls(**new_block)
            new_block_dict = new_block.model_dump()
            new_full_content_for_hash = canonicalize_for_hash(
                new_block_dict,
                normalized_rest,
                volatile_fields=volatile_fields,
                metadata_serializer=serialize_block_fn,
                body_canonicalizer=canonicalizer,
            )
            computed_hash = compute_canonical_hash(new_full_content_for_hash)
            new_block.hash = computed_hash
            new_block.last_modified_at = now
            block_str = serialize_block_fn(new_block)
            # Normalize: exactly one blank line between block and next content
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
            logger.debug(f"[END] robust restamp for {path}")
            return new_content, self.handle_result(
                status="success",
                path=path,
                messages=[],
                metadata={
                    "note": "Robust restamp: old block removed, sticky fields preserved, canonical block written",
                    "hash": computed_hash,
                    "content": new_content,
                },
            )
        except Exception as e:
            logger.error(
                f"Exception in stamp_with_idempotency for {path}: {e}", exc_info=True
            )
            raise

    def build_metadata_block(
        self,
        *,
        path: Path,
        author: str,
        entrypoint_type: str,
        namespace_prefix: str,
        now: Optional[str] = None,
        meta_type: Optional[str] = None,
        description: Optional[str] = None,
        uuid_val: Optional[str] = None,
        created_at_val: Optional[str] = None,
        last_modified_at_val: Optional[str] = None,
        hash_val: Optional[str] = None,
        version: str = "1.0.0",
        owner: str = "OmniNode Team",
        copyright: str = "OmniNode Team",
        protocol_version: Optional[str] = None,
        schema_version: Optional[str] = None,
        runtime_language_hint: str = "python>=3.11",
        state_contract: str = "state_contract://default",
        lifecycle: str = "active",
        extra_fields: Optional[dict] = None,
    ) -> NodeMetadataBlock:
        """
        Centralized construction of NodeMetadataBlock for all handlers.
        Handles all required, default, and volatile fields.
        """
        versions = get_onex_versions()
        # Ensure entrypoint_type is EntrypointType
        if isinstance(entrypoint_type, str):
            entrypoint_type = EntrypointType(entrypoint_type)
        # Ensure meta_type is MetaType
        if meta_type is not None and isinstance(meta_type, str):
            meta_type = MetaType(meta_type)
        # Ensure lifecycle is Lifecycle
        lifecycle_val = (
            Lifecycle(lifecycle) if isinstance(lifecycle, str) else lifecycle
        )
        # last_modified_at and hash must never be None
        last_modified = last_modified_at_val or (
            now if now else datetime.datetime.utcnow().isoformat()
        )
        hash_val_final = hash_val or "0" * 64
        # --- NAMESPACE SANITIZATION LOGIC ---
        stem = path.stem
        sanitized_stem = re.sub(r"[^a-zA-Z0-9_.]", "_", stem)
        if not re.match(r"^[a-zA-Z]", sanitized_stem):
            sanitized_stem = f"_{sanitized_stem}"
        namespace = f"{namespace_prefix}.{sanitized_stem}"
        # --- END NAMESPACE SANITIZATION ---
        block = NodeMetadataBlock(
            metadata_version=versions["metadata_version"],
            protocol_version=versions["protocol_version"],
            owner=owner,
            copyright=copyright,
            schema_version=versions["schema_version"],
            name=path.name,
            version=version,
            uuid=uuid_val or str(uuid.uuid4()),
            author=author,
            created_at=created_at_val
            or (now if now else datetime.datetime.utcnow().isoformat()),
            last_modified_at=last_modified,
            description=description or "Stamped by ONEX",
            state_contract=state_contract,
            lifecycle=lifecycle_val,
            hash=hash_val_final,
            entrypoint=EntrypointBlock(type=entrypoint_type, target=path.name),
            runtime_language_hint=runtime_language_hint,
            namespace=namespace,
            meta_type=meta_type if meta_type is not None else MetaType.TOOL,
        )
        if extra_fields:
            for k, v in extra_fields.items():
                setattr(block, k, v)
        return block

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
