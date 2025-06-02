from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class PortUsageEntry(BaseModel):
    """
    Explicit mapping of a port to a node (by UUID), with lease and protocol info.
    """
    port: int = Field(..., description="Port number in use")
    node_id: UUID = Field(..., description="UUID of the node using this port")
    lease_id: str = Field(..., description="Lease ID associated with this port usage")
    protocol: str = Field(..., description="Protocol for the port (e.g., 'zmq', 'jetstream', 'ipc')")
    status: str = Field(..., description="Lease status: 'active', 'expired', etc.")
    expires_at: Optional[str] = Field(None, description="Lease expiration timestamp (ISO8601)")

class PortUsageMap(BaseModel):
    """
    Map of port number to PortUsageEntry for fast lookup and introspection.
    """
    ports: Dict[int, PortUsageEntry] = Field(default_factory=dict, description="Map of port number to usage entry") 