from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, constr


class EntrypointBlock(BaseModel):
    type: Literal["python", "cli", "docker"] = Field(
        ..., description="Entrypoint execution type"
    )
    target: str = Field(..., description="Execution target (file, script, or image)")


class IOContract(BaseModel):
    inputs: Dict[str, str]
    outputs: Dict[str, str]


class SignatureContract(BaseModel):
    function_name: str
    parameters: Dict[str, str]
    return_type: str
    raises: Optional[List[str]] = Field(default_factory=list)


class StateContractBlock(BaseModel):
    preconditions: Dict[str, str]
    postconditions: Dict[str, str]
    transitions: Optional[Dict[str, str]] = None


class TrustScoreStub(BaseModel):
    runs: int = Field(..., description="Number of runs")
    failures: int = Field(..., description="Number of failures")
    trust_score: Optional[float] = Field(None, description="Trust score (optional)")


class SignatureBlock(BaseModel):
    signature: Optional[str] = Field(
        None, description="Cryptographic signature (optional)"
    )
    algorithm: Optional[str] = Field(
        None, description="Signature algorithm (e.g., RSA, ECDSA)"
    )
    signed_by: Optional[str] = Field(
        None, description="Signer identity or key reference"
    )
    issued_at: Optional[str] = Field(
        None, description="Signature issuance timestamp (ISO 8601)"
    )


class NodeMetadataBlock(BaseModel):
    """
    Canonical ONEX node metadata block (see onex_node.yaml and node_contracts.md).
    All field names, types, and constraints must match the canonical schema.
    """

    schema_version: constr(pattern=r"^\d+\.\d+\.\d+$")
    name: str
    version: constr(pattern=r"^\d+\.\d+\.\d+$")
    uuid: constr(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    )
    author: str
    created_at: str  # ISO 8601
    last_modified_at: str  # ISO 8601
    description: str
    state_contract: str  # Canonical URI, pattern enforced in schema
    lifecycle: Literal["draft", "active", "deprecated", "archived"]
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    entrypoint: EntrypointBlock
    namespace: constr(pattern=r"^(omninode|onex)\.[a-zA-Z0-9_\.]+$")
    meta_type: Literal["tool", "validator", "agent", "model", "schema", "plugin"]
    runtime_language_hint: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    trust_score_stub: Optional[TrustScoreStub] = None
    x_extensions: Dict[str, Any] = Field(default_factory=dict)
    protocols_supported: List[str] = Field(default_factory=list)
    base_class: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    environment: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    signature_block: Optional[SignatureBlock] = None
