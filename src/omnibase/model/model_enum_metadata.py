# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_enum_metadata.py
# version: 1.0.0
# uuid: 9dc5d7dd-9701-4589-adf9-2fb575b41148
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165281
# last_modified_at: 2025-05-21T16:42:46.041472
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c8f8e61d49f813e095a2c39e3e84067a98b3597c845c7512236a31e0d12dd2b3
# entrypoint: python@model_enum_metadata.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_enum_metadata
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
