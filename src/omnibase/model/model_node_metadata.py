from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Literal, Any

class EntrypointBlock(BaseModel):
    type: Literal["python", "cli", "http"] = Field(..., description="Entrypoint execution type")
    path: str = Field(..., description="Module path, CLI command, or URL")

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

class NodeMetadataBlock(BaseModel):
    """
    Canonical metadata block for all ONEX nodes (v0.1).
    Supports plugin discovery, validator registration, tool scaffolding, and graph orchestration.
    """
    node_id: str = Field(..., description="Globally unique node identifier")
    node_type: Literal["plugin", "validator", "tool", "graph", "state"] = Field(..., description="Node specialization")
    version_hash: str = Field(..., description="Deterministic hash or version string for the node implementation")
    entry_point: EntrypointBlock = Field(..., description="Structured entrypoint reference")
    contract_type: Literal["io_schema", "signature", "custom"] = Field(..., description="Contract specification type")
    contract: Union[IOContract, SignatureContract, Dict[str, Any]] = Field(..., description="Declared interface contract")
    state_contract: Optional[StateContractBlock] = Field(None, description="Optional state transition contract")
    trust_score: Optional[float] = Field(None, description="Optional trust or reputation score")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    description: Optional[str] = Field(None, description="Human-readable description")
    sandbox_signature: Optional[str] = Field(None, description="Provenance signature or attestation")
    dependencies: List[str] = Field(default_factory=list, description="Runtime or build-time dependencies")
    capabilities: List[Literal["validate", "transform", "generate", "analyze", "extract", "route"]] = Field(
        default_factory=list, description="Declarative capability flags"
    )
    x_extensions: Dict[str, Any] = Field(default_factory=dict, description="Optional non-standard extension fields") 