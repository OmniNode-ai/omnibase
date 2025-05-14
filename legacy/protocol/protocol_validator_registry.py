from typing import Protocol, Optional, List, Type
from foundation.model.model_keyed import KeyedMetadataBlockModel

class ProtocolValidatorRegistry(Protocol):
    def register(self, name: str, validator_cls: type, meta: dict) -> None:
        """Register a validator with its metadata."""
        ...

    def get_validator(self, name: str, version: Optional[str] = None) -> Optional[type]:
        """Get a validator by name and optional version. If version is None, returns latest version."""
        ...

    def list_validators(self) -> List[str]:
        """List all registered validator names."""
        ...

    def get_all_metadata(self) -> KeyedMetadataBlockModel:
        """Get metadata for all validators."""
        ...

    def register_language_registry(self, language: str, registry: 'ProtocolValidatorRegistry') -> None:
        """Register a language-specific registry."""
        ...

    def get_language_registry(self, language: str) -> Optional['ProtocolValidatorRegistry']:
        """Get a language-specific registry."""
        ...

    def get_validator_versions(self, name: str) -> List[str]:
        """Get all versions available for a validator."""
        ...

    def get_latest_version(self, name: str) -> Optional[str]:
        """Get the latest version of a validator."""
        ...

    def check_version_compatibility(self, name: str, version: str) -> bool:
        """Check if a validator version is compatible with the current protocol version."""
        ... 