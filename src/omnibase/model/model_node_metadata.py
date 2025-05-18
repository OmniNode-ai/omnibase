import enum
import logging
from typing import Annotated, Any, Callable, Dict, Iterator, List, Optional

from pydantic import BaseModel, Field, StringConstraints

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
    def __get_validators__(cls) -> Iterator[Callable]:
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


class NodeMetadataBlock(BaseModel):
    """
    Canonical ONEX node metadata block (see onex_node.yaml and node_contracts.md).
    All field names, types, and constraints must match the canonical schema.
    """

    metadata_version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ]
    protocol_version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ]
    owner: Annotated[str, StringConstraints(min_length=1)]
    copyright: Annotated[str, StringConstraints(min_length=1)]
    schema_version: Annotated[
        str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")
    ]
    name: Annotated[str, StringConstraints(min_length=1)]
    version: Annotated[str, StringConstraints(min_length=1, pattern=r"^\d+\.\d+\.\d+$")]
    uuid: Annotated[
        str,
        StringConstraints(
            min_length=1,
            pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        ),
    ]
    author: Annotated[str, StringConstraints(min_length=1)]
    created_at: Annotated[str, StringConstraints(min_length=1)]
    last_modified_at: Annotated[str, StringConstraints(min_length=1)]
    description: Annotated[str, StringConstraints(min_length=1)]
    state_contract: Annotated[str, StringConstraints(min_length=1)]
    lifecycle: Lifecycle
    hash: Annotated[str, StringConstraints(min_length=1, pattern=r"^[a-fA-F0-9]{64}$")]
    entrypoint: EntrypointBlock
    runtime_language_hint: Optional[str] = None
    namespace: Annotated[
        str,
        StringConstraints(min_length=1, pattern=r"^(omninode|onex)\.[a-zA-Z0-9_\.]+$"),
    ]
    meta_type: MetaType
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
    x_extensions: Optional[dict] = None
    testing: Optional[TestingBlock] = None
    os_requirements: Optional[list[str]] = None
    architectures: Optional[list[str]] = None
    container_image_reference: Optional[str] = None
    compliance_profiles: List[str] = Field(default_factory=list)
    data_handling_declaration: Optional[DataHandlingDeclaration] = None
    logging_config: Optional[LoggingConfig] = None
    source_repository: Optional[SourceRepository] = None
