# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 2b01097f-0b5d-4f1b-bfa4-52ba39b5a9a0
# name: stamping_engine.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:02.925697
# last_modified_at: 2025-05-19T16:20:02.925700
# description: Stamped Python file: stamping_engine.py
# state_contract: none
# lifecycle: active
# hash: 7d38ac87b17d68b9a7ac7b0243d6667ac4bffc851dabc97f9b0716a680437dfb
# entrypoint: {'type': 'python', 'target': 'stamping_engine.py'}
# namespace: onex.stamped.stamping_engine.py
# meta_type: tool
# === /OmniNode:Metadata ===

import datetime
from pathlib import Path

from omnibase.canonical.canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_onex_message import LogLevelEnum, OnexMessageModel
from omnibase.model.model_onex_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


def stamp_file(
    path: Path, content: str, handler: ProtocolFileTypeHandler
) -> OnexResultModel:
    """
    Canonical stamping pipeline for all file types.
    - Extracts metadata block and body using the handler
    - Parses the block (using canonical utility)
    - Computes canonical hash and checks for idempotency
    - Updates last_modified_at and hash if dirty
    - Calls the handler to serialize the block and reassemble the file
    - Returns a protocol-compliant OnexResultModel
    """
    messages = []
    serializer = CanonicalYAMLSerializer()
    try:
        # 0. Normalize block placement and file structure
        # Normalization is handled by the engine, not the handler
        # 1. Extract block and body
        meta_block_str, body = handler.extract_block(path, content)
        body = serializer.normalize_body(body)
        prev_meta = None
        if meta_block_str:
            try:
                # Use canonical model's YAML block extraction and loading method
                prev_meta = NodeMetadataBlock.from_file_or_content(
                    meta_block_str, already_extracted_block=meta_block_str
                )
            except Exception as e:
                messages.append(
                    OnexMessageModel(
                        summary=f"Malformed metadata block: {e}",
                        level=LogLevelEnum.ERROR,
                    )
                )
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    target=str(path),
                    messages=messages,
                    metadata={"note": "Malformed metadata block", "error": str(e)},
                    auto_fix_applied=False,
                    failed_files=[str(path)],
                )
        now = datetime.datetime.utcnow().isoformat()
        if prev_meta is None:
            # Block construction is handled by the engine, not the handler
            from omnibase.model.model_node_metadata import (
                EntrypointBlock,
                EntrypointType,
                Lifecycle,
                MetaType,
            )

            meta_model = NodeMetadataBlock(
                metadata_version="0.1.0",
                protocol_version="1.0.0",
                owner="OmniNode Team",
                copyright="OmniNode Team",
                schema_version="1.1.0",
                name=path.stem,
                version="1.0.0",
                uuid="00000000-0000-0000-0000-000000000000",
                author="OmniNode Team",
                created_at=now,
                last_modified_at=now,
                description="Stamped by stamping_engine",
                state_contract="state_contract://default",
                lifecycle=Lifecycle.ACTIVE,
                hash="0" * 64,
                entrypoint=EntrypointBlock(
                    type=EntrypointType.PYTHON, target=path.name
                ),
                runtime_language_hint="python>=3.11",
                namespace=f"onex.stamped.{path.stem}",
                meta_type=MetaType.TOOL,
            )
            hash_val = serializer.canonicalize_for_hash(
                meta_model, body, comment_prefix="# "
            )
            meta_model.hash = hash_val
            meta_model.last_modified_at = now
        else:
            hash_val = serializer.canonicalize_for_hash(
                prev_meta, body, comment_prefix="# "
            )
            if hash_val == prev_meta.hash:
                meta_model = prev_meta
            else:
                meta_model = prev_meta.model_copy()
                meta_model.last_modified_at = now
                meta_model.hash = hash_val
        block = handler.serialize_block(meta_model)
        if body.strip():
            stamped = block.rstrip("\n") + "\n\n" + body.lstrip("\n")
        else:
            stamped = block.rstrip("\n") + "\n"
        if not stamped.endswith("\n"):
            stamped += "\n"
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=messages,
            metadata={
                "note": "Stamped file",
                "hash": meta_model.hash,
                "content": stamped,
            },
            diff=None,
            auto_fix_applied=True,
            fixed_files=[str(path)],
        )
    except Exception as e:
        messages.append(
            OnexMessageModel(summary=f"Stamping failed: {e}", level=LogLevelEnum.ERROR)
        )
        return OnexResultModel(
            status=OnexStatus.ERROR,
            target=str(path),
            messages=messages,
            metadata={"note": "Stamping failed", "error": str(e)},
            auto_fix_applied=False,
            failed_files=[str(path)],
        )
