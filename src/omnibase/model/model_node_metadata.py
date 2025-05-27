# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_node_metadata.py
# version: 1.0.0
# uuid: 92bc3783-426c-4f0b-9b8e-5c54ee86ba95
# author: OmniNode Team
# created_at: 2025-05-22T14:05:21.445998
# last_modified_at: 2025-05-22T20:22:47.710441
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 653de640227a49b3a14307039b1817d27e321c622b2349762cb5d5e582ea898d
# entrypoint: python@model_node_metadata.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_node_metadata
# meta_type: tool
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
)

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.core.structured_logging import emit_log_event
from omnibase.enums import FunctionLanguageEnum, LogLevelEnum
from omnibase.mixin.mixin_canonical_serialization import CanonicalYAMLSerializer
from omnibase.mixin.mixin_hash_computation import HashComputationMixin
from omnibase.mixin.mixin_yaml_serialization import YAMLSerializationMixin

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class Lifecycle(enum.StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class MetaType(enum.StrEnum):
    TOOL = "tool"
    VALIDATOR = "validator"
    AGENT = "agent"
    MODEL = "model"
    SCHEMA = "schema"
    PLUGIN = "plugin"
    IGNORE_CONFIG = "ignore_config"


class EntrypointType(enum.StrEnum):
    PYTHON = "python"
    CLI = "cli"
    DOCKER = "docker"


class DataClassification(enum.StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class LogLevel(enum.StrEnum):
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"
    NONE = "none"


class LogFormat(enum.StrEnum):
    JSON = "json"
    TEXT = "text"
    KEY_VALUE = "key-value"


class Architecture(enum.StrEnum):
    AMD64 = "amd64"
    ARM64 = "arm64"
    PPC64LE = "ppc64le"


class FunctionTool(BaseModel):
    """
    Language-agnostic function tool metadata for the unified tools approach.
    Functions are treated as tools within the main metadata block.
    """

    type: str = Field(default="function", description="Tool type (always 'function')")
    language: FunctionLanguageEnum = Field(
        ...,
        description="Programming language (python, javascript, typescript, bash, yaml, etc.)",
    )
    line: int = Field(..., description="Line number where function is defined")
    description: Annotated[str, StringConstraints(min_length=1)] = Field(
        ..., description="Function description"
    )
    inputs: List[str] = Field(
        default_factory=list, description="Function input parameters with types"
    )
    outputs: List[str] = Field(
        default_factory=list, description="Function output types"
    )
    error_codes: List[str] = Field(
        default_factory=list, description="Error codes this function may raise"
    )
    side_effects: List[str] = Field(
        default_factory=list, description="Side effects this function may have"
    )

    def to_serializable_dict(self) -> dict[str, Any]:
        """Convert to serializable dictionary for metadata block."""
        return {k: getattr(self, k) for k in self.__class__.model_fields}

    @classmethod
    def from_serializable_dict(
        cls: Type["FunctionTool"], data: dict[str, Any]
    ) -> "FunctionTool":
        """Create from serializable dictionary."""
        return cls(**data)


class EntrypointBlock(BaseModel):
    type: EntrypointType = Field(..., description="Entrypoint execution type")
    target: Annotated[str, StringConstraints(min_length=1)] = Field(
        ..., description="Execution target (file, script, or image)"
    )

    def to_serializable_dict(self) -> dict[str, Any]:
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

        return {
            k: serialize_value(getattr(self, k)) for k in self.__class__.model_fields
        }

    @classmethod
    def from_serializable_dict(
        cls: Type["EntrypointBlock"], data: dict[str, Any]
    ) -> "EntrypointBlock":
        return cls(**data)


class IOContract(BaseModel):
    inputs: Dict[str, str]
    outputs: Dict[str, str]


class SignatureContract(BaseModel):
    function_name: str
    parameters: Dict[str, str]
    return_type: str
    raises: List[str] = []


class StateContractBlock(BaseModel):
    preconditions: Dict[str, str]
    postconditions: Dict[str, str]
    transitions: Optional[Dict[str, str]] = None


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


class IOBlock(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    schema_ref: Annotated[str, StringConstraints(min_length=1)]
    required: Optional[bool] = True
    format_hint: Optional[str] = None
    description: Optional[Annotated[str, StringConstraints(min_length=1)]] = None


class DataHandlingDeclaration(BaseModel):
    processes_sensitive_data: bool
    data_residency_required: Optional[str] = None
    data_classification: Optional[DataClassification] = None


class LoggingConfig(BaseModel):
    level: Optional[LogLevel] = None
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
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"commit_hash value: {repr(value)}",
                node_id=_COMPONENT_NAME,
            )
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


class NodeMetadataBlock(YAMLSerializationMixin, HashComputationMixin, BaseModel):
    """
    Canonical ONEX node metadata block (see onex_node.yaml and node_contracts.md).
    All field names, types, and constraints must match the canonical schema.

    NOTE: `metadata_version` is the single version for both schema and canonicalization logic.
    Any change to the schema OR to canonicalization (e.g., normalization, hash computation) MUST increment `metadata_version`.
    This ensures idempotency and hash comparability across versions.

    Context-dependent fields (must be provided by handler):
      - author
      - entrypoint
      - namespace
      - name
      - uuid
      - created_at
      - last_modified_at
      - hash
    All other fields have sensible defaults below.
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
    runtime_language_hint: Optional[str] = Field(default="python>=3.11")
    namespace: Annotated[
        str,
        StringConstraints(min_length=1, pattern=r"^(omninode|onex)\.[a-zA-Z0-9_\.]+$"),
    ]
    meta_type: MetaType = Field(default=MetaType.TOOL)
    trust_score: Optional[float] = None
    tags: Optional[list[str]] = None
    capabilities: Optional[list[str]] = None
    protocols_supported: Optional[list[str]] = None
    base_class: Optional[list[str]] = None
    dependencies: Optional[list[Any]] = None
    inputs: Optional[list[IOBlock]] = None
    outputs: Optional[list[IOBlock]] = None
    environment: Optional[list[str]] = None
    license: Optional[str] = None
    signature_block: Optional[SignatureBlock] = None
    x_extensions: Dict[str, Any] = Field(default_factory=dict)
    testing: Optional[TestingBlock] = None
    os_requirements: Optional[list[str]] = None
    architectures: Optional[list[str]] = None
    container_image_reference: Optional[str] = None
    compliance_profiles: List[str] = Field(default_factory=list)
    data_handling_declaration: Optional[DataHandlingDeclaration] = None
    logging_config: Optional[LoggingConfig] = None
    source_repository: Optional[SourceRepository] = None

    # Function tools support - unified tools approach
    tools: Optional[Dict[str, FunctionTool]] = Field(
        default=None,
        description="Function tools within this file (unified tools approach)",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Canonicalization/canonicalizer policy (not Pydantic config)
    canonicalization_policy: ClassVar[dict[str, Any]] = {
        "canonicalize_body": staticmethod(
            lambda body: CanonicalYAMLSerializer().normalize_body(body)
        )
    }

    @classmethod
    def from_file_or_content(
        cls, content: str, already_extracted_block: Optional[str] = None
    ) -> "NodeMetadataBlock":
        """
        Extract the metadata block from file content and parse as NodeMetadataBlock.
        If 'already_extracted_block' is provided, parse it directly (assumed to be YAML, delimiters/comments stripped).
        Otherwise, extract from content using canonical utility.
        Raises OnexError if no block is found or parsing fails.
        """
        import yaml

        from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN
        from omnibase.mixin.mixin_canonical_serialization import (
            extract_metadata_block_and_body,
            strip_block_delimiters_and_assert,
        )

        if already_extracted_block is not None:
            block_yaml = already_extracted_block
        else:
            block_str, _ = extract_metadata_block_and_body(
                content, YAML_META_OPEN, YAML_META_CLOSE
            )
            if not block_str:
                emit_log_event(
                    LogLevelEnum.ERROR,
                    "No metadata block found in content",
                    node_id=_COMPONENT_NAME,
                )
                raise OnexError(
                    "No metadata block found in content",
                    CoreErrorCode.VALIDATION_FAILED,
                )
            # Strip comment prefixes from all lines (if present)
            block_lines = []
            for line in block_str.splitlines():
                if line.lstrip().startswith("# "):
                    prefix_index = line.find("# ")
                    block_lines.append(line[:prefix_index] + line[prefix_index + 2 :])
                else:
                    block_lines.append(line)
            # Remove delimiter lines
            delimiters = {
                YAML_META_OPEN.replace("# ", ""),
                YAML_META_CLOSE.replace("# ", ""),
            }
            block_yaml = strip_block_delimiters_and_assert(
                block_lines,
                delimiters,
                context="NodeMetadataBlock.from_file_or_content",
            )
        try:
            data = yaml.safe_load(block_yaml)
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to parse YAML block: {e}",
                node_id=_COMPONENT_NAME,
            )
            raise OnexError(
                f"Failed to parse YAML block: {e}",
                CoreErrorCode.CONFIGURATION_PARSE_ERROR,
            )
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

        result = {
            k: serialize_value(getattr(self, k)) for k in self.__class__.model_fields
        }

        # Use compact entrypoint format: "python@filename.py"
        if use_compact_entrypoint and "entrypoint" in result:
            entrypoint = getattr(self, "entrypoint")
            if entrypoint:
                result["entrypoint"] = f"{entrypoint.type.value}@{entrypoint.target}"

        return result

    @classmethod
    def from_serializable_dict(
        cls: Type["NodeMetadataBlock"], data: dict[str, Any]
    ) -> "NodeMetadataBlock":
        # Handle entrypoint deserialization
        if "entrypoint" in data and isinstance(data["entrypoint"], dict):
            data["entrypoint"] = EntrypointBlock.from_serializable_dict(
                data["entrypoint"]
            )

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
            data["tools"] = tools_dict

        return cls(**data)

    @classmethod
    def create_with_defaults(
        cls,
        name: Optional[str] = None,
        author: Optional[str] = None,
        namespace: Optional[str] = None,
        entrypoint_type: Optional[str] = None,
        entrypoint_target: Optional[str] = None,
        **additional_fields: Any,
    ) -> "NodeMetadataBlock":
        """
        Create a complete NodeMetadataBlock with sensible defaults for all required fields.
        This is the canonical way to construct metadata blocks, ensuring all required fields are present.
        """
        from datetime import datetime
        from uuid import uuid4

        now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # Build complete data with all required fields
        data: Dict[str, Any] = {
            "name": name or "unknown",
            "uuid": str(uuid4()),
            "author": author or "unknown",
            "created_at": now,
            "last_modified_at": now,
            "hash": "0" * 64,  # Will be computed later
            "entrypoint": EntrypointBlock(
                type=EntrypointType(entrypoint_type or "python"),
                target=entrypoint_target or "main.py",
            ),
            "namespace": namespace or "onex.stamped.unknown",
        }

        # Add any additional fields provided
        data.update(additional_fields)

        return cls(**data)  # type: ignore[arg-type]
