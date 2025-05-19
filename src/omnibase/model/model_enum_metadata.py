# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 93ead147-720d-4685-a91f-a509195b5a0b
# name: model_enum_metadata.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:00.794744
# last_modified_at: 2025-05-19T16:20:00.794751
# description: Stamped Python file: model_enum_metadata.py
# state_contract: none
# lifecycle: active
# hash: 4f01cc75a60635fd6b5461d69ce98a6b98044c4fcd70cd2d9b5cb8799864c22f
# entrypoint: {'type': 'python', 'target': 'model_enum_metadata.py'}
# namespace: onex.stamped.model_enum_metadata.py
# meta_type: tool
# === /OmniNode:Metadata ===

from enum import Enum


class MetaTypeEnum(str, Enum):
    TOOL = "tool"
    VALIDATOR = "validator"
    AGENT = "agent"
    MODEL = "model"
    PLUGIN = "plugin"
    SCHEMA = "schema"
    NODE = "node"
    IGNORE_CONFIG = "ignore_config"
    UNKNOWN = "unknown"


class ProtocolVersionEnum(str, Enum):
    V0_1_0 = "0.1.0"
    V1_0_0 = "1.0.0"
    # Add more as needed


class RuntimeLanguageEnum(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    UNKNOWN = "unknown"


class NodeMetadataField(Enum):
    """
    Canonical Enum for all NodeMetadataBlock field names.
    Used for type-safe field references in tests, plugins, and codegen.
    This Enum must be kept in sync with the NodeMetadataBlock model.
    """

    NODE_ID = "node_id"
    NODE_TYPE = "node_type"
    VERSION_HASH = "version_hash"
    ENTRY_POINT = "entry_point"
    CONTRACT_TYPE = "contract_type"
    CONTRACT = "contract"
    STATE_CONTRACT = "state_contract"
    TRUST_SCORE = "trust_score"
    TAGS = "tags"
    DESCRIPTION = "description"
    SANDBOX_SIGNATURE = "sandbox_signature"
    DEPENDENCIES = "dependencies"
    CAPABILITIES = "capabilities"
    X_EXTENSIONS = "x_extensions"
    HASH = "hash"
    LAST_MODIFIED_AT = "last_modified_at"

    @classmethod
    def required(cls) -> list["NodeMetadataField"]:
        # Update this list if the model's required fields change
        return [
            cls.NODE_ID,
            cls.NODE_TYPE,
            cls.VERSION_HASH,
            cls.ENTRY_POINT,
            cls.CONTRACT_TYPE,
            cls.CONTRACT,
            cls.HASH,
            cls.LAST_MODIFIED_AT,
        ]

    @classmethod
    def optional(cls) -> list["NodeMetadataField"]:
        # All other fields are optional
        return [
            cls.STATE_CONTRACT,
            cls.TRUST_SCORE,
            cls.TAGS,
            cls.DESCRIPTION,
            cls.SANDBOX_SIGNATURE,
            cls.DEPENDENCIES,
            cls.CAPABILITIES,
            cls.X_EXTENSIONS,
        ]


class UriTypeEnum(str, Enum):
    TOOL = "tool"
    VALIDATOR = "validator"
    AGENT = "agent"
    MODEL = "model"
    PLUGIN = "plugin"
    SCHEMA = "schema"
    NODE = "node"
    IGNORE_CONFIG = "ignore_config"
    UNKNOWN = "unknown"


SCHEMA_REF = "schema_ref"

# Add more as needed
