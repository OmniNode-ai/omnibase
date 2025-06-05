# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T08:19:40.214329'
# description: Stamped by PythonHandler
# entrypoint: python://model_node_metadata
# hash: c3b5781a99c5e5c292687d7d048e46ec8bf0c5f699a664327a33bb6f39867612
# last_modified_at: '2025-05-29T14:13:58.833046+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_node_metadata.py
# namespace: python://omnibase.model.model_node_metadata
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e2fc1037-9f90-45d2-a14b-be759abddd39
# version: 1.0.0
# === /OmniNode:Metadata ===


#
# NOTE: The `metadata_version` field is the single source of versioning for both schema and canonicalization logic.
# Any change to the schema (fields, types, required/optional status) OR to the canonicalization logic (how the body or metadata is normalized for hashing/idempotency)
# MUST increment `metadata_version`. This ensures hashes and idempotency logic remain valid and comparable across versions.
#
# If you change how the hash is computed, how fields are normalized, or the structure of the metadata block, bump `metadata_version`.
#
# This policy is enforced for all ONEX metadata blocks.

import enum
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    List,
    Optional,
    Type,
    Union,
)

import yaml  # Add this import if not present
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    StringConstraints,
    field_validator,
    model_validator,
    validator,
)

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import EntrypointType, FunctionLanguageEnum, Lifecycle, MetaTypeEnum
from omnibase.enums.metadata import ToolTypeEnum
from omnibase.metadata.metadata_constants import (
    MD_META_CLOSE,
    MD_META_OPEN,
    METADATA_VERSION,
    PY_META_CLOSE,
    PY_META_OPEN,
    SCHEMA_VERSION,
    YAML_META_CLOSE,
    YAML_META_OPEN,
    get_namespace_prefix,
)
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.mixin.mixin_hash_computation import HashComputationMixin
from omnibase.mixin.mixin_yaml_serialization import YAMLSerializationMixin
from omnibase.model.model_entrypoint import EntrypointBlock
from omnibase.model.model_function_tool import FunctionTool
from omnibase.model.model_project_metadata import (
    get_canonical_namespace_prefix,
    get_canonical_versions,
)
from omnibase.model.model_tool_collection import ToolCollection

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class DataClassification(enum.StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class LogFormat(enum.StrEnum):
    JSON = "json"
    TEXT = "text"
    KEY_VALUE = "key-value"
    MARKDOWN = "markdown"
    YAML = "yaml"
    CSV = "csv"


class Architecture(enum.StrEnum):
    AMD64 = "amd64"
    ARM64 = "arm64"
    PPC64LE = "ppc64le"


class IOBlock(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    schema_ref: Annotated[str, StringConstraints(min_length=1)]
    required: Optional[bool] = True
    format_hint: Optional[str] = None
    description: Optional[Annotated[str, StringConstraints(min_length=1)]] = None


class IOContract(BaseModel):
    inputs: List[IOBlock]
    outputs: List[IOBlock]


class SignatureContract(BaseModel):
    function_name: str
    parameters: List[IOBlock]
    return_type: str
    raises: List[str] = []


class StateContractBlock(BaseModel):
    preconditions: List[IOBlock]
    postconditions: List[IOBlock]
    transitions: Optional[List[IOBlock]] = None


class TrustScoreStub(BaseModel):
    runs: int = Field(..., description="Number of runs")
    failures: int = Field(..., description="Number of failures")
    trust_score: Optional[float] = Field(None, description="Trust score (optional)")


class DependencyBlock(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    type: Annotated[str, StringConstraints(min_length=1)]
    target: Annotated[str, StringConstraints(min_length=1)]
    binding: Optional[str] = None
    protocol_required: Optional[str] = None
    optional: Optional[bool] = False
    description: Optional[Annotated[str, StringConstraints(min_length=1)]] = None


class LoggingConfig(BaseModel):
    level: Optional[str] = None
    format: Optional[LogFormat] = None
    audit_events: List[str] = Field(default_factory=list)


class SourceRepository(BaseModel):
    url: Optional[str] = None
    commit_hash: Optional[
        Annotated[str, StringConstraints(pattern=r"^[a-fA-F0-9]{40}$")]
    ] = None
    path: Optional[str] = None

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[Any], Any]]:
        yield cls._debug_commit_hash

    @staticmethod
    def _debug_commit_hash(value: Any) -> Any:
        if value is not None:
            value = value.strip() if isinstance(value, str) else value
        return value


class TestingBlock(BaseModel):
    canonical_test_case_ids: List[str] = Field(default_factory=list)
    required_ci_tiers: List[str] = Field(default_factory=list)
    minimum_coverage_percentage: Optional[float] = None


class SignatureBlock(BaseModel):
    signature: Optional[str] = None
    algorithm: Optional[str] = None
    signed_by: Optional[str] = None
    issued_at: Optional[str] = None


class Namespace(BaseModel):
    """
    Canonical ONEX namespace type. Handles normalization, validation, and construction from file paths.
    Always enforces the canonical prefix from project.onex.yaml.
    Pattern: <filetype>://<prefix>.<subdirs>.<stem> (filetype is the extension, e.g., python, yaml, json, md)
    Serializes as a single-line URI string, never as a mapping.
    """

    value: str

    CANONICAL_SCHEME_MAP: ClassVar[dict[str, str]] = {
        "py": "python",
        "python": "python",
        "md": "markdown",
        "markdown": "markdown",
        "yml": "yaml",
        "yaml": "yaml",
        "json": "json",
        "cli": "cli",
        "docker": "docker",
    }

    @classmethod
    def normalize_scheme(cls, scheme: str) -> str:
        return cls.CANONICAL_SCHEME_MAP.get(scheme.lower(), scheme.lower())

    @classmethod
    def from_path(cls, path: "Path") -> "Namespace":
        from omnibase.model.model_project_metadata import get_canonical_namespace_prefix

        # Always use Path for safety
        if not hasattr(path, "parts"):
            from pathlib import Path as _Path

            path = _Path(path)
        stem = path.stem
        raw_ext = path.suffix[1:] if path.suffix.startswith(".") else path.suffix
        # Canonical extension mapping
        ext_map = {
            "py": "python",
            "md": "markdown",
            "markdown": "markdown",
            "yaml": "yaml",
            "yml": "yaml",
            "log": "log",
            "txt": "text",
        }
        ext = ext_map.get(raw_ext.lower(), raw_ext.lower() or "file")
        parts = list(path.parts)
        # Remove any leading '.' from parts
        if parts and parts[0] == ".":
            parts = parts[1:]
        canonical_prefix = get_canonical_namespace_prefix()
        # Find the canonical prefix in the path and slice from there
        if canonical_prefix in parts:
            idx = parts.index(canonical_prefix)
            ns_parts = parts[idx:]
        else:
            ns_parts = parts
        # Remove any leading '.' from ns_parts again (paranoia)
        if ns_parts and ns_parts[0].startswith("."):
            ns_parts[0] = ns_parts[0].lstrip(".")
        # For all files, include the extension in the last segment for uniqueness, unless already present
        if ext and ext != "python":
            if not ns_parts[-1].endswith(f"_{ext}"):
                # Remove extension from last part if present
                if ns_parts[-1].endswith(f".{raw_ext}"):
                    ns_parts[-1] = ns_parts[-1][: -(len(raw_ext) + 1)]
                ns_parts[-1] = f"{ns_parts[-1]}_{ext}"
        else:
            # For python files, strip the extension
            if raw_ext and ns_parts[-1].endswith(f".{raw_ext}"):
                ns_parts[-1] = ns_parts[-1][: -(len(raw_ext) + 1)]
        # Remove any accidental double dots
        ns = f"{ext}://{'.'.join(ns_parts)}"
        return cls(value=ns)

    def to_serializable_dict(self) -> str:
        return self.value

    def __str__(self):
        return self.value

    def model_dump(self, *args, **kwargs):
        # Always dump as a string for YAML/JSON
        return self.value

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # Ensure schema is string, not object
        return {"type": "string"}


class DataHandlingDeclaration(BaseModel):
    processes_sensitive_data: bool
    data_residency_required: Optional[str] = None
    data_classification: Optional[DataClassification] = None


class ExtensionValueModel(BaseModel):
    """
    Strongly typed model for extension values in x_extensions.
    Accepts any type for value (str, int, float, bool, dict, list, etc.) for protocol and legacy compatibility.
    """

    value: Optional[Any] = None
    description: Optional[str] = None
    # Add more fields as needed for extension use cases

    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}


