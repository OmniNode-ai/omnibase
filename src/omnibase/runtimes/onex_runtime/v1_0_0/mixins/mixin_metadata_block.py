import hashlib
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Tuple

import yaml

if TYPE_CHECKING:
    pass
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.metadata.metadata_constants import (
    METADATA_VERSION,
    SCHEMA_VERSION,
    get_namespace_prefix,
)
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.model.model_node_metadata import EntrypointBlock, Namespace
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.runtimes.onex_runtime.v1_0_0.utils.hash_utils import (
    compute_idempotency_hash,
    compute_metadata_hash_for_new_blocks,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.metadata_block_normalizer import (
    DELIMITERS,
)

_COMPONENT_NAME = Path(__file__).stem
_version_cache = None


def get_onex_versions() -> dict[str, Any]:
    global _version_cache
    if _version_cache is not None:
        if not isinstance(_version_cache, dict):
            raise OnexError(
                "_version_cache must be a dict", CoreErrorCode.INVALID_PARAMETER
            )
        return _version_cache
    cwd = Path(os.getcwd())
    search_dirs: list[Path] = [cwd]
    search_dirs += list(cwd.parents)
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
        prev_data = prev_block.model_dump() if prev_block else {}
        base_data = context_defaults.copy() if context_defaults else {}
        base_data.update(prev_data)
        sticky_fields = ["created_at", "uuid"]
        for field in sticky_fields:
            if prev_block is not None and hasattr(prev_block, field):
                updates[field] = getattr(prev_block, field)
            elif field in prev_data:
                updates.setdefault(field, prev_data[field])
        updates.setdefault("name", path.name)
        updates.setdefault("namespace", Namespace.from_path(path))
        entrypoint = updates.get("entrypoint", {})
        entrypoint_type = updates.get("entrypoint_type") or base_data.get(
            "entrypoint_type"
        )
        if not entrypoint_type:
            ext = path.suffix.lower().lstrip(".")
            from omnibase.model.model_node_metadata import Namespace

            entrypoint_type = Namespace.CANONICAL_SCHEME_MAP.get(ext, ext or "python")
        entrypoint_target = updates.get("entrypoint_target") or base_data.get(
            "entrypoint_target"
        )
        if not entrypoint_target:
            entrypoint_target = path.stem
        emit_log_event_sync(
            "DEBUG",
            f"[UPDATE_METADATA_BLOCK] entrypoint_type={entrypoint_type}, entrypoint_target={entrypoint_target}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )
        final_data = {**base_data, **updates}
        tools_val = None
        for src in (updates, base_data, prev_data):
            if "tools" in src and src["tools"] is not None:
                tools_val = src["tools"]
                break
        if tools_val is not None:
            final_data["tools"] = tools_val
        else:
            final_data.pop("tools", None)
        emit_log_event_sync(
            "DEBUG",
            f"[UPDATE_METADATA_BLOCK] tools field before model construction: {tools_val}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )
        filtered_data = {
            k: v
            for k, v in final_data.items()
            if v is not None and k not in ["name", "author", "namespace", "entrypoint"]
        }
        updates.pop("hash", None)
        if context_defaults:
            context_defaults.pop("hash", None)
        result = model_cls.create_with_defaults(
            name=updates.get("name", path.name),
            author=updates.get("author", "unknown"),
            namespace=updates.get("namespace", Namespace.from_path(path)),
            entrypoint_type=entrypoint_type,
            entrypoint_target=entrypoint_target,
            file_path=path,
            **filtered_data,
        )
        result.hash = "0" * 64
        return result

    def _normalize_filename_for_namespace(self, filename: str) -> str:
        """
        Normalize a filename for use in namespace generation.
        Removes leading dots, replaces dashes with underscores, and ensures valid characters.
        """
        import re

        normalized = filename.lstrip(".")
        normalized = re.sub("[^a-zA-Z0-9_]", "_", normalized)
        normalized = re.sub("_+", "_", normalized)
        normalized = normalized.strip("_")
        if not normalized:
            normalized = "file"
        return normalized

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
        emit_log_event_sync(
            "DEBUG",
            f"[IDEMPOTENCY] Enter stamp_with_idempotency for {path}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )
        try:
            try:
                prev_meta, rest = extract_block_fn(path, content)
                emit_log_event_sync(
                    "DEBUG",
                    f"[STAMP] original content: {repr(content)}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                emit_log_event_sync(
                    "DEBUG",
                    f"[STAMP] extracted rest: {repr(rest)}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                if not rest.strip():
                    raise RuntimeError(
                        f"[TEST DEBUG] Extracted rest is empty after extract_block_fn in test_spacing_after_block. Original content: {repr(content)}"
                    )
                emit_log_event_sync(
                    "DEBUG",
                    f"[IDEMPOTENCY] extract_block_fn returned for {path}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
            except Exception as e:
                emit_log_event_sync(
                    "ERROR",
                    f"[IDEMPOTENCY] extract_block_fn exception for {path}: {e}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                prev_meta, rest = None, content
            canonicalizer = model_cls.get_canonicalizer() if model_cls else lambda x: x
            if normalize_rest_fn:
                normalized_rest = normalize_rest_fn(rest)
            else:
                normalized_rest = canonicalizer(rest)
            volatile_fields = (
                list(model_cls.get_volatile_fields())
                if model_cls
                else ["hash", "last_modified_at"]
            )
            normalized_stem = self._normalize_filename_for_namespace(path.stem)
            updates = {
                "author": author,
                "entrypoint": EntrypointBlock(type=entrypoint_type, target=path.name),
                "namespace": Namespace.from_path(path),
                "meta_type": meta_type,
                "description": description,
            }
            emit_log_event_sync(
                "DEBUG",
                f"[STAMP_WITH_IDEMPOTENCY] entrypoint_target={path.name}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            if prev_meta is None:
                updates["created_at"] = (
                    self.get_file_creation_date(path)
                    or datetime.now(timezone.utc).isoformat()
                )
                updates["last_modified_at"] = datetime.now(timezone.utc).isoformat()
                new_block = self.update_metadata_block(
                    prev_meta, updates, path, model_cls, context_defaults
                )
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
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    f"[IDEMPOTENCY] stored_hash={stored_hash[:16]}..., computed_hash={computed_hash[:16]}..., content_changed={content_changed}, is_placeholder={is_placeholder_hash}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                if not content_changed and not is_placeholder_hash:
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
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"[END] stamp_with_idempotency for {path} (idempotent)",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
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
                    updates["last_modified_at"] = datetime.now(timezone.utc).isoformat()
                    updated_block = self.update_metadata_block(
                        prev_meta, updates, path, model_cls, context_defaults
                    )
                    updated_hash = compute_idempotency_hash(
                        metadata_model=updated_block,
                        body=normalized_rest,
                        volatile_fields=volatile_fields,
                        metadata_serializer=serialize_block_fn,
                        body_canonicalizer=canonicalizer,
                    )
                    updated_block.hash = updated_hash
                    final_block = updated_block
            emit_log_event_sync(
                "DEBUG",
                f"[IDEMPOTENCY] About to serialize final_block for {path}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            block_str = serialize_block_fn(final_block)
            emit_log_event_sync(
                "DEBUG",
                f"[IDEMPOTENCY] Serialized block for {path}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            if normalized_rest:
                print(f"[DEBUG] normalized_rest: {repr(normalized_rest)}")
                rest_stripped = normalized_rest.lstrip("\n")
                print(f"[DEBUG] rest_stripped: {repr(rest_stripped)}")
                block_str = block_str.rstrip()
                code_body = rest_stripped.lstrip()
                if code_body:
                    new_content = f"{block_str}\n\n{code_body}"
                else:
                    new_content = f"{block_str}\n\n"
            else:
                new_content = block_str + "\n\n"
            new_content = new_content.rstrip() + "\n"
            print(f"[DEBUG] new_content: {repr(new_content)}")
            emit_log_event_sync(
                "DEBUG",
                f"[IDEMPOTENCY] Exit stamp_with_idempotency for {path}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
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
            emit_log_event_sync(
                "ERROR",
                f"[IDEMPOTENCY] Exception in stamp_with_idempotency for {path}: {e}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            from omnibase.model.model_onex_message_result import (
                OnexMessageModel,
                OnexStatus,
            )

            return content, self.handle_result(
                status=OnexStatus.ERROR,
                path=path,
                messages=[OnexMessageModel(summary=f"Error stamping file: {str(e)}")],
                metadata={"note": f"Error: {str(e)}", "content": content},
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
        canonical_fields = model_cls.model_fields
        block_dict = block.model_dump() if hasattr(block, "model_dump") else dict(block)
        extra_fields = set(block_dict.keys()) - set(canonical_fields.keys())
        if extra_fields:
            reasons.append(f"Extra fields: {sorted(extra_fields)}")
        missing_fields = set(canonical_fields.keys()) - set(block_dict.keys())
        if missing_fields:
            reasons.append(f"Missing fields: {sorted(missing_fields)}")
        for k, v in block_dict.items():
            if k in canonical_fields:
                expected_type = canonical_fields[k].annotation
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
                if v is not None and not MetadataBlockMixin._is_instance_of_type(
                    v, expected_type
                ):
                    reasons.append(
                        f"Field '{k}' has wrong type: {type(v).__name__} (expected {expected_type})"
                    )
        return len(reasons) == 0, reasons

    @staticmethod
    def _is_instance_of_type(value: Any, typ: Any) -> bool:
        import typing

        origin = getattr(typ, "__origin__", None)
        if origin is typing.Union:
            return any(
                MetadataBlockMixin._is_instance_of_type(value, t) for t in typ.__args__
            )
        if origin is not None:
            if origin in (list, tuple, set):
                return isinstance(value, origin)
            if origin is dict:
                return isinstance(value, dict)
            return False
        import enum

        if isinstance(typ, type) and issubclass(typ, enum.Enum):
            return isinstance(value, typ) or isinstance(value, str)
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
                ts = stat.st_birthtime
            else:
                ts = stat.st_ctime
            return datetime.fromtimestamp(ts).isoformat()
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Error getting file creation date for {path}: {e}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            return None

    @staticmethod
    def remove_all_metadata_blocks(content: str, filetype: str) -> str:
        """
        Remove all metadata blocks for the given filetype using protocol delimiters.
        Uses the same delimiter logic as the canonical normalizer.
        """
        import re

        open_delim, close_delim = DELIMITERS.get(filetype, (None, None))
        if not open_delim or not close_delim:
            return content
        block_pattern = f"{re.escape(open_delim)}[\\s\\S]+?{re.escape(close_delim)}\\n*"
        return re.sub(block_pattern, "", content, flags=re.MULTILINE)
