# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: metadata.py
# version: 1.0.0
# uuid: 9dc5d7dd-9701-4589-adf9-2fb575b41148
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165281
# last_modified_at: 2025-05-26T18:58:45.719295
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 0684061f597d48cd9c1c2e2abd68c9f538a7fb641c3b64c4f43cdb8e88d74164
# entrypoint: python@metadata.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.metadata
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


class FunctionLanguageEnum(str, Enum):
    """Enum for supported function discovery languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    SHELL = "shell"
    YAML = "yaml"
    JSON = "json"


class NodeMetadataField(Enum):
    """
    Canonical Enum for all NodeMetadataBlock field names.
    Used for type-safe field references in tests, plugins, and codegen.
    This Enum must be kept in sync with the NodeMetadataBlock model.
    """

    # Core metadata fields
    METADATA_VERSION = "metadata_version"
    PROTOCOL_VERSION = "protocol_version"
    OWNER = "owner"
    COPYRIGHT = "copyright"
    SCHEMA_VERSION = "schema_version"
    NAME = "name"
    VERSION = "version"
    UUID = "uuid"
    AUTHOR = "author"
    CREATED_AT = "created_at"
    LAST_MODIFIED_AT = "last_modified_at"
    DESCRIPTION = "description"
    STATE_CONTRACT = "state_contract"
    LIFECYCLE = "lifecycle"
    HASH = "hash"
    ENTRYPOINT = "entrypoint"
    RUNTIME_LANGUAGE_HINT = "runtime_language_hint"
    NAMESPACE = "namespace"
    META_TYPE = "meta_type"

    # Optional fields
    TRUST_SCORE = "trust_score"
    TAGS = "tags"
    CAPABILITIES = "capabilities"
    PROTOCOLS_SUPPORTED = "protocols_supported"
    BASE_CLASS = "base_class"
    DEPENDENCIES = "dependencies"
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    ENVIRONMENT = "environment"
    LICENSE = "license"
    SIGNATURE_BLOCK = "signature_block"
    X_EXTENSIONS = "x_extensions"
    TESTING = "testing"
    OS_REQUIREMENTS = "os_requirements"
    ARCHITECTURES = "architectures"
    CONTAINER_IMAGE_REFERENCE = "container_image_reference"
    COMPLIANCE_PROFILES = "compliance_profiles"
    DATA_HANDLING_DECLARATION = "data_handling_declaration"
    LOGGING_CONFIG = "logging_config"
    SOURCE_REPOSITORY = "source_repository"

    @classmethod
    def required(cls) -> list["NodeMetadataField"]:
        """Return list of required fields based on NodeMetadataBlock model."""
        return [
            cls.NAME,
            cls.UUID,
            cls.AUTHOR,
            cls.CREATED_AT,
            cls.LAST_MODIFIED_AT,
            cls.HASH,
            cls.ENTRYPOINT,
            cls.NAMESPACE,
        ]

    @classmethod
    def optional(cls) -> list["NodeMetadataField"]:
        """Return list of optional fields with defaults."""
        return [
            cls.METADATA_VERSION,
            cls.PROTOCOL_VERSION,
            cls.OWNER,
            cls.COPYRIGHT,
            cls.SCHEMA_VERSION,
            cls.VERSION,
            cls.DESCRIPTION,
            cls.STATE_CONTRACT,
            cls.LIFECYCLE,
            cls.RUNTIME_LANGUAGE_HINT,
            cls.META_TYPE,
            cls.TRUST_SCORE,
            cls.TAGS,
            cls.CAPABILITIES,
            cls.PROTOCOLS_SUPPORTED,
            cls.BASE_CLASS,
            cls.DEPENDENCIES,
            cls.INPUTS,
            cls.OUTPUTS,
            cls.ENVIRONMENT,
            cls.LICENSE,
            cls.SIGNATURE_BLOCK,
            cls.X_EXTENSIONS,
            cls.TESTING,
            cls.OS_REQUIREMENTS,
            cls.ARCHITECTURES,
            cls.CONTAINER_IMAGE_REFERENCE,
            cls.COMPLIANCE_PROFILES,
            cls.DATA_HANDLING_DECLARATION,
            cls.LOGGING_CONFIG,
            cls.SOURCE_REPOSITORY,
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
