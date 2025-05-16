from enum import Enum


class MetaTypeEnum(str, Enum):
    TOOL = "tool"
    VALIDATOR = "validator"
    AGENT = "agent"
    MODEL = "model"
    PLUGIN = "plugin"
    SCHEMA = "schema"
    NODE = "node"
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

    @classmethod
    def required(cls):
        # Update this list if the model's required fields change
        return [
            cls.NODE_ID,
            cls.NODE_TYPE,
            cls.VERSION_HASH,
            cls.ENTRY_POINT,
            cls.CONTRACT_TYPE,
            cls.CONTRACT,
        ]

    @classmethod
    def optional(cls):
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
    UNKNOWN = "unknown"


# Add more as needed
