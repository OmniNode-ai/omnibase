from enum import Enum


# Canonical Enum for all node status values (ONEX Standard)
class NodeStatusEnum(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EPHEMERAL = "ephemeral"
    # Add more as protocol evolves
