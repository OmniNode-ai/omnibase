# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 9d243489-062b-4566-a68f-b68eebf56f2c
# name: model_node_metadata.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:57.193430
# last_modified_at: 2025-05-19T16:19:57.193436
# description: Stamped Python file: model_node_metadata.py
# state_contract: none
# lifecycle: active
# hash: b6e56bda7adfda613b3dfb5ac265b3b2a073b62052e55b554926d85047974f72
# entrypoint: {'type': 'python', 'target': 'model_node_metadata.py'}
# namespace: onex.stamped.model_node_metadata.py
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
import logging
from typing import Annotated, Any, Callable, ClassVar, Dict, Iterator, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from omnibase.canonical.canonical_serialization import CanonicalYAMLSerializer
from omnibase.canonical.hash_computation_mixin import HashComputationMixin
from omnibase.canonical.yaml_serialization_mixin import YAMLSerializationMixin

logger = logging.getLogger(__name__)


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


class EntrypointBlock(BaseModel):
    type: EntrypointType = Field(..., description="Entrypoint execution type")
    target: Annotated[str, StringConstraints(min_length=1)] = Field(
        ..., description="Execution target (file, script, or image)"
    )


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
            print(f"[DEBUG] commit_hash value: {repr(value)}")
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
        Raises ValueError if no block is found or parsing fails.
        """
        import yaml

        from omnibase.canonical.canonical_serialization import (
            extract_metadata_block_and_body,
            strip_block_delimiters_and_assert,
        )
        from omnibase.metadata.metadata_constants import YAML_META_CLOSE, YAML_META_OPEN

        logger = logging.getLogger("omnibase.model.model_node_metadata")
        if already_extracted_block is not None:
            block_yaml = already_extracted_block
        else:
            block_str, _ = extract_metadata_block_and_body(
                content, YAML_META_OPEN, YAML_META_CLOSE
            )
            if not block_str:
                logger.error("No metadata block found in content")
                raise ValueError("No metadata block found in content")
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
            logger.error(f"Failed to parse YAML block: {e}")
            raise ValueError(f"Failed to parse YAML block: {e}")
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
