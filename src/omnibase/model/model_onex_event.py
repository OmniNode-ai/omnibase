# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.677980'
# description: Stamped by PythonHandler
# entrypoint: python://model_onex_event
# hash: de98dbd4ad2b8aceb9d54f5f0911f0500bb06f4005203f57aa3d6dd44c0b62c8
# last_modified_at: '2025-05-29T14:13:58.847934+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onex_event.py
# namespace: python://omnibase.model.model_onex_event
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: fe3fe6eb-ac1a-4f91-a5d1-8fba44bbb898
# version: 1.0.0
# === /OmniNode:Metadata ===


from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from omnibase.enums.enum_node_status import NodeStatusEnum
from omnibase.enums.enum_registry_execution_mode import RegistryExecutionModeEnum
from omnibase.model.model_node_metadata import (
    IOBlock,
    NodeMetadataBlock,
    SignatureBlock,
)


class OnexEventTypeEnum(str, Enum):
    NODE_START = "NODE_START"
    NODE_SUCCESS = "NODE_SUCCESS"
    NODE_FAILURE = "NODE_FAILURE"
    NODE_REGISTER = "NODE_REGISTER"
    TELEMETRY_OPERATION_START = "TELEMETRY_OPERATION_START"
    TELEMETRY_OPERATION_SUCCESS = "TELEMETRY_OPERATION_SUCCESS"
    TELEMETRY_OPERATION_ERROR = "TELEMETRY_OPERATION_ERROR"
    STRUCTURED_LOG = "STRUCTURED_LOG"
    INTROSPECTION_REQUEST = "INTROSPECTION_REQUEST"
    INTROSPECTION_RESPONSE = "INTROSPECTION_RESPONSE"
    NODE_DISCOVERY_REQUEST = "NODE_DISCOVERY_REQUEST"
    NODE_DISCOVERY_RESPONSE = "NODE_DISCOVERY_RESPONSE"
    NODE_ANNOUNCE = "NODE_ANNOUNCE"  # Emitted by nodes on startup or registration
    NODE_ANNOUNCE_ACCEPTED = (
        "NODE_ANNOUNCE_ACCEPTED"  # Emitted by registry node on successful registration
    )
    NODE_ANNOUNCE_REJECTED = (
        "NODE_ANNOUNCE_REJECTED"  # Emitted by registry node if registration fails
    )
    TOOL_DISCOVERY_REQUEST = "TOOL_DISCOVERY_REQUEST"  # Protocol-pure tool discovery request
    TOOL_DISCOVERY_RESPONSE = "TOOL_DISCOVERY_RESPONSE"  # Protocol-pure tool discovery response
    # --- Proxy invocation event types ---
    TOOL_PROXY_INVOKE = "TOOL_PROXY_INVOKE"  # Request to invoke a tool via proxy
    TOOL_PROXY_ACCEPTED = "TOOL_PROXY_ACCEPTED"  # Proxy invocation accepted and routed
    TOOL_PROXY_REJECTED = "TOOL_PROXY_REJECTED"  # Proxy invocation rejected (invalid or unroutable)
    TOOL_PROXY_RESULT = "TOOL_PROXY_RESULT"  # Result of proxy tool invocation
    TOOL_PROXY_ERROR = "TOOL_PROXY_ERROR"  # Error during proxy tool invocation
    TOOL_PROXY_TIMEOUT = "TOOL_PROXY_TIMEOUT"  # Proxy invocation timed out
    # Add more event types as needed


class OnexEventMetadataModel(BaseModel):
    # Canonical fields for event metadata; extend for event-type-specific models
    input_state: Optional[dict] = None
    output_state: Optional[dict] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    recoverable: Optional[bool] = None
    node_version: Optional[str] = None
    operation_type: Optional[str] = None
    execution_time_ms: Optional[float] = None
    result_summary: Optional[str] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    registry_id: Optional[Union[str, UUID]] = None
    trust_state: Optional[str] = None
    ttl: Optional[int] = None
    # Add more fields as needed for protocol
    # For custom event types, subclass this model

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_node_announce(
        cls, announce: "NodeAnnounceMetadataModel"
    ) -> "OnexEventMetadataModel":
        """
        Construct an OnexEventMetadataModel from a NodeAnnounceMetadataModel, mapping all fields.
        """
        return cls(**announce.model_dump())


class OnexEvent(BaseModel):
    """
    Canonical event model for ONEX event emission and bus logic.
    Used by all event bus, node runner, and event store components.
    """

    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp (UTC)"
    )
    node_id: Union[str, UUID] = Field(
        ..., description="ID of the node emitting the event"
    )
    event_type: OnexEventTypeEnum = Field(..., description="Type of event emitted")
    correlation_id: Optional[str] = Field(
        default=None, description="Optional correlation ID for request tracking"
    )
    metadata: Optional[BaseModel] = Field(
        default=None,
        description="Optional event metadata or payload (must be a Pydantic model, never a dict)",
    )

    @model_validator(mode="after")
    def ensure_metadata_model(cls, values):
        meta = values.metadata
        if meta is not None:
            if isinstance(meta, dict):
                values.metadata = OnexEventMetadataModel(**meta)
            elif type(meta) is BaseModel:
                values.metadata = OnexEventMetadataModel(**meta.model_dump())
        return values