class NodeMetadataBlock(YAMLSerializationMixin, HashComputationMixin, BaseModel):
    """
    Canonical ONEX node metadata block (see onex_node.yaml and node_contracts.md).
    Entrypoint must be a URI: <type>://<target>
    Example: 'python://main.py', 'cli://script.sh', 'docker://image', 'markdown://log.md'
    """

    metadata_version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ] = Field(default="0.1.0")
    protocol_version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ] = Field(default="1.1.0")
    owner: Annotated[str, StringConstraints(min_length=1)] = Field(
        default="OmniNode Team"
    )
    copyright: Annotated[str, StringConstraints(min_length=1)] = Field(
        default="OmniNode Team"
    )
    schema_version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ] = Field(default="1.1.0")
    name: Annotated[str, StringConstraints(min_length=1)]
    version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ] = Field(default="1.0.0")
    uuid: Annotated[
        str,
        StringConstraints(
            pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        ),
    ]
    author: Annotated[str, StringConstraints(min_length=1)]
    created_at: Annotated[str, StringConstraints(min_length=1)]
    last_modified_at: Annotated[str, StringConstraints(min_length=1)] = Field(
        json_schema_extra={"volatile": True}
    )
    description: Annotated[str, StringConstraints(min_length=1)] = Field(
        default="Stamped by ONEX"
    )
    state_contract: Annotated[str, StringConstraints(min_length=1)] = Field(
        default="state_contract://default"
    )
    lifecycle: Lifecycle = Field(default=Lifecycle.ACTIVE)
    hash: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^[a-fA-F0-9]{64}$")
    ] = Field(json_schema_extra={"volatile": True})
    entrypoint: EntrypointBlock
    runtime_language_hint: Optional[str] = None
    namespace: Namespace = Field(
        ..., description="Namespace, e.g., <prefix>.tools.<name>"
    )
    meta_type: MetaTypeEnum = Field(default=MetaTypeEnum.TOOL)
    trust_score: Optional[float] = None
    tags: Optional[list[str]] = None
    capabilities: Optional[list[str]] = None
    protocols_supported: Optional[list[str]] = None
    base_class: Optional[list[str]] = None
    dependencies: Optional[List[DependencyBlock]] = None
    inputs: Optional[list[IOBlock]] = None
    outputs: Optional[list[IOBlock]] = None
    environment: Optional[list[str]] = None
    license: Optional[str] = None
    signature_block: Optional[SignatureBlock] = None
    x_extensions: Dict[str, ExtensionValueModel] = Field(default_factory=dict)
    testing: Optional[TestingBlock] = None
    os_requirements: Optional[list[str]] = None
    architectures: Optional[list[str]] = None
    container_image_reference: Optional[str] = None
    compliance_profiles: List[str] = Field(default_factory=list)
    data_handling_declaration: Optional[DataHandlingDeclaration] = None
    logging_config: Optional[LoggingConfig] = None
    source_repository: Optional[SourceRepository] = None
    contracts: Optional[dict] = None
    scenarios: Optional[list[str]] = None
    scenario_test_entrypoint: Optional[str] = Field(
        default=None,
        description="Entrypoint for scenario-based test harness; e.g., 'python -m ...' or CLI command."
    )

    # Function tools support - unified tools approach
    tools: Optional[ToolCollection] = Field(
        default=None,
        description="Function tools within this file (unified tools approach). This is a ToolCollection, not a dict.",
    )

    RUNTIME_LANGUAGE_HINT_MAP: ClassVar[dict[str, str]] = {
        "python": "python>=3.11",
        "typescript": "typescript>=4.0",
        "javascript": "javascript>=ES2020",
        "html": "html5",
        # Add more as needed
    }

    model_config = {"arbitrary_types_allowed": True}

    # Canonicalization/canonicalizer policy (not Pydantic config)
    canonicalization_policy: ClassVar[dict[str, Any]] = {
        "canonicalize_body": staticmethod(
            lambda body: CanonicalYAMLSerializer().normalize_body(body)
        )
    }

    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def from_file_or_content(
        cls, content: str, already_extracted_block: Optional[str] = None, event_bus=None
    ) -> "NodeMetadataBlock":
        block_yaml = already_extracted_block or content
        data = yaml.safe_load(block_yaml)
        return cls(**data)

    @classmethod
    def get_volatile_fields(cls) -> list[str]:
        model_fields = getattr(cls, "model_fields", {})
        if isinstance(model_fields, dict):
            return [
                name
                for name, field in model_fields.items()
                if getattr(field, "json_schema_extra", None)
                and field.json_schema_extra.get("volatile")
            ]
        return []

    @classmethod
    def get_canonicalizer(cls) -> Any:
        policy = cls.canonicalization_policy
        if isinstance(policy, dict):
            return policy.get("canonicalize_body", None)
        return None

    def some_function(self) -> None:
        # implementation
        pass

    def another_function(self) -> None:
        # implementation
        pass

    def to_serializable_dict(
        self, use_compact_entrypoint: bool = True
    ) -> dict[str, Any]:
        """
        Canonical serialization for ONEX metadata block:
        - Omit all optional fields if their value is '', None, { }, or [] (except protocol-required fields).
        - Always emit canonical values for protocol_version, schema_version, and metadata_version.
        - Never emit empty string or null for any field unless protocol requires it.
        - Entrypoint and namespace are always emitted as single-line URI strings.
        """

        def serialize_value(val: Any) -> Any:
            if hasattr(val, "to_serializable_dict"):
                return val.to_serializable_dict()
            elif isinstance(val, enum.Enum):
                return val.value
            elif isinstance(val, list):
                return [serialize_value(v) for v in val]
            elif isinstance(val, dict):
                return {k: serialize_value(v) for k, v in val.items()}
            else:
                return val

        canonical_versions = get_canonical_versions()
        PROTOCOL_REQUIRED_FIELDS = {"tools"}

        d = {}
        for k in self.__class__.model_fields:
            if k == "metadata_version":
                d[k] = canonical_versions.metadata_version
                continue
            if k == "protocol_version":
                d[k] = canonical_versions.protocol_version
                continue
            if k == "schema_version":
                d[k] = canonical_versions.schema_version
                continue
            v = getattr(self, k)
            # Omit if optional and value is '', None, {}, or [] (unless protocol-required)
            if (
                v == "" or v is None or v == {} or v == []
            ) and k not in PROTOCOL_REQUIRED_FIELDS:
                continue
            # Entrypoint as URI string (always)
            if k == "entrypoint" and isinstance(v, EntrypointBlock):
                d[k] = v.to_uri()
                continue
            # Namespace as URI string (always)
            if k == "namespace" and isinstance(v, Namespace):
                d[k] = str(v)
                continue
            # PATCH: Omit tools if None, empty dict, or empty ToolCollection (protocol rule)
            if k == "tools":
                if v is None:
                    continue
                if isinstance(v, dict) and not v:
                    continue
                if hasattr(v, "root") and not v.root:
                    continue
            d[k] = serialize_value(v)
        # PATCH: Remove all None/null/empty fields after dict construction
        d = {k: v for k, v in d.items() if v not in (None, "", [], {})}
        return d

    @classmethod
    def from_serializable_dict(
        cls: Type["NodeMetadataBlock"], data: dict[str, Any]
    ) -> "NodeMetadataBlock":
        # Handle entrypoint deserialization
        if "entrypoint" in data:
            if isinstance(data["entrypoint"], str):
                data["entrypoint"] = EntrypointBlock(
                    type=data["entrypoint"].split("://")[0],
                    target=data["entrypoint"].split("://")[1],
                )
            elif isinstance(data["entrypoint"], dict):
                data["entrypoint"] = EntrypointBlock(**data["entrypoint"])
        # Handle tools deserialization
        if "tools" in data and isinstance(data["tools"], dict):
            tools_dict = {}
            for tool_name, tool_data in data["tools"].items():
                if isinstance(tool_data, dict):
                    tools_dict[tool_name] = FunctionTool.from_serializable_dict(
                        tool_data
                    )
                else:
                    tools_dict[tool_name] = tool_data
            data["tools"] = ToolCollection.from_dict(tools_dict)
        return cls(**data)

    @classmethod
    def create_with_defaults(
        cls,
        name: Optional[str] = None,
        author: Optional[str] = None,
        namespace: Optional[Namespace] = None,
        entrypoint_type: Optional[str] = None,
        entrypoint_target: Optional[str] = None,
        file_path: Optional["Path"] = None,
        runtime_language_hint: Optional[str] = None,
        **additional_fields: Any,
    ) -> "NodeMetadataBlock":
        """
        Create a complete NodeMetadataBlock with sensible defaults for all required fields.
        PROTOCOL: entrypoint_type and entrypoint_target must be used as provided, for all file types. entrypoint_target must always be the filename stem (no extension).

        # === CRITICAL INVARIANT: UUID and CREATED_AT IDEMPOTENCY ===
        # These fields MUST be preserved if present (not None) in additional_fields.
        # Regression (May 2025): Logic previously always generated new values, breaking protocol idempotency.
        # See test_stamp_idempotency in test_node.py and standards doc for rationale.
        # DO NOT REMOVE THIS CHECK: Any change here must be justified in PR and reviewed by maintainers.
        """
        import re
        from datetime import datetime
        from uuid import uuid4

        now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        canonical_versions = get_canonical_versions()
        canonical_namespace = None
        ep_type = entrypoint_type or None
        ep_target = entrypoint_target
        # Infer entrypoint_type from file extension if not provided
        if file_path is not None and not ep_type:
            ext = file_path.suffix.lower().lstrip(".")
            ep_type = Namespace.CANONICAL_SCHEME_MAP.get(ext, ext)
        # Always use the filename stem (no extension) for entrypoint_target
        if file_path is not None and not ep_target:
            ep_target = file_path.stem
        elif ep_target:
            import os

            ep_target = Path(ep_target).stem
        else:
            ep_target = "main"
        # Set runtime_language_hint only for code files
        if runtime_language_hint is None:
            code_types = {"python", "typescript", "javascript", "html"}
            if ep_type in code_types:
                runtime_language_hint = cls.RUNTIME_LANGUAGE_HINT_MAP.get(ep_type, None)
            else:
                runtime_language_hint = None
        if file_path is not None:
            canonical_namespace = Namespace.from_path(file_path)
        # Entrypoint construction: always use provided type/target (target is stem)
        entrypoint = EntrypointBlock(type=ep_type, target=ep_target)
        data: Dict[str, Any] = {
            "name": name or (file_path.stem if file_path is not None else "unknown"),
            "uuid": (
                additional_fields["uuid"]
                if "uuid" in additional_fields and additional_fields["uuid"] is not None
                else str(uuid4())
            ),
            "author": author or "unknown",
            "created_at": (
                additional_fields["created_at"]
                if "created_at" in additional_fields
                and additional_fields["created_at"] is not None
                else now
            ),
            "last_modified_at": now,
            "hash": "0" * 64,
            "entrypoint": entrypoint,
            "namespace": namespace
            or canonical_namespace
            or Namespace(value=f"{get_namespace_prefix()}.unknown"),
            "metadata_version": canonical_versions.metadata_version,
            "protocol_version": canonical_versions.protocol_version,
            "schema_version": canonical_versions.schema_version,
        }
        if runtime_language_hint is not None:
            data["runtime_language_hint"] = runtime_language_hint
        for vfield in ("metadata_version", "protocol_version", "schema_version"):
            if vfield in additional_fields:
                del additional_fields[vfield]
        # PATCH: Always pass tools if present in additional_fields
        tools = additional_fields.pop("tools", None)
        if tools is not None:
            # Omit tools if empty dict or empty ToolCollection
            if (isinstance(tools, dict) and not tools) or (
                hasattr(tools, "root") and not tools.root
            ):
                tools = None
            else:
                print(
                    f"[TRACE] create_with_defaults: tools field present, type: {type(tools)}"
                )
            if tools is not None:
                data["tools"] = tools
        data.update(additional_fields)
        return cls(**data)  # type: ignore[arg-type]

    @field_validator("entrypoint", mode="before")
    @classmethod
    def validate_entrypoint(cls, value):
        from omnibase.model.model_node_metadata import EntrypointBlock

        if isinstance(value, EntrypointBlock):
            return value
        if isinstance(value, str):
            # Accept URI string and convert to EntrypointBlock
            return EntrypointBlock.from_uri(value)
        raise ValueError("entrypoint must be an EntrypointBlock instance or URI string")

    @field_validator("namespace", mode="before")
    @classmethod
    def validate_namespace_field(cls, value):
        # Recursively flatten any dict or Namespace to a plain string
        def flatten_namespace(val):
            if isinstance(val, Namespace):
                return val.value
            if isinstance(val, str):
                # Normalize scheme if present
                if "://" in val:
                    scheme, rest = val.split("://", 1)
                    scheme = Namespace.normalize_scheme(scheme)
                    return f"{scheme}://{rest}"
                return val
            if isinstance(val, dict) and "value" in val:
                return flatten_namespace(val["value"])
            return str(val)

        return Namespace(value=flatten_namespace(value))

    @field_validator("x_extensions", mode="before")
    @classmethod
    def coerce_x_extensions(cls, v):
        if not isinstance(v, dict):
            return v
        out = {}
        for k, val in v.items():
            if isinstance(val, ExtensionValueModel):
                out[k] = val
            elif isinstance(val, dict):
                out[k] = ExtensionValueModel(**val)
            else:
                out[k] = ExtensionValueModel(value=val)
        return out

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        d["entrypoint"] = self.entrypoint.to_uri()
        return d


