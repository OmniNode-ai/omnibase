import datetime
import uuid
from pathlib import Path
from typing import Any, Optional, Tuple

from omnibase.metadata.metadata_constants import METADATA_VERSION, SCHEMA_VERSION
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.utils.metadata_utils import canonicalize_for_hash, compute_canonical_hash


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
            name=path.stem,
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
        return block

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
        print(f"[DEBUG] stamp_with_idempotency called with now={now}")
        messages: list = []
        prev_meta, rest = extract_block_fn(path, content)
        prev_uuid, prev_created_at, prev_hash = self.extract_preserved_fields(prev_meta)
        prev_last_modified = (
            getattr(prev_meta, "last_modified_at", None) if prev_meta else None
        )
        # Use canonicalizer from model
        canonicalizer = model_cls.get_canonicalizer() if model_cls else (lambda x: x)
        normalized_rest = canonicalizer(rest)
        # Get volatile fields from model
        volatile_fields = (
            list(model_cls.get_volatile_fields())
            if model_cls
            else ["hash", "last_modified_at"]
        )
        # Prepare previous canonicalized content (with volatile fields placeholdered)
        if prev_meta is not None and isinstance(prev_meta, dict):
            print(
                "[DEBUG] Converting prev_meta from dict to NodeMetadataBlock before model_dump (per typing_and_protocols rule)"
            )
            prev_meta = model_cls(**prev_meta)
        print(f"[DEBUG] prev_meta type before model_dump: {type(prev_meta)}")
        prev_meta_dict = prev_meta.model_dump() if prev_meta else {}
        prev_full_content_for_hash = canonicalize_for_hash(
            prev_meta_dict,
            normalized_rest,
            volatile_fields=volatile_fields,
            metadata_serializer=serialize_block_fn,
            body_canonicalizer=canonicalizer,
        )
        # Prepare new canonicalized content (with volatile fields placeholdered), using previous last_modified_at for comparison
        print(f"[DEBUG] Using now={now} for new block construction (comparison phase)")
        new_block_for_compare = self.build_metadata_block(
            path=path,
            now=(
                prev_last_modified if prev_last_modified else now
            ),  # Use previous last_modified_at for comparison
            author=author,
            entrypoint_type=entrypoint_type,
            namespace_prefix=namespace_prefix,
            meta_type=meta_type,
            description=description,
            uuid_val=prev_uuid,
            created_at_val=prev_created_at,
            last_modified_at_val=prev_last_modified,
        )
        if new_block_for_compare is not None and isinstance(
            new_block_for_compare, dict
        ):
            print(
                "[DEBUG] Converting new_block_for_compare from dict to NodeMetadataBlock before model_dump (per typing_and_protocols rule)"
            )
            new_block_for_compare = model_cls(**new_block_for_compare)
        print(
            f"[DEBUG] new_block_for_compare type before model_dump: {type(new_block_for_compare)}"
        )
        new_block_for_compare_dict = new_block_for_compare.model_dump()
        new_full_content_for_hash = canonicalize_for_hash(
            new_block_for_compare_dict,
            normalized_rest,
            volatile_fields=volatile_fields,
            metadata_serializer=serialize_block_fn,
            body_canonicalizer=canonicalizer,
        )
        print("[DEBUG] prev_full_content_for_hash:")
        print(prev_full_content_for_hash)
        print("[DEBUG] new_full_content_for_hash:")
        print(new_full_content_for_hash)
        print(
            f"[DEBUG] prev_last_modified: {prev_last_modified}, prev_hash: {prev_hash}"
        )
        print(
            f"[DEBUG] Equality check: {prev_full_content_for_hash == new_full_content_for_hash}"
        )
        if prev_meta and prev_full_content_for_hash == new_full_content_for_hash:
            # Idempotent: preserve previous last_modified_at and hash in the output block
            output_block = prev_meta.model_copy(
                update={"hash": prev_hash, "last_modified_at": prev_last_modified}
            )
            block_str = serialize_block_fn(output_block)
            new_content = (
                f"{block_str}\n\n{normalized_rest}" if normalized_rest else block_str
            )
            print(f"[DEBUG] Idempotent: returning previous block.\n{block_str}")
            return new_content, self.handle_result(
                status="success",
                path=path,
                messages=[],
                metadata={
                    "note": "Idempotent: no changes needed",
                    "hash": prev_hash,
                    "last_modified_at": prev_last_modified,
                    "content": new_content,
                },
            )
        # Not idempotent: update last_modified_at and hash using now
        print(
            f"[DEBUG] Using now={now} for new block construction (not idempotent branch)"
        )
        new_block = self.build_metadata_block(
            path=path,
            now=now,
            author=author,
            entrypoint_type=entrypoint_type,
            namespace_prefix=namespace_prefix,
            meta_type=meta_type,
            description=description,
            uuid_val=prev_uuid,
            created_at_val=prev_created_at,
            last_modified_at_val=now,  # Only set to now because content is different
        )
        if new_block is not None and isinstance(new_block, dict):
            print(
                "[DEBUG] Converting new_block from dict to NodeMetadataBlock before model_dump (per typing_and_protocols rule)"
            )
            new_block = model_cls(**new_block)
        print(f"[DEBUG] new_block type before model_dump: {type(new_block)}")
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
        new_content = (
            f"{block_str}\n\n{normalized_rest}" if normalized_rest else block_str
        )
        print(f"[DEBUG] Not idempotent: returning new block.\n{block_str}")
        return new_content, self.handle_result(
            status="success",
            path=path,
            messages=messages,
            metadata={
                "note": "Stamped with idempotency",
                "hash": computed_hash,
                "content": new_content,
            },
        )

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
        protocol_version: str = SCHEMA_VERSION,
        schema_version: str = SCHEMA_VERSION,
        runtime_language_hint: str = "python>=3.11",
        state_contract: str = "state_contract://default",
        lifecycle: str = "active",
        extra_fields: Optional[dict] = None,
    ) -> NodeMetadataBlock:
        """
        Centralized construction of NodeMetadataBlock for all handlers.
        Handles all required, default, and volatile fields.
        """
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
        block = NodeMetadataBlock(
            metadata_version=METADATA_VERSION,
            protocol_version=protocol_version,
            owner=owner,
            copyright=copyright,
            schema_version=schema_version,
            name=path.stem,
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
            namespace=f"{namespace_prefix}.{path.stem}",
            meta_type=meta_type if meta_type is not None else MetaType.TOOL,
        )
        if extra_fields:
            for k, v in extra_fields.items():
                setattr(block, k, v)
        return block