# Optionally, document the expected metadata structure for node_announce events:
# NODE_ANNOUNCE metadata fields:
#   node_id: str or UUID
#   metadata_block: dict (canonical node metadata)
#   status: str ("ephemeral" | "online" | "validated")
#   execution_mode: str ("memory" | "container" | "external")
#   inputs: dict (schema summary)
#   outputs: dict (schema summary)
#   graph_binding: Optional[str]
#   trust_state: Optional[str]
#   ttl: Optional[int]
# NODE_ANNOUNCE_ACCEPTED/REJECTED metadata fields:
#   node_id: str or UUID
#   status: str ("accepted" | "rejected")
#   reason: Optional[str] (for rejection)
#   registry_id: Optional[str or UUID]
#   trust_state: Optional[str]
#   ttl: Optional[int]


class TrustStateEnum(str, Enum):
    UNTRUSTED = "untrusted"
    TRUSTED = "trusted"
    VERIFIED = "verified"


class TelemetryOperationStartMetadataModel(OnexEventMetadataModel):
    """
    Metadata for TELEMETRY_OPERATION_START events.
    """

    operation: str
    function: str
    args_count: int
    kwargs_keys: list[str]


class TelemetryOperationSuccessMetadataModel(OnexEventMetadataModel):
    """
    Metadata for TELEMETRY_OPERATION_SUCCESS events.
    """

    operation: str
    function: str
    execution_time_ms: float
    result_type: str
    success: bool


class TelemetryOperationErrorMetadataModel(OnexEventMetadataModel):
    """
    Metadata for TELEMETRY_OPERATION_ERROR events.
    """

    operation: str
    function: str
    execution_time_ms: float
    error_type: str
    error_message: str
    success: bool


class NodeAnnounceMetadataModel(BaseModel):
    """
    Canonical metadata model for NODE_ANNOUNCE events.
    - node_id appears both at the event top-level and in metadata; they must match unless proxying is explicitly documented.
    - All fields use canonical models/enums; no raw strings for domain data.
    """

    node_id: str | UUID = Field(..., description="ID of the node being announced")
    metadata_block: NodeMetadataBlock = Field(
        ..., description="Canonical node metadata block"
    )
    status: NodeStatusEnum = Field(..., description="Node status (enum)")
    execution_mode: RegistryExecutionModeEnum = Field(
        ..., description="Execution mode (enum)"
    )
    inputs: list[IOBlock] = Field(..., description="Input schema summary (typed)")
    outputs: list[IOBlock] = Field(..., description="Output schema summary (typed)")
    graph_binding: Optional[str] = Field(
        None, description="Optional graph binding ID (e.g. 'graph://namespace/path@v1')"
    )
    trust_state: Optional[TrustStateEnum] = Field(
        None, description="Optional trust state enum"
    )
    ttl: Optional[int] = Field(None, description="Optional time-to-live in seconds")
    schema_version: str = Field(
        ..., description="Schema version for forward compatibility"
    )
    timestamp: datetime = Field(
        ..., description="UTC timestamp of event emission (ISO8601)"
    )
    signature_block: Optional[SignatureBlock] = Field(
        None, description="Optional digital signature block for integrity/trust"
    )
    node_version: Optional[str] = Field(
        None, description="Version of the node code or container"
    )
    correlation_id: Optional[UUID] = Field(
        None,
        description="Optional correlation/request ID for distributed tracing (UUID)",
    )

    @model_validator(mode="after")
    def enforce_signature_if_trusted(cls, values):
        trust_state = values.trust_state
        signature_block = values.signature_block
        if trust_state and not signature_block:
            raise ValueError("signature_block is required if trust_state is set")
        return values

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "node_id": "123e4567-e89b-12d3-a456-426614174000",
                "metadata_block": {
                    "name": "example_node",
                    "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    "inputs": [
                        {
                            "name": "input_1",
                            "schema_ref": "string",
                            "required": True,
                            "description": "Example input",
                        }
                    ],
                    "outputs": [
                        {
                            "name": "output_1",
                            "schema_ref": "string",
                            "required": True,
                            "description": "Example output",
                        }
                    ],
                    "metadata_version": "1.1.0",
                    "schema_version": "1.1.0",
                    "author": "OmniNode Team",
                    "created_at": "2025-06-01T12:00:00Z",
                    "entrypoint": {"type": "python", "target": "main.py"},
                    "namespace": "python://example.example_node",
                    "meta_type": "TOOL",
                },
                "status": "online",
                "execution_mode": "memory",
                "inputs": [
                    {
                        "name": "input_1",
                        "schema_ref": "string",
                        "required": True,
                        "description": "Example input",
                    }
                ],
                "outputs": [
                    {
                        "name": "output_1",
                        "schema_ref": "string",
                        "required": True,
                        "description": "Example output",
                    }
                ],
                "graph_binding": None,
                "trust_state": None,
                "ttl": None,
                "schema_version": "1.1.0",
                "timestamp": "2025-06-01T12:00:00Z",
                "signature_block": None,
                "node_version": "1.0.3",
                "correlation_id": "b7e6c2e2-8c2a-4e2a-9b2e-1c2a3e4b5c6d",
            }
        }
    )


OnexEvent.model_rebuild()
OnexEventMetadataModel.model_rebuild()