# NOTE: The only difference between model_dump() and __dict__ is that model_dump() serializes entrypoint as a dict, while __dict__ keeps it as an EntrypointBlock object. This is expected and not a source of non-determinism for YAML serialization, which uses model_dump or to_serializable_dict.


def debug_compare_model_dump_vs_dict(model):
    import difflib
    import pprint

    dump = model.model_dump()
    dct = {k: v for k, v in model.__dict__.items() if not k.startswith("_")}
    dump_str = pprint.pformat(dump, width=120, sort_dicts=True)
    dict_str = pprint.pformat(dct, width=120, sort_dicts=True)
    diff = list(
        difflib.unified_diff(
            dump_str.splitlines(),
            dict_str.splitlines(),
            fromfile="model_dump()",
            tofile="__dict__",
            lineterm="",
        )
    )
    return diff


# Utility: Remove all volatile fields from a dict using NodeMetadataField.volatile()
def strip_volatile_fields_from_dict(d: dict) -> dict:
    from omnibase.enums.metadata import NodeMetadataField

    volatile_keys = {f.value for f in NodeMetadataField.volatile()}
    return {k: v for k, v in d.items() if k not in volatile_keys}


# --- EntrypointBlock YAML representer registration ---
def _entrypointblock_yaml_representer(dumper, data):
    # Always serialize EntrypointBlock as a URI string
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.to_uri())


yaml.add_representer(EntrypointBlock, _entrypointblock_yaml_representer)
# NOTE: This ensures any EntrypointBlock dumped via PyYAML is a URI string, not a mapping.

# --- Fix Pydantic forward reference for ExtractedBlockModel ---
from omnibase.model.model_extracted_block import ExtractedBlockModel

ExtractedBlockModel.model_rebuild()
